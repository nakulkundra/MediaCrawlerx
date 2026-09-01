# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/zhihu/client.py
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

# -*- coding: utf-8 -*-
import asyncio
import json
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx
from httpx import Response
from playwright.async_api import BrowserContext, Page
from tenacity import retry, stop_after_attempt, wait_fixed
from tools.httpx_util import make_async_client

import config
from base.base_crawler import AbstractApiClient
from constant import zhihu as zhihu_constant
from model.m_zhihu import ZhihuComment, ZhihuContent, ZhihuCreator
from proxy.proxy_mixin import ProxyRefreshMixin
from tools import utils

if TYPE_CHECKING:
    from proxy.proxy_ip_pool import ProxyIpPool

from .exception import DataFetchError, ForbiddenError
from .field import SearchSort, SearchTime, SearchType
from .help import ZhihuExtractor, sign


class ZhiHuClient(AbstractApiClient, ProxyRefreshMixin):

    def __init__(
        self,
        timeout=10,
        proxy=None,
        *,
        headers: Dict[str, str],
        playwright_page: Page,
        cookie_dict: Dict[str, str],
        proxy_ip_pool: Optional["ProxyIpPool"] = None,
    ):
        self.proxy = proxy
        self.timeout = timeout
        self.default_headers = headers
        self.cookie_urls = ["https://www.zhihu.com"]
        self.cookie_dict = cookie_dict
        self._extractor = ZhihuExtractor()
        # Initialize proxy pool (from ProxyRefreshMixin)
        self.init_proxy_pool(proxy_ip_pool)

    async def _pre_headers(self, url: str) -> Dict:
        """
        Sign request headers
        Args:
            url: Request URL with query parameters
        Returns:

        """
        d_c0 = self.cookie_dict.get("d_c0")
        if not d_c0:
            raise Exception("d_c0 not found in cookies")
        sign_res = sign(url, self.default_headers.get("cookie", self.default_headers.get("Cookie", "")))
        headers = self.default_headers.copy()
        headers['x-zst-81'] = sign_res["x-zst-81"]
        headers['x-zse-96'] = sign_res["x-zse-96"]
        return headers

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def request(self, method, url, **kwargs) -> Union[str, Any]:
        """
        Wrapper for httpx common request method with response handling
        Args:
            method: Request method
            url: Request URL
            **kwargs: Other request parameters such as headers, body, etc.

        Returns:

        """
        # Check if proxy is expired before each request
        await self._refresh_proxy_if_expired()

        return_response = kwargs.pop('return_response', False)

        async with make_async_client(proxy=self.proxy) as client:
            response = await client.request(method, url, timeout=self.timeout, **kwargs)

        if response.status_code != 200:
            utils.logger.error(f"[ZhiHuClient.request] Request Url: {url}, Request error: {response.text}")
            if response.status_code == 403:
                raise ForbiddenError(response.text)
            elif response.status_code == 404:  # Content without comments also returns 404
                return {}

            raise DataFetchError(response.text)

        if return_response:
            return response.text
        try:
            data: Dict = response.json()
            if data.get("error"):
                utils.logger.error(f"[ZhiHuClient.request] Request error: {data}")
                raise DataFetchError(data.get("error", {}).get("message"))
            return data
        except json.JSONDecodeError:
            utils.logger.error(f"[ZhiHuClient.request] Request error: {response.text}")
            raise DataFetchError(response.text)

    async def get(self, uri: str, params=None, **kwargs) -> Union[Response, Dict, str]:
        """
        GET request with header signing
        Args:
            uri: Request URI
            params: Request parameters

        Returns:

        """
        final_uri = uri
        if isinstance(params, dict):
            final_uri += '?' + urlencode(params)
        headers = await self._pre_headers(final_uri)
        base_url = (zhihu_constant.ZHIHU_URL if "/p/" not in uri else zhihu_constant.ZHIHU_ZHUANLAN_URL)
        return await self.request(method="GET", url=f"{base_url}{final_uri}", headers=headers, **kwargs)

    async def post(self, uri: str, data: dict, **kwargs) -> Dict:
        """
        POST request with header signing
        Args:
            uri: Request route
            data: Request body parameters

        Returns:

        """
        headers = await self._pre_headers(uri)
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return await self.request(
            method="POST",
            url=f"{zhihu_constant.ZHIHU_URL}{uri}",
            data=json_str,
            headers=headers,
            **kwargs,
        )

    async def pong(self) -> bool:
        """
        Check if login status is valid
        Returns:

        """
        utils.logger.info("[ZhiHuClient.pong] Begin pong zhihu...")
        ping_flag = False
        try:
            uri = "/api/v4/me"
            resp_data = await self.get(uri)
            if resp_data.get("id"):
                ping_flag = True
        except Exception as e:
            utils.logger.error(f"[ZhiHuClient.pong] Pong zhihu failed: {e}")
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
        self.default_headers["cookie"] = cookie_str
        self.cookie_dict = cookie_dict
        utils.logger.info(
            f"[ZhiHuClient.update_cookies] Cookie updated successfully for {cookie_urls}"
        )

    async def get_contents_by_keyword(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        sort: SearchSort = SearchSort.DEFAULT,
        search_time: SearchTime = SearchTime.DEFAULT,
        search_type: SearchType = SearchType.ALL,
    ) -> List[ZhihuContent]:
        """
        Search Zhihu contents by keyword
        Args:
            keyword: Keyword
            page: Page number
            page_size: Page size
            sort: Sort method
            search_time: Time range filter
            search_type: Search content type

        Returns:
            List[ZhihuContent]: List of contents
        """
        uri = "/api/v4/search_v3"
        offset = (page - 1) * page_size
        params = {
            "t": search_type.value,
            "q": keyword,
            "correction": "1",
            "offset": str(offset),
            "limit": str(page_size),
            "filter_fields": "",
            "lc_idx": str(offset),
            "show_all_topics": "0",
            "search_source": "Normal",
        }
        if sort != SearchSort.DEFAULT:
            params["sort_by"] = sort.value
        if search_time != SearchTime.DEFAULT:
            params["time_zone"] = search_time.value

        json_data = await self.get(uri, params=params)
        return self._extractor.extract_contents_from_search(json_data)

    async def get_content_by_id(self, content_id: str, content_type: str) -> Optional[ZhihuContent]:
        """
        Get content detail by ID
        Args:
            content_id: Content ID
            content_type: Content type (answer, article, zvideo)

        Returns:
            Optional[ZhihuContent]: Content detail
        """
        if content_type == zhihu_constant.ANSWER_NAME:
            uri = f"/api/v4/answers/{content_id}"
            params = {"include": "content,excerpt,question,author,voteup_count,comment_count,created_time,updated_time"}
            json_data = await self.get(uri, params=params)
            return self._extractor._extract_answer_content(json_data)
        elif content_type == zhihu_constant.ARTICLE_NAME:
            uri = f"/api/v4/articles/{content_id}"
            params = {"include": "content,excerpt,author,voteup_count,comment_count,created,updated"}
            json_data = await self.get(uri, params=params)
            return self._extractor._extract_article_content(json_data)
        elif content_type == zhihu_constant.VIDEO_NAME:
            uri = f"/api/v4/zvideos/{content_id}"
            params = {"include": "description,author,voteup_count,comment_count,created_at,updated_at"}
            json_data = await self.get(uri, params=params)
            return self._extractor._extract_zvideo_content(json_data)
        return None

    async def get_root_comments(
        self, content_id: str, content_type: str, offset: int = 0, limit: int = 20
    ) -> Dict:
        """
        Get root comments for content
        Args:
            content_id: Content ID
            content_type: Content type (answers, articles, zvideos)
            offset: Offset
            limit: Limit

        Returns:
            Dict: JSON response
        """
        endpoint_type = "answers" if content_type == zhihu_constant.ANSWER_NAME else ("articles" if content_type == zhihu_constant.ARTICLE_NAME else "zvideos")
        uri = f"/api/v4/comment_v5/{endpoint_type}/{content_id}/root_comment"
        params = {
            "order_by": "score",
            "limit": str(limit),
            "offset": str(offset),
        }
        return await self.get(uri, params=params)

    async def get_child_comments(self, comment_id: str, offset: int = 0, limit: int = 20) -> Dict:
        """
        Get child comments (sub-comments) for a root comment
        Args:
            comment_id: Comment ID
            offset: Offset
            limit: Limit

        Returns:
            Dict: JSON response
        """
        uri = f"/api/v4/comment_v5/comment/{comment_id}/child_comment"
        params = {
            "order_by": "ts",
            "limit": str(limit),
            "offset": str(offset),
        }
        return await self.get(uri, params=params)

    async def get_all_comments(
        self,
        content_id: str,
        content_type: str,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
        max_count: int = 10,
    ) -> List[ZhihuComment]:
        """
        Get all comments including child comments for a content item
        Args:
            content_id: Content ID
            content_type: Content type
            crawl_interval: Delay between requests in seconds
            callback: Callback function
            max_count: Maximum comments to retrieve

        Returns:
            List[ZhihuComment]: Comment list
        """
        result: List[ZhihuComment] = []
        offset = 0
        limit = 20
        is_end = False

        while not is_end and len(result) < max_count:
            try:
                json_data = await self.get_root_comments(content_id, content_type, offset=offset, limit=limit)
                comments = self._extractor.extract_comments(json_data, content_id)
                if not comments:
                    break

                if len(result) + len(comments) > max_count:
                    comments = comments[: max_count - len(result)]

                if callback:
                    await callback(content_id, comments)
                result.extend(comments)

                # Get sub-comments if enabled
                if config.ENABLE_GET_SUB_COMMENTS:
                    for root_comment in comments:
                        sub_comments = await self.get_all_sub_comments(
                            root_comment.comment_id, content_id, crawl_interval, callback
                        )
                        result.extend(sub_comments)

                pagination = json_data.get("paging", {})
                is_end = pagination.get("is_end", True)
                offset += limit
                await asyncio.sleep(crawl_interval)

            except Exception as e:
                utils.logger.error(f"[ZhiHuClient.get_all_comments] Error fetching comments: {e}")
                break

        return result

    async def get_all_sub_comments(
        self,
        root_comment_id: str,
        content_id: str,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
    ) -> List[ZhihuComment]:
        """
        Get all child comments for a root comment
        Args:
            root_comment_id: Root comment ID
            content_id: Content ID
            crawl_interval: Delay between requests
            callback: Callback function

        Returns:
            List[ZhihuComment]: Sub-comment list
        """
        sub_comments: List[ZhihuComment] = []
        offset = 0
        limit = 20
        is_end = False

        while not is_end:
            try:
                json_data = await self.get_child_comments(root_comment_id, offset=offset, limit=limit)
                comments = self._extractor.extract_comments(json_data, content_id)
                if not comments:
                    break

                if callback:
                    await callback(content_id, comments)
                sub_comments.extend(comments)

                pagination = json_data.get("paging", {})
                is_end = pagination.get("is_end", True)
                offset += limit
                await asyncio.sleep(crawl_interval)
            except Exception as e:
                utils.logger.error(f"[ZhiHuClient.get_all_sub_comments] Error fetching child comments: {e}")
                break

        return sub_comments

    async def get_creator_info(self, url_token: str) -> ZhihuCreator:
        """
        Get creator profile info
        Args:
            url_token: Creator url token

        Returns:
            ZhihuCreator: Creator profile object
        """
        uri = f"/api/v4/members/{url_token}"
        params = {"include": "headline,description,gender,follower_count,following_count,answer_count,articles_count,zvideo_count,voteup_count"}
        json_data = await self.get(uri, params=params)
        return self._extractor.extract_creator_info(json_data)

    async def get_creator_contents(self, url_token: str, offset: int = 0, limit: int = 20) -> Dict:
        """
        Get creator published contents
        Args:
            url_token: Creator url token
            offset: Offset
            limit: Limit

        Returns:
            Dict: JSON response
        """
        uri = f"/api/v4/members/{url_token}/creations"
        params = {
            "offset": str(offset),
            "limit": str(limit),
        }
        return await self.get(uri, params=params)

    async def get_all_creator_contents(
        self,
        url_token: str,
        crawl_interval: float = 1.0,
        callback: Optional[Callable] = None,
        max_count: int = 0,
    ) -> List[ZhihuContent]:
        """
        Get all creator published contents
        Args:
            url_token: Creator url token
            crawl_interval: Delay between requests
            callback: Callback function
            max_count: Maximum items to retrieve

        Returns:
            List[ZhihuContent]: List of creator contents
        """
        result: List[ZhihuContent] = []
        offset = 0
        limit = 20
        is_end = False

        while not is_end and (max_count == 0 or len(result) < max_count):
            try:
                json_data = await self.get_creator_contents(url_token, offset=offset, limit=limit)
                contents = self._extractor.extract_creator_contents(json_data)
                if not contents:
                    break

                if max_count > 0 and len(result) + len(contents) > max_count:
                    contents = contents[: max_count - len(result)]

                if callback:
                    await callback(contents)
                result.extend(contents)

                pagination = json_data.get("paging", {})
                is_end = pagination.get("is_end", True)
                offset += limit
                await asyncio.sleep(crawl_interval)

            except Exception as e:
                utils.logger.error(f"[ZhiHuClient.get_all_creator_contents] Error fetching creator contents: {e}")
                break

        return result
