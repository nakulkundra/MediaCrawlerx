# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/xhs/client.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# Statement: This code is for learning and research purposes only. Users should abide by the following principles:
# 1. Shall not be used for any commercial purposes.
# 2. When using, please abide by the terms of use and robots.txt rules of the target platform.
# 3. Do not conduct large-scale crawling or disrupt platform operations.
# 4. Request frequency should be reasonably controlled to avoid placing unnecessary burden on the target platform.
# 5. Must not be used for any illegal or improper purposes.
#
# For detailed license terms, please refer to the LICENSE file in the project root directory.
# Using this code indicates that you agree to abide by the above principles and all terms in the LICENSE.

import asyncio
import json
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union
from urllib.parse import quote, urlencode

import httpx
from playwright.async_api import BrowserContext, Page
from tenacity import (
    RetryError,
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed,
)
from tools.httpx_util import make_async_client

import config
from base.base_crawler import AbstractApiClient
from proxy.proxy_mixin import ProxyRefreshMixin
from tools import utils

if TYPE_CHECKING:
    from proxy.proxy_ip_pool import ProxyIpPool

from .exception import (
    DataFetchError,
    IPBlockError,
    NoteNotFoundError,
    PlatformAccessError,
)
from .extractor import XiaoHongShuExtractor
from .field import SearchNoteType, SearchSortType
from .help import get_search_id
from .playwright_sign import sign_with_xhshow


