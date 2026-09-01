# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/xhs/core.py
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
import os
import random
from asyncio import Task
from typing import Dict, List, Optional

from playwright.async_api import (
    BrowserContext,
    BrowserType,
    Page,
    Playwright,
    async_playwright,
)
from tenacity import RetryError

import config
from base.base_crawler import AbstractCrawler
from model.m_xiaohongshu import CreatorUrlInfo, NoteUrlInfo
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import xhs as xhs_store
from tools import utils
from tools.cdp_browser import CDPBrowserManager
from var import crawler_type_var, source_keyword_var

from .client import XiaoHongShuClient
from .exception import (
    DataFetchError,
    IPBlockError,
    NoteNotFoundError,
    PlatformAccessError,
)
from .field import SearchSortType
from .help import get_search_id, parse_creator_info_from_url, parse_note_info_from_note_url
from .login import XiaoHongShuLogin


class XiaoHongShuCrawler(AbstractCrawler):
    context_page: Page
    xhs_client: XiaoHongShuClient
    browser_context: BrowserContext
    cdp_manager: Optional[CDPBrowserManager]

    def __init__(self) -> None:
        self.index_url = "https://www.rednote.com" if config.XHS_INTERNATIONAL else "https://www.xiaohongshu.com"
        self.cookie_urls = [self.index_url]
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        self.cdp_manager = None
        self.ip_proxy_pool = None  # Proxy IP pool for automatic proxy refresh

    async def start(self) -> None:
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            self.ip_proxy_pool = await create_ip_pool(config.IP_PROXY_POOL_COUNT, enable_validate_ip=True)
            ip_proxy_info: IpInfoModel = await self.ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = utils.format_proxy_info(ip_proxy_info)

        async with async_playwright() as playwright:
            # Choose launch mode based on configuration
            if config.ENABLE_CDP_MODE:
                utils.logger.info("[XiaoHongShuCrawler] Launching browser using CDP mode")
                self.browser_context = await self.launch_browser_with_cdp(
                    playwright,
                    playwright_proxy_format,
                    self.user_agent,
                    headless=config.CDP_HEADLESS,
                )
            else:
                utils.logger.info("[XiaoHongShuCrawler] Launching browser using standard mode")
                # Launch a browser context.
                chromium = playwright.chromium
                self.browser_context = await self.launch_browser(
                    chromium,
                    playwright_proxy_format,
                    self.user_agent,
                    headless=config.HEADLESS,
                )
                # stealth.min.js is a js script to prevent the website from detecting the crawler.
                await self.browser_context.add_init_script(path="libs/stealth.min.js")

            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url)

            # Create a client to interact with the Xiaohongshu website.
            self.xhs_client = await self.create_xhs_client(httpx_proxy_format)
            if not await self.xhs_client.pong():
                login_obj = XiaoHongShuLogin(
                    login_type=config.LOGIN_TYPE,
                    login_phone="",  # input your phone number
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    cookie_str=config.COOKIES,
                )
                await login_obj.begin()
                await self.xhs_client.update_cookies(
                    browser_context=self.browser_context,
                    urls=self.cookie_urls,
                )

            crawler_type_var.set(config.CRAWLER_TYPE)
            if config.CRAWLER_TYPE == "search":
                # Search for notes and retrieve their comment information.
                await self.search()
            elif config.CRAWLER_TYPE == "detail":
                # Get the information and comments of the specified post
                await self.get_specified_notes()
            elif config.CRAWLER_TYPE == "creator":
                # Get creator's information and their notes and comments
                await self.get_creators_and_notes()
            else:
                pass

            utils.logger.info("[XiaoHongShuCrawler.start] Xhs Crawler finished ...")

    async def search(self) -> None:
        """Search for notes and retrieve their comment information."""
        utils.logger.info("[XiaoHongShuCrawler.search] Begin search Xiaohongshu keywords")
        xhs_limit_count = 20  # Xiaohongshu limit page fixed value
        if config.CRAWLER_MAX_NOTES_COUNT < xhs_limit_count:
            config.CRAWLER_MAX_NOTES_COUNT = xhs_limit_count
        start_page = config.START_PAGE
        for keyword in config.KEYWORDS.split(","):
            source_keyword_var.set(keyword)
            utils.logger.info(f"[XiaoHongShuCrawler.search] Current search keyword: {keyword}")
            page = 1
            search_id = get_search_id()
            while (page - start_page + 1) * xhs_limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    utils.logger.info(f"[XiaoHongShuCrawler.search] Skip page {page}")
                    page += 1
                    continue
                try:
                    utils.logger.info(
                        f"[XiaoHongShuCrawler.search] search xhs keyword: {keyword}, page: {page}"
                    )
                    notes_res = await self.xhs_client.get_note_by_keyword(
                        keyword=keyword,
                        page=page,
                        page_size=xhs_limit_count,
                        sort=SearchSortType.GENERAL,
                        search_id=search_id,
                    )
                    items = notes_res.get("items", [])
                    if not items:
                        utils.logger.info(f"[XiaoHongShuCrawler.search] Search item list is empty")
                        break
                    utils.logger.info(f"[XiaoHongShuCrawler.search] Search items len: {len(items)}")
                    note_id_list = []
                    xsec_token_list = []
                    for item in items:
                        if item.get("model_type") == "note":
                            note_id_list.append(item.get("id"))
                            xsec_token_list.append(item.get("xsec_token", ""))
                    await self.get_specified_notes(note_id_list=note_id_list, xsec_token_list=xsec_token_list)

                    # Sleep after page navigation
                    await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                    utils.logger.info(f"[XiaoHongShuCrawler.search] Sleeping for {config.CRAWLER_MAX_SLEEP_SEC} seconds after page {page}")

                    page += 1
                except Exception as ex:
                    utils.logger.error(
                        f"[XiaoHongShuCrawler.search] Search error, page: {page}, keyword: {keyword}, err: {ex}"
                    )
                    break

    async def get_specified_notes(
        self,
        note_id_list: Optional[List[str]] = None,
        xsec_token_list: Optional[List[str]] = None,
    ):
        """
        Get information and comments of specified posts
        """
        if note_id_list is None:
            note_url_list = config.XHS_SPECIFIED_ID_LIST
            note_info_list = [parse_note_info_from_note_url(url) for url in note_url_list]
            note_id_list = [info.note_id for info in note_info_list if info.note_id]
            xsec_token_list = [info.xsec_token for info in note_info_list if info.note_id]

        if not note_id_list:
            return

        if not xsec_token_list:
            xsec_token_list = [""] * len(note_id_list)

        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_note_detail_async_task(
                note_id=note_id, xsec_token=xsec_token, semaphore=semaphore
            )
            for note_id, xsec_token in zip(note_id_list, xsec_token_list)
        ]
        note_details = await asyncio.gather(*task_list)
        for note_detail in note_details:
            if note_detail is not None:
                await xhs_store.update_xhs_note(note_detail)

        await self.batch_get_notes_comments(note_id_list, xsec_token_list)

    async def get_note_detail_async_task(
        self, note_id: str, xsec_token: str, semaphore: asyncio.Semaphore
    ) -> Optional[Dict]:
        """Get note detail async task"""
        async with semaphore:
            try:
                utils.logger.info(f"[XiaoHongShuCrawler.get_note_detail] Begin get note detail, note_id: {note_id}")
                note_detail = await self.xhs_client.get_note_by_id(note_id, xsec_token=xsec_token)

                await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                utils.logger.info(
                    f"[XiaoHongShuCrawler.get_note_detail] Sleeping for {config.CRAWLER_MAX_SLEEP_SEC} seconds after fetching note details {note_id}"
                )
                if not note_detail:
                    utils.logger.warning(f"[XiaoHongShuCrawler.get_note_detail] API empty, trying HTML parser for {note_id}")
                    note_detail = await self.xhs_client.get_note_by_id_from_html(note_id, xsec_token=xsec_token)

                return note_detail
            except Exception as ex:
                utils.logger.error(f"[XiaoHongShuCrawler.get_note_detail] Get note detail error: {ex}")
                return None

    async def batch_get_notes_comments(
        self, note_id_list: List[str], xsec_token_list: List[str]
    ):
        """Batch get notes comments"""
        if not config.ENABLE_GET_COMMENTS:
            return

        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list: List[Task] = []
        for note_id, xsec_token in zip(note_id_list, xsec_token_list):
            task = asyncio.create_task(
                self.get_comments_async_task(note_id, xsec_token, semaphore),
                name=note_id,
            )
            task_list.append(task)
        await asyncio.gather(*task_list)

    async def get_comments_async_task(
        self, note_id: str, xsec_token: str, semaphore: asyncio.Semaphore
    ):
        """Get comments async task"""
        async with semaphore:
            utils.logger.info(f"[XiaoHongShuCrawler.get_comments] Begin get comments for note_id: {note_id}")
            await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)

            try:
                await self.xhs_client.get_note_all_comments(
                    note_id=note_id,
                    crawl_interval=config.CRAWLER_MAX_SLEEP_SEC,
                    callback=xhs_store.batch_update_xhs_note_comments,
                    max_count=config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES,
                    xsec_token=xsec_token,
                )
            except Exception as ex:
                utils.logger.error(f"[XiaoHongShuCrawler.get_comments] Failed to get comments for note {note_id}: {ex}")

    async def get_creators_and_notes(self) -> None:
        """Get creator's information and their notes and comments"""
        utils.logger.info("[XiaoHongShuCrawler.get_creators_and_notes] Begin get xhs creators")
        for creator_url in config.XHS_CREATOR_URL_LIST:
            creator_url_info: CreatorUrlInfo = parse_creator_info_from_url(creator_url)
            if not creator_url_info.user_id:
                continue

            creator_info_res = await self.xhs_client.get_creator_info(user_id=creator_url_info.user_id)
            if creator_info_res:
                creator_info = creator_info_res.get("basic_info", {})
                await xhs_store.save_creator(creator_url_info.user_id, creator_info)

                notes_list = await self.xhs_client.get_all_notes_by_creator(
                    user_id=creator_url_info.user_id,
                    crawl_interval=config.CRAWLER_MAX_SLEEP_SEC,
                    callback=xhs_store.batch_update_xhs_notes,
                )
                note_id_list = [note.get("note_id") or note.get("id") for note in notes_list if note.get("note_id") or note.get("id")]
                xsec_token_list = [note.get("xsec_token", "") for note in notes_list if note.get("note_id") or note.get("id")]
                await self.batch_get_notes_comments(note_id_list, xsec_token_list)

    async def create_xhs_client(self, httpx_proxy: Optional[str]) -> XiaoHongShuClient:
        """Create xhs client"""
        utils.logger.info("[XiaoHongShuCrawler.create_xhs_client] Begin create xhs API client ...")
        cookie_str, cookie_dict = await utils.convert_browser_context_cookies(
            self.browser_context,
            urls=self.cookie_urls,
        )
        xhs_client = XiaoHongShuClient(
            proxy=httpx_proxy,
            headers={
                "User-Agent": self.user_agent,
                "Cookie": cookie_str,
                "Origin": self.index_url,
                "Referer": self.index_url + "/",
                "Content-Type": "application/json;charset=UTF-8",
            },
            playwright_page=self.context_page,
            cookie_dict=cookie_dict,
            proxy_ip_pool=self.ip_proxy_pool,
        )
        return xhs_client

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """Launch browser and create browser context"""
        utils.logger.info("[XiaoHongShuCrawler.launch_browser] Begin create browser context ...")
        if config.SAVE_LOGIN_STATE:
            user_data_dir = os.path.join(
                os.getcwd(), "browser_data", config.USER_DATA_DIR % config.PLATFORM
            )
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                accept_downloads=True,
                headless=headless,
                proxy=playwright_proxy,  # type: ignore
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent,
                channel="chrome",
            )
            return browser_context
        else:
            browser = await chromium.launch(
                headless=headless, proxy=playwright_proxy, channel="chrome"  # type: ignore
            )
            browser_context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}, user_agent=user_agent
            )
            return browser_context

    async def launch_browser_with_cdp(
        self,
        playwright: Playwright,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """Launch browser using CDP mode"""
        try:
            self.cdp_manager = CDPBrowserManager()
            browser_context = await self.cdp_manager.launch_and_connect(
                playwright=playwright,
                playwright_proxy=playwright_proxy,
                user_agent=user_agent,
                headless=headless,
            )
            browser_info = await self.cdp_manager.get_browser_info()
            utils.logger.info(f"[XiaoHongShuCrawler] CDP browser info: {browser_info}")
            return browser_context
        except Exception as e:
            utils.logger.error(f"[XiaoHongShuCrawler] CDP mode launch failed, falling back to standard: {e}")
            chromium = playwright.chromium
            return await self.launch_browser(
                chromium, playwright_proxy, user_agent, headless
            )

    async def close(self):
        """Close browser context"""
        if self.cdp_manager:
            await self.cdp_manager.cleanup()
            self.cdp_manager = None
        else:
            await self.browser_context.close()
        utils.logger.info("[XiaoHongShuCrawler.close] Browser context closed ...")
