# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/xhs/login.py
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
import functools
import sys
from typing import Optional

from playwright.async_api import BrowserContext, Page
from tenacity import (
    RetryError,
    retry,
    retry_if_result,
    stop_after_attempt,
    wait_fixed,
)

import config
from base.base_crawler import AbstractLogin
from cache.cache_factory import CacheFactory
from tools import utils


class XiaoHongShuLogin(AbstractLogin):

    def __init__(
        self,
        login_type: str,
        browser_context: BrowserContext,
        context_page: Page,
        login_phone: Optional[str] = "",
        cookie_str: str = "",
    ):
        config.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    @retry(
        stop=stop_after_attempt(600),
        wait=wait_fixed(1),
        retry=retry_if_result(lambda value: value is False),
    )
    async def check_login_state(self, no_logged_in_session: str) -> bool:
        """
        Verify login status using dual-check: UI elements and Cookies.
        """
        # 1. Priority check: Check if the "Me" (Profile) node appears in the sidebar
        try:
            # Selector for elements containing "Me" text with a link pointing to the profile
            # XPath Explanation: Find a span with text "Me" inside an anchor tag (<a>)
            # whose href attribute contains "/user/profile/"
            user_profile_selector = "xpath=//a[contains(@href, '/user/profile/')]//span[text()='我']"

            # Set a short timeout since this is called within a retry loop
            is_visible = await self.context_page.is_visible(user_profile_selector, timeout=500)
            if is_visible:
                utils.logger.info(
                    "[XiaoHongShuLogin.check_login_state] Login status confirmed by UI element ('Me' button)."
                )
                return True
        except Exception:
            pass

        # 2. Alternative: Check for CAPTCHA prompt
        if "请通过验证" in await self.context_page.content():
            utils.logger.info(
                "[XiaoHongShuLogin.check_login_state] CAPTCHA appeared, please verify manually."
            )

        # 3. Compatibility fallback: Original Cookie-based change detection
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        current_web_session = cookie_dict.get("web_session")

        # If web_session has changed, consider the login successful
        if current_web_session and current_web_session != no_logged_in_session:
            utils.logger.info(
                "[XiaoHongShuLogin.check_login_state] Login status confirmed by Cookie (web_session changed)."
            )
            return True

        return False

    async def begin(self):
        """Start login xiaohongshu"""
        utils.logger.info("[XiaoHongShuLogin.begin] Begin login xiaohongshu ...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError(
                "[XiaoHongShuLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ..."
            )

    async def login_by_qrcode(self):
        """login xiaohongshu website and keep webdriver login state"""
        utils.logger.info(
            "[XiaoHongShuLogin.login_by_qrcode] Begin login xiaohongshu by qrcode ..."
        )
        # find login qrcode
        qrcode_img_selector = "xpath=//img[@class='qrcode-img']"
        base64_qrcode_img = await utils.find_login_qrcode(
            self.context_page, selector=qrcode_img_selector
        )
        if not base64_qrcode_img:
            utils.logger.info(
                "[XiaoHongShuLogin.login_by_qrcode] login failed , have not found qrcode please check ...."
            )
            sys.exit()

        # show login qrcode
        partial_show_qrcode = functools.partial(
            utils.show_qrcode, base64_qrcode_img
        )
        asyncio.get_running_loop().run_in_executor(
            executor=None, func=partial_show_qrcode
        )

        utils.logger.info(
            f"[XiaoHongShuLogin.login_by_qrcode] Waiting for scan code login, remaining time is 120s"
        )

        # get not logged session
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        no_logged_in_session = cookie_dict.get("web_session")

        try:
            await self.check_login_state(no_logged_in_session)
        except RetryError:
            utils.logger.info(
                "[XiaoHongShuLogin.login_by_qrcode] Login xiaohongshu failed by qrcode login method ..."
            )
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(
            f"[XiaoHongShuLogin.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ..."
        )
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_mobile(self):
        """login xiaohongshu website by mobile phone and sms code"""
        utils.logger.info(
            "[XiaoHongShuLogin.login_by_mobile] Begin login xiaohongshu by mobile ..."
        )
        # Mobile login placeholder
        pass

    async def login_by_cookies(self):
        """login xiaohongshu website by cookies"""
        utils.logger.info(
            "[XiaoHongShuLogin.login_by_cookies] Begin login xiaohongshu by cookie ..."
        )
        for key, value in utils.convert_str_cookie_to_dict(
            self.cookie_str
        ).items():
            await self.browser_context.add_cookies(
                [
                    {
                        "name": key,
                        "value": value,
                        "domain": ".xiaohongshu.com",
                        "path": "/",
                    }
                ]
            )