class XiaoHongShuClient(AbstractApiClient, ProxyRefreshMixin):

    def __init__(
        self,
        timeout=60,  # If media crawling is enabled, Xiaohongshu long videos need longer timeout
        proxy=None,
        *,
        headers: Dict[str, str],
        playwright_page: Page,
        cookie_dict: Dict[str, str],
        proxy_ip_pool: Optional["ProxyIpPool"] = None,
    ):
        self.proxy = proxy
        self.timeout = timeout
        self.headers = headers
        if config.XHS_INTERNATIONAL:
            self._host = "https://webapi.rednote.com"
            self._domain = "https://www.rednote.com"
        else:
            self._host = "https://edith.xiaohongshu.com"
            self._domain = "https://www.xiaohongshu.com"
        self.cookie_urls = [self._domain]
        self.IP_ERROR_STR = "Network connection error, please check network settings or restart"
        self.IP_ERROR_CODE = 300012
        self.SECURITY_LIMIT_CODE = 300011
        self.NOTE_NOT_FOUND_CODE = -510000
        self.NOTE_ABNORMAL_STR = "Note status abnormal, please check later"
        self.NOTE_ABNORMAL_CODE = -510001
        self.playwright_page = playwright_page
        self.cookie_dict = cookie_dict
        self._extractor = XiaoHongShuExtractor()
        # Initialize proxy pool (from ProxyRefreshMixin)
        self.init_proxy_pool(proxy_ip_pool)

    async def _pre_headers(self, url: str, params: Optional[Dict] = None, payload: Optional[Dict] = None) -> Dict:
        """
        Request header parameter signature (using xhshow pure algorithm)

        Args:
            url: Request URI path
            params: GET request parameters
            payload: POST request parameters

        Returns:
            Dict: Signed request headers
        """
        if params is not None:
            data = params
        elif payload is not None:
            data = payload
        else:
            raise ValueError("params or payload is required")

        # Generate signatures using xhshow pure algorithm
        signs = sign_with_xhshow(
            uri=url,
            data=data,
            a1=self.cookie_dict.get("a1", ""),
            web_session=self.cookie_dict.get("web_session", ""),
        )

        headers = {
            "X-S": signs["x-s"],
            "X-T": signs["x-t"],
            "x-S-Common": signs["x-s-common"],
            "X-B3-Traceid": signs["x-b3-traceid"],
        }
        self.headers.update(headers)
        return self.headers

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_not_exception_type(
            (NoteNotFoundError, IPBlockError, PlatformAccessError)
        ),
    )
    async def request(self, method, url, **kwargs) -> Union[str, Any]:
        """
        Wrapper for httpx common request method, processes request response
        Args:
            method: Request method
            url: Request URL
            **kwargs: Other request parameters, such as headers, body, etc.

        Returns:

        """
        # Check if proxy is expired before each request
        await self._refresh_proxy_if_expired()

        return_response = kwargs.pop("return_response", False)
        async with make_async_client(proxy=self.proxy) as client:
            response = await client.request(method, url, timeout=self.timeout, **kwargs)

        if response.status_code in {401, 403, 429}:
            raise PlatformAccessError(
                f"XHS request blocked with HTTP {response.status_code}"
            )

        if response.status_code == 471 or response.status_code == 461:
            # Captcha required
            verify_type = response.headers.get("Verifytype", "")
            verify_uuid = response.headers.get("Verifyuuid", "")
            msg = f"CAPTCHA appeared, request failed, Verifytype: {verify_type}, Verifyuuid: {verify_uuid}, Response: {response}"
            utils.logger.error(msg)
            raise Exception(msg)

        response_data: Optional[Dict] = None
        try:
            candidate_data = response.json()
            if isinstance(candidate_data, dict):
                response_data = candidate_data
        except (TypeError, ValueError):
            pass

        response_code = (
            str(response_data.get("code"))
            if response_data is not None and response_data.get("code") is not None
            else ""
        )
        if response_code == str(self.IP_ERROR_CODE):
            raise IPBlockError(self.IP_ERROR_STR)
        if response_code == str(self.SECURITY_LIMIT_CODE):
            raise PlatformAccessError(
                f"XHS account security restriction, code: {self.SECURITY_LIMIT_CODE}"
            )

        if return_response:
            return response.text
        data: Dict = response_data if response_data is not None else response.json()
        if data.get("success"):
            return data.get("data", data.get("success", {}))
        elif data.get("code") in (self.NOTE_NOT_FOUND_CODE, self.NOTE_ABNORMAL_CODE):
            raise NoteNotFoundError(f"Note not found or abnormal, code: {data['code']}")
        else:
            err_msg = data.get("msg", None) or f"{response.text}"
            raise DataFetchError(err_msg)

    @staticmethod
    def _build_query_string(params: Dict) -> str:
        """Build URL query string with encoding matching browser behavior (commas not encoded)"""
        parts = []
        for key, value in params.items():
            value_str = str(value) if value is not None else ""
            parts.append(f"{key}={quote(value_str, safe=',')}")
        return "&".join(parts)

    async def get(self, uri: str, params: Optional[Dict] = None) -> Dict:
        """
        GET request with header signing
        Args:
            uri: Request route
            params: Request parameters

        Returns:

        """
        final_uri = uri
        if isinstance(params, dict):
            final_uri = f"{uri}?{self._build_query_string(params)}"
        headers = await self._pre_headers(url=final_uri, params=params)
        return await self.request(
            method="GET", url=f"{self._host}{final_uri}", headers=headers
        )

    async def post(self, uri: str, data: dict) -> Dict:
        """
        POST request with header signing
        Args:
            uri: Request route
            data: Request body parameters

        Returns:

        """
        headers = await self._pre_headers(url=uri, payload=data)
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return await self.request(
            method="POST",
            url=f"{self._host}{uri}",
            data=json_str,
            headers=headers,
        )

    async def pong(self) -> bool:
        """
        Check if login state is valid
        Returns:

        """
        utils.logger.info("[XiaoHongShuClient.pong] Begin pong xiaohongshu ...")
        ping_flag = False
        try:
            feed_data = await self.get_user_info()
            if feed_data:
                ping_flag = True
        except Exception as e:
            utils.logger.error(f"[XiaoHongShuClient.pong] Pong xiaohongshu failed: {e}")
            ping_flag = False
        return ping_flag

    async def update_cookies(
        self,
        browser_context: BrowserContext,
        urls: Optional[List[str]] = None,
    ):
        """
        Update cookies from browser context
        Args:
            browser_context: Browser context
            urls: Target URLs

        Returns:

        """
        cookie_urls = urls or self.cookie_urls
        cookie_str, cookie_dict = await utils.convert_browser_context_cookies(
            browser_context,
            urls=cookie_urls,
        )
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict
        utils.logger.info(
            f"[XiaoHongShuClient.update_cookies] Cookie updated successfully for {cookie_urls}"
        )

    async def get_user_info(self) -> Dict:
        """
        Get current user info
        Returns:

        """
        uri = "/api/sns/web/v1/user/selfinfo"
        return await self.get(uri)

    async def get_note_by_keyword(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        sort: SearchSortType = SearchSortType.GENERAL,
        note_type: SearchNoteType = SearchNoteType.ALL,
        search_id: str = "",
    ) -> Dict:
        """
        Search notes by keyword
        Args:
            keyword: Search keyword
            page: Page number
            page_size: Page size
            sort: Sort method
            note_type: Note type
            search_id: Search ID

        Returns:

        """
        uri = "/api/sns/web/v1/search/notes"
        data = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "search_id": search_id or get_search_id(),
            "sort": sort.value,
            "note_type": note_type.value,
        }
        return await self.post(uri, data)

    async def get_note_by_id(self, note_id: str, xsec_token: str = "") -> Dict:
        """
        Get note detail by note ID
        Args:
            note_id: Note ID
            xsec_token: Security token

        Returns:

        """
        data = {
            "source_note_id": note_id,
            "image_formats": ["jpg", "webp", "avif"],
            "extra": {"need_body_topic": "1"},
            "xsec_source": "pc_search",
            "xsec_token": xsec_token,
        }
        uri = "/api/sns/web/v1/feed"
        return await self.post(uri, data)

    async def get_note_by_id_from_html(self, note_id: str, xsec_token: str = "") -> Optional[Dict]:
        """
        Get note detail by scraping HTML page directly
        Args:
            note_id: Note ID
            xsec_token: Security token

        Returns:

        """
        url = f"{self._domain}/explore/{note_id}?xsec_token={xsec_token}&xsec_source=pc_search"
        if not self.playwright_page:
            return None
        await self.playwright_page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(1)
        html_content = await self.playwright_page.content()
        return self._extractor.extract_note_detail_from_html(note_id, html_content)

    async def get_note_comments(
        self,
        note_id: str,
        cursor: str = "",
        xsec_token: str = "",
    ) -> Dict:
        """
        Get first-level comments for a note
        Args:
            note_id: Note ID
            cursor: Pagination cursor
            xsec_token: Security token

        Returns:

        """
        uri = "/api/sns/web/v2/comment/page"
        params = {
            "note_id": note_id,
            "cursor": cursor,
            "top_comment_id": "",
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
        }
        return await self.get(uri, params)

    async def get_note_sub_comments(
        self,
        note_id: str,
        root_comment_id: str,
        num: int = 30,
        cursor: str = "",
    ) -> Dict:
        """
        Get sub-comments for a root comment
        Args:
            note_id: Note ID
            root_comment_id: Root comment ID
            num: Number of sub-comments
            cursor: Pagination cursor

        Returns:

        """
        uri = "/api/sns/web/v2/comment/sub/page"
        params = {
            "note_id": note_id,
            "root_comment_id": root_comment_id,
            "num": num,
            "cursor": cursor,
            "image_formats": "jpg,webp,avif",
        }
        return await self.get(uri, params)

    async def get_note_all_comments(
        self,
        note_id: str,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
        max_count: int = 10,
        xsec_token: str = "",
    ) -> List[Dict]:
        """
        Get all comments including sub-comments for a note
        Args:
            note_id: Note ID
            crawl_interval: Delay between requests in seconds
            callback: Callback function for comments
            max_count: Maximum comments to retrieve
            xsec_token: Security token

        Returns:

        """
        result = []
        cursor = ""
        has_more = True
        while has_more and len(result) < max_count:
            comments_res = await self.get_note_comments(
                note_id=note_id, cursor=cursor, xsec_token=xsec_token
            )
            has_more = comments_res.get("has_more", False)
            cursor = comments_res.get("cursor", "")
            comments: List[Dict] = comments_res.get("comments", [])
            if not comments:
                break
            if len(result) + len(comments) > max_count:
                comments = comments[: max_count - len(result)]
            if callback:
                await callback(note_id, comments)
            result.extend(comments)
            await asyncio.sleep(crawl_interval)

            if config.ENABLE_GET_SUB_COMMENTS:
                for comment in comments:
                    sub_comments = await self.get_all_sub_comments_for_comment(
                        note_id=note_id,
                        root_comment=comment,
                        crawl_interval=crawl_interval,
                        callback=callback,
                    )
                    result.extend(sub_comments)
        return result

    async def get_all_sub_comments_for_comment(
        self,
        note_id: str,
        root_comment: Dict,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
    ) -> List[Dict]:
        """
        Get all sub-comments for a specific root comment
        Args:
            note_id: Note ID
            root_comment: Root comment dictionary
            crawl_interval: Delay between requests
            callback: Callback function

        Returns:

        """
        sub_comment_count = int(root_comment.get("sub_comment_count", 0))
        if sub_comment_count == 0:
            return []
        root_comment_id = root_comment.get("id", "")
        cursor = ""
        has_more = True
        sub_comments_result = []
        while has_more:
            res = await self.get_note_sub_comments(
                note_id=note_id,
                root_comment_id=root_comment_id,
                cursor=cursor,
            )
            has_more = res.get("has_more", False)
            cursor = res.get("cursor", "")
            sub_comments = res.get("comments", [])
            if callback and sub_comments:
                await callback(note_id, sub_comments)
            sub_comments_result.extend(sub_comments)
            await asyncio.sleep(crawl_interval)
        return sub_comments_result

    async def get_creator_info(self, user_id: str) -> Dict:
        """
        Get creator profile information
        Args:
            user_id: User ID

        Returns:

        """
        uri = "/api/sns/web/v1/user/otherinfo"
        params = {"target_user_id": user_id}
        return await self.get(uri, params)

    async def get_notes_by_creator(self, creator: str, cursor: str = "") -> Dict:
        """
        Get creator published notes
        Args:
            creator: User ID
            cursor: Pagination cursor

        Returns:

        """
        uri = "/api/sns/web/v1/user_posted"
        params = {
            "num": "30",
            "cursor": cursor,
            "user_id": creator,
            "image_formats": "jpg,webp,avif",
        }
        return await self.get(uri, params)

    async def get_all_notes_by_creator(
        self,
        user_id: str,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
    ) -> List[Dict]:
        """
        Get all notes published by a creator
        Args:
            user_id: User ID
            crawl_interval: Delay between requests
            callback: Callback function

        Returns:

        """
        result = []
        cursor = ""
        has_more = True
        while has_more:
            notes_res = await self.get_notes_by_creator(creator=user_id, cursor=cursor)
            has_more = notes_res.get("has_more", False)
            cursor = notes_res.get("cursor", "")
            notes = notes_res.get("notes", [])
            if not notes:
                break
            if callback:
                await callback(notes)
            result.extend(notes)
            await asyncio.sleep(crawl_interval)
        return result
