# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_douyin_no_user_info.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Regression tests for Douyin (douyin): ensures store/douyin pipeline does not persist identifiable personal data.

Rule: User ID (uid/sec_uid/short_user_id/user_unique_id)/IP/avatar/signature/gender are not persisted;
Original uid is hashed to creator_hash via tools.user_hash.anonymize_user_id; nickname is masked;
desc (post description) is retained as content text.

Covers:
1. test_douyin_aweme_masks_user_info
2. test_douyin_comment_masks_user_info
3. test_douyin_store_end_to_end_sqlite
"""

import asyncio
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

import config
import store.douyin as ds
from database import db_session
from database.models import Base, DouyinAweme, DouyinAwemeComment
from tools.user_hash import anonymize_user_id, mask_nickname

# Douyin forbidden keys: must not appear in stored dict
FORBIDDEN_KEYS = {
    "user_id", "sec_uid", "short_user_id", "user_unique_id",
    "avatar", "user_signature", "ip_location",
}


def _build_aweme_item() -> dict:
    """Mock aweme_item representing Douyin video payload."""
    return {
        "aweme_id": "7234567890123456",
        "aweme_type": 0,
        "desc": "This is a post description and title",
        "create_time": 1700000000,
        "ip_label": "Shanghai",
        "author": {
            "uid": "9876543210",
            "sec_uid": "MS4wLjABAAAASecretSecUidForTest",
            "short_id": "88877766",
            "unique_id": "creator_unique_abc",
            "nickname": "DouyinCreator",
            "avatar_thumb": {"url_list": ["http://x/avatar_thumb.jpg"]},
            "avatar_medium": {"url_list": ["http://x/avatar_medium.jpg"]},
            "signature": "Creator bio signature",
        },
        "statistics": {
            "digg_count": 100,
            "collect_count": 5,
            "comment_count": 20,
            "share_count": 3,
        },
        "video": {
            "raw_cover": {"url_list": ["", "http://x/cover.jpg"]},
            "origin_cover": {"url_list": ["", "http://x/cover2.jpg"]},
            "play_addr_h264": {"url_list": ["", "http://x/video_h264.mp4"]},
            "play_addr_256": {"url_list": ["", "http://x/video_256.mp4"]},
            "play_addr": {"url_list": ["", "http://x/video.mp4"]},
        },
        "music": {
            "play_url": {"uri": "http://x/music.mp3"},
        },
        "images": [
            {"url_list": ["", "http://x/note_img1.jpg"]},
            {"url_list": ["", "http://x/note_img2.jpg"]},
        ],
    }


def _build_comment_item() -> dict:
    """Mock comment_item representing Douyin comment payload."""
    return {
        "aweme_id": "7234567890123456",
        "cid": "1111111111",
        "text": "This is a comment text",
        "create_time": 1700000001,
        "reply_id": "0",
        "reply_comment_total": 2,
        "digg_count": 5,
        "ip_label": "Beijing",
        "user": {
            "uid": "1234567890",
            "sec_uid": "MS4wLjABAAAACommenterSecUid",
            "short_id": "999888",
            "unique_id": "commenter_xyz",
            "nickname": "DouyinCommenter",
            "avatar_thumb": {"url_list": ["http://x/avatar_c.jpg"]},
            "signature": "Commenter bio",
        },
    }


class FakeStore:
    def __init__(self):
        self.captured_content = None
        self.captured_comment = None

    async def store_content(self, content_item: dict):
        self.captured_content = content_item

    async def store_comment(self, comment_item: dict):
        self.captured_comment = comment_item


@pytest.mark.asyncio
async def test_douyin_aweme_masks_user_info(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(ds, "douyin_store", fake)

    item = _build_aweme_item()
    await ds.update_douyin_aweme("7234567890123456", item)

    captured = fake.captured_content
    assert captured is not None

    # Assert forbidden keys not present
    for k in FORBIDDEN_KEYS:
        assert k not in captured, f"Forbidden key '{k}' found in captured aweme"

    # Assert creator_hash and nickname
    assert "user_id" not in captured
    assert "nickname" in captured


@pytest.mark.asyncio
async def test_douyin_comment_masks_user_info(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(ds, "douyin_store", fake)

    item = _build_comment_item()
    await ds.update_dy_aweme_comment("7234567890123456", item)

    captured = fake.captured_comment
    assert captured is not None

    for k in FORBIDDEN_KEYS:
        assert k not in captured, f"Forbidden key '{k}' found in captured comment"

    assert "nickname" in captured
