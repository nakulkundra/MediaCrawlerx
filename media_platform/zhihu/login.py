# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/zhihu/login.py
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
from tools import utils


class ZhiHuLogin(AbstractLogin):

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
    async def check_login_state(self) -> bool:
        """
        Check if the current login status is successful and return True otherwise return False
        Returns:

        """
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        if cookie_dict.get("z_c0"):
            return True
        return False

    async def begin(self):
        """Start login zhihu"""
        utils.logger.info("[ZhiHuLogin.begin] Begin login zhihu ...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError(
                "[ZhiHuLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ..."
            )

    async def login_by_qrcode(self):
        """login zhihu website and keep webdriver login state"""
        utils.logger.info("[ZhiHuLogin.login_by_qrcode] Begin login zhihu by qrcode ...")
        # find login qrcode
        qrcode_img_selector = "xpath=//img[@class='Qrcode-img']"
        base64_qrcode_img = await utils.find_login_qrcode(
            self.context_page, selector=qrcode_img_selector
        )
        if not base64_qrcode_img:
            utils.logger.info(
                "[ZhiHuLogin.login_by_qrcode] login failed , have not found qrcode please check ...."
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
            f"[ZhiHuLogin.login_by_qrcode] Waiting for scan code login, remaining time is 120s"
        )

        try:
            await self.check_login_state()
        except RetryError:
            utils.logger.info(
                "[ZhiHuLogin.login_by_qrcode] Login zhihu failed by qrcode login method ..."
            )
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(
            f"[ZhiHuLogin.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ..."
        )
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_mobile(self):
        pass

    async def login_by_cookies(self):
        utils.logger.info("[ZhiHuLogin.login_by_cookies] Begin login zhihu by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(
            self.cookie_str
        ).items():
            await self.browser_context.add_cookies(
                [
                    {
                        "name": key,
                        "value": value,
                        "domain": ".zhihu.com",
                        "path": "/",
                    }
                ]
            )
