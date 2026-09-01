# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_xhs_core_access_error.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Regression tests (Xiaohongshu xhs): Access restricted exceptions must not break asyncio.gather.

Background:
When IPBlockError / PlatformAccessError are not retried, tenacity re-raises them directly.
Core layer handles IPBlockError / PlatformAccessError gracefully, returning None and continuing with the remaining batch.

Covers:
1. Note detail tasks skip on IPBlockError / PlatformAccessError and return None.
2. Batch gather does not fail entirely when one note is rate-limited.
3. Creator homepage scraping skips on rate-limiting rather than aborting the entire run.
"""

import asyncio
from unittest.mock import AsyncMock
import pytest

import config
from media_platform.xhs.core import XiaoHongShuCrawler
from media_platform.xhs.exception import IPBlockError, PlatformAccessError


def make_crawler(xhs_client):
    crawler = XiaoHongShuCrawler.__new__(XiaoHongShuCrawler)
    crawler.xhs_client = xhs_client
    return crawler


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [
        IPBlockError("Network connection error"),
        PlatformAccessError("XHS request blocked with HTTP 403"),
    ],
)
async def test_note_detail_task_skips_access_error(error):
    xhs_client = AsyncMock()
    xhs_client.get_note_by_id.side_effect = error
    xhs_client.get_note_by_id_from_html.side_effect = AssertionError(
        "Should not attempt HTML fallback after rate limit"
    )

    result = await make_crawler(xhs_client).get_note_detail_async_task(
        note_id="n1",
        xsec_source="pc_search",
        xsec_token="tok1",
        semaphore=asyncio.Semaphore(1),
    )

    assert result is None
