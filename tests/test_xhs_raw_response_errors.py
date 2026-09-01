# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_xhs_raw_response_errors.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import json
from unittest.mock import AsyncMock, Mock
import httpx
import pytest
from tenacity import RetryError

from media_platform.xhs.client import XiaoHongShuClient
from media_platform.xhs.exception import IPBlockError, PlatformAccessError


class FakeAsyncClient:
    def __init__(self, request_impl):
        self.request_impl = request_impl

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def request(self, *args, **kwargs):
        return await self.request_impl(*args, **kwargs)


def make_client():
    client = XiaoHongShuClient(
        headers={"Cookie": "web_session=test"},
        playwright_page=object(),
        cookie_dict={},
    )
    client._refresh_proxy_if_expired = AsyncMock()
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [401, 403, 429])
async def test_raw_response_rejects_access_http_status(monkeypatch, status_code):
    calls = 0

    async def request_impl(method, url, **kwargs):
        nonlocal calls
        calls += 1
        return httpx.Response(
            status_code,
            text="blocked",
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(
        "media_platform.xhs.client.httpx.AsyncClient",
        lambda **kwargs: FakeAsyncClient(request_impl),
    )

    client = make_client()
    with pytest.raises(PlatformAccessError):
        await client.request("GET", "https://edith.xiaohongshu.com/api/sns/web/v1/feed")
