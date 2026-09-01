# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_api_limits.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

import config
from api.main import app
from api.schemas import CrawlerStartRequest, CrawlerTypeEnum, LoginTypeEnum, PlatformEnum
from api.services.crawler_manager import CrawlerManager
from cmd_arg import parse_cmd


@pytest.mark.asyncio
async def test_cmd_arg_crawler_max_notes_count():
    # Store original values
    orig_notes = config.CRAWLER_MAX_NOTES_COUNT
    orig_comments = config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES

    try:
        await parse_cmd([
            "--platform", "xhs",
            "--crawler_max_notes_count", "42",
            "--max_comments_count_singlenotes", "24"
        ])
        assert config.CRAWLER_MAX_NOTES_COUNT == 42
        assert config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES == 24
    finally:
        config.CRAWLER_MAX_NOTES_COUNT = orig_notes
        config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = orig_comments


def test_crawler_manager_build_command():
    cm = CrawlerManager()

    # 1. No max limits passed in API request
    req1 = CrawlerStartRequest(
        platform=PlatformEnum.XHS,
        login_type=LoginTypeEnum.QRCODE,
        crawler_type=CrawlerTypeEnum.SEARCH,
        keywords="test",
    )
    cmd1 = cm._build_command(req1)
    assert "--crawler_max_notes_count" not in cmd1
    assert "--max_comments_count_singlenotes" not in cmd1

    # 2. Limits specified in API request
    req2 = CrawlerStartRequest(
        platform=PlatformEnum.XHS,
        login_type=LoginTypeEnum.QRCODE,
        crawler_type=CrawlerTypeEnum.SEARCH,
        keywords="test",
        crawler_max_notes_count=50,
        max_comments_count_singlenotes=100,
    )
    cmd2 = cm._build_command(req2)
    assert "--crawler_max_notes_count" in cmd2
    idx_notes = cmd2.index("--crawler_max_notes_count")
    assert cmd2[idx_notes + 1] == "50"

    assert "--max_comments_count_singlenotes" in cmd2
    idx_comments = cmd2.index("--max_comments_count_singlenotes")
    assert cmd2[idx_comments + 1] == "100"


def test_api_start_with_limits():
    client = TestClient(app)
    with patch("api.routers.crawler.crawler_manager.start_crawler", new_callable=AsyncMock) as mock_start:
        mock_start.return_value = True
        response = client.post(
            "/api/crawler/start",
            json={
                "platform": "xhs",
                "login_type": "qrcode",
                "crawler_type": "search",
                "keywords": "test",
                "crawler_max_notes_count": 10,
                "max_comments_count_singlenotes": 5,
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_start.assert_called_once()
        req_arg = mock_start.call_args[0][0]
        assert req_arg.crawler_max_notes_count == 10
        assert req_arg.max_comments_count_singlenotes == 5
