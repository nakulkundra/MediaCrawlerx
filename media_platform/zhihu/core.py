# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/zhihu/core.py
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
import os
from asyncio import Task
from typing import Dict, List, Optional, Tuple, cast

from playwright.async_api import (
    BrowserContext,
    BrowserType,
    Page,
    Playwright,
    async_playwright,
)

import config
from base.base_crawler import AbstractCrawler
from constant import zhihu as constant
from model.m_zhihu import ZhihuContent, ZhihuCreator
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import zhihu as zhihu_store
from tools import utils
from tools.cdp_browser import CDPBrowserManager
from var import crawler_type_var, source_keyword_var

from .client import ZhiHuClient
from .exception import DataFetchError
from .help import ZhihuExtractor, judge_zhihu_url
from .login import ZhiHuLogin


class ZhihuCrawler(AbstractCrawler):
    context_page: Page
    zhihu_client: ZhiHuClient
    browser_context: BrowserContext
    cdp_manager: Optional[CDPBrowserManager]

    def __init__(self) -> None:
        self.index_url = "https://www.zhihu.com"
        self.cookie_urls = [self.index_url]
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        self._extractor = ZhihuExtractor()
        self.cdp_manager = None
        self.ip_proxy_pool = None  # Proxy IP pool for automatic proxy refresh

    async def start(self) -> None:
        """
        Start the crawler
        Returns:

        """
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            self.ip_proxy_pool = await create_ip_pool(
                config.IP_PROXY_POOL_COUNT, enable_validate_ip=True
            )
            ip_proxy_info: IpInfoModel = await self.ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = utils.format_proxy_info(
                ip_proxy_info
            )

        async with async_playwright() as playwright:
            # Choose launch mode based on configuration
            if config.ENABLE_CDP_MODE:
                utils.logger.info("[ZhihuCrawler] Launching browser in CDP mode")
                self.browser_context = await self.launch_browser_with_cdp(
                    playwright,
                    playwright_proxy_format,
                    self.user_agent,
                    headless=config.CDP_HEADLESS,
                )
            else:
                utils.logger.info("[ZhihuCrawler] Launching browser in standard mode")
                # Launch a browser context.
                chromium = playwright.chromium
                self.browser_context = await self.launch_browser(
                    chromium, None, self.user_agent, headless=config.HEADLESS
                )
                # stealth.min.js is a js script to prevent the website from detecting the crawler.
                await self.browser_context.add_init_script(path="libs/stealth.min.js")

            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url, wait_until="domcontentloaded")

            # Create a client to interact with the zhihu website.
            self.zhihu_client = await self.create_zhihu_client(httpx_proxy_format)
            if not await self.zhihu_client.pong():
                login_obj = ZhiHuLogin(
                    login_type=config.LOGIN_TYPE,
                    login_phone="",  # input your phone number
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    cookie_str=config.COOKIES,
                )
                await login_obj.begin()
                await self.zhihu_client.update_cookies(
                    browser_context=self.browser_context,
                    urls=self.cookie_urls,
                )

            # Zhihu's search API requires opening the search page first to access cookies, homepage alone won't work
            utils.logger.info(
                "[ZhihuCrawler.start] Zhihu navigating to search page to get search page cookies, this process takes about 5 seconds"
            )
            await self.context_page.goto(
                f"{self.index_url}/search?q=python&search_source=Guess&utm_content=search_hot&type=content"
            )
            await asyncio.sleep(5)
            await self.zhihu_client.update_cookies(
                browser_context=self.browser_context,
                urls=self.cookie_urls,
            )

            crawler_type_var.set(config.CRAWLER_TYPE)
            if config.CRAWLER_TYPE == "search":
                # Search for contents and retrieve their comments
                await self.search()
            elif config.CRAWLER_TYPE == "detail":
                # Get the information and comments of the specified content
                await self.get_specified_notes()
            elif config.CRAWLER_TYPE == "creator":
                # Get creator's information and their contents and comments
                await self.get_specified_creators()
            else:
                pass

            utils.logger.info("[ZhihuCrawler.start] Zhihu Crawler finished ...")

    async def search(self) -> None:
        """
        Search for contents and retrieve their comment information.
        Returns:

        """
        utils.logger.info("[ZhihuCrawler.search] Begin search zhihu keywords")
        zhihu_limit_count = 20
        if config.CRAWLER_MAX_NOTES_COUNT < zhihu_limit_count:
            config.CRAWLER_MAX_NOTES_COUNT = zhihu_limit_count
        start_page = config.START_PAGE

        for keyword in config.KEYWORDS.split(","):
            source_keyword_var.set(keyword)
            utils.logger.info(f"[ZhihuCrawler.search] Current search keyword: {keyword}")
            page = 1
            while (page - start_page + 1) * zhihu_limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    utils.logger.info(f"[ZhihuCrawler.search] Skip page {page}")
                    page += 1
                    continue
                try:
                    utils.logger.info(f"[ZhihuCrawler.search] search zhihu keyword: {keyword}, page: {page}")
                    content_list: List[ZhihuContent] = await self.zhihu_client.get_contents_by_keyword(
                        keyword=keyword,
                        page=page,
                        page_size=zhihu_limit_count,
                    )
                    if not content_list:
                        utils.logger.info(f"[ZhihuCrawler.search] Search content list is empty")
                        break

                    utils.logger.info(f"[ZhihuCrawler.search] Content list len: {len(content_list)}")
                    for content_item in content_list:
                        await zhihu_store.update_zhihu_content(content_item)

                    await self.batch_get_contents_comments(content_list)

                    await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                    utils.logger.info(f"[ZhihuCrawler.search] Sleeping for {config.CRAWLER_MAX_SLEEP_SEC} seconds after page {page}")

                    page += 1
                except Exception as ex:
                    utils.logger.error(f"[ZhihuCrawler.search] Search error, page: {page}, keyword: {keyword}, err: {ex}")
                    break

    async def get_specified_notes(self):
        """
        Get specified notes information and comments
        """
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = []
        for url in config.ZHIHU_SPECIFIED_ID_LIST:
            url_info = judge_zhihu_url(url)
            content_type = url_info.get("type")
            content_id = url_info.get("id")
            if content_type and content_id:
                task_list.append(self.get_content_detail_task(content_id, content_type, semaphore))

        contents = await asyncio.gather(*task_list)
        valid_contents = [c for c in contents if c is not None]
        for content in valid_contents:
            await zhihu_store.update_zhihu_content(content)

        await self.batch_get_contents_comments(valid_contents)

    async def get_content_detail_task(
        self, content_id: str, content_type: str, semaphore: asyncio.Semaphore
    ) -> Optional[ZhihuContent]:
        """Get single content detail task"""
        async with semaphore:
            try:
                utils.logger.info(f"[ZhihuCrawler.get_content_detail] Begin get content detail, id: {content_id}")
                content = await self.zhihu_client.get_content_by_id(content_id, content_type)
                await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                return content
            except Exception as e:
                utils.logger.error(f"[ZhihuCrawler.get_content_detail] Error getting content {content_id}: {e}")
                return None

    async def batch_get_contents_comments(self, content_list: List[ZhihuContent]):
        """Batch get comments for contents"""
        if not config.ENABLE_GET_COMMENTS:
            return

        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list: List[Task] = []
        for content in content_list:
            task = asyncio.create_task(
                self.get_comments_async_task(content, semaphore),
                name=content.content_id,
            )
            task_list.append(task)
        await asyncio.gather(*task_list)

    async def get_comments_async_task(
        self, content: ZhihuContent, semaphore: asyncio.Semaphore
    ):
        """Get comments async task"""
        async with semaphore:
            utils.logger.info(f"[ZhihuCrawler.get_comments] Begin get comments for content_id: {content.content_id}")
            await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)

            try:
                await self.zhihu_client.get_all_comments(
                    content_id=content.content_id,
                    content_type=content.content_type,
                    crawl_interval=config.CRAWLER_MAX_SLEEP_SEC,
                    callback=zhihu_store.batch_update_zhihu_comments,
                    max_count=config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES,
                )
            except Exception as e:
                utils.logger.error(f"[ZhihuCrawler.get_comments] Error getting comments for content {content.content_id}: {e}")

    async def get_specified_creators(self) -> None:
        """Get creator's information and their contents and comments"""
        utils.logger.info("[ZhihuCrawler.get_specified_creators] Begin get zhihu creators")
        for creator_url in config.ZHIHU_CREATOR_URL_LIST:
            url_info = judge_zhihu_url(creator_url)
            url_token = url_info.get("url_token")
            if not url_token:
                continue

            try:
                creator_info = await self.zhihu_client.get_creator_info(url_token)
                if creator_info:
                    await zhihu_store.save_creator(creator_info)

                    contents = await self.zhihu_client.get_all_creator_contents(
                        url_token=url_token,
                        crawl_interval=config.CRAWLER_MAX_SLEEP_SEC,
                        callback=zhihu_store.batch_update_zhihu_contents,
                        max_count=config.CRAWLER_MAX_NOTES_COUNT,
                    )
                    await self.batch_get_contents_comments(contents)
            except Exception as e:
                utils.logger.error(f"[ZhihuCrawler.get_specified_creators] Error getting creator {url_token}: {e}")

    async def create_zhihu_client(self, httpx_proxy: Optional[str]) -> ZhiHuClient:
        """Create zhihu client"""
        utils.logger.info("[ZhihuCrawler.create_zhihu_client] Begin create zhihu API client ...")
        cookie_str, cookie_dict = await utils.convert_browser_context_cookies(
            self.browser_context,
            urls=self.cookie_urls,
        )
        zhihu_client = ZhiHuClient(
            proxy=httpx_proxy,
            headers={
                "User-Agent": self.user_agent,
                "cookie": cookie_str,
                "Origin": "https://www.zhihu.com",
                "Referer": "https://www.zhihu.com/",
                "Content-Type": "application/json;charset=UTF-8",
                "x-requested-with": "fetch",
            },
            playwright_page=self.context_page,
            cookie_dict=cookie_dict,
            proxy_ip_pool=self.ip_proxy_pool,
        )
        return zhihu_client

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """Launch browser and create browser context"""
        utils.logger.info("[ZhihuCrawler.launch_browser] Begin create browser context ...")
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
            utils.logger.info(f"[ZhihuCrawler] CDP browser info: {browser_info}")
            return browser_context
        except Exception as e:
            utils.logger.error(f"[ZhihuCrawler] CDP mode launch failed, falling back to standard: {e}")
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
        utils.logger.info("[ZhihuCrawler.close] Browser context closed ...")
