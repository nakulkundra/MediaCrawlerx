# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_cdp_browser.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from unittest.mock import AsyncMock, MagicMock
import pytest

import config
from tools.cdp_browser import CDPBrowserManager


@pytest.mark.asyncio
async def test_existing_browser_connects_directly_to_devtools_browser(monkeypatch):
    monkeypatch.setattr(config, "CDP_CONNECT_EXISTING", True)
    monkeypatch.setattr(config, "BROWSER_LAUNCH_TIMEOUT", 60)

    manager = CDPBrowserManager()
    manager.debug_port = 9222
    manager._get_browser_websocket_url = AsyncMock(
        side_effect=AssertionError("existing browser mode must not call /json/version")
    )

    browser = MagicMock()
    browser.is_connected.return_value = True
    browser.contexts = []

    playwright = MagicMock()
    playwright.chromium.connect_over_cdp = AsyncMock(return_value=browser)

    manager.playwright = playwright
    manager.browser = None

    result = await manager._connect_existing_browser()

    assert result is True
    playwright.chromium.connect_over_cdp.assert_awaited_once_with(
        endpoint_url="http://localhost:9222",
        timeout=60000,
    )
