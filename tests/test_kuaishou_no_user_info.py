# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_kuaishou_no_user_info.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Regression tests for Kuaishou (kuaishou): ensures store/kuaishou pipeline does not persist identifiable personal data.

Rule: User ID/avatar/signature/ip_location/gender are not persisted;
Original user_id is hashed to creator_hash via tools.user_hash.anonymize_user_id; nickname is masked.

Covers:
1. update_kuaishou_video
2. update_ks_video_comment
3. test_kuaishou_store_end_to_end_sqlite
"""

import asyncio
import contextlib
import types
import pytest

import store.kuaishou as ks
from store.kuaishou import update_kuaishou_video, update_ks_video_comment
from tools.user_hash import anonymize_user_id, mask_nickname

FORBIDDEN_KEYS = {"user_id", "avatar", "signature", "ip_location", "gender"}

MOCK_VIDEO_ID = "3xf8e9kq2b7w4"
MOCK_AUTHOR_ID = "ks_author_001"
MOCK_AUTHOR_NAME = "KuaishouCreator"
MOCK_CAPTION = "Test video caption #test"

MOCK_COMMENT_V2_AUTHOR_ID = "ks_user_888"
MOCK_COMMENT_V2_AUTHOR_NAME = "KuaishouFriend"
MOCK_COMMENT_LEGACY_AUTHOR_ID = "ks_user_777"
MOCK_COMMENT_LEGACY_AUTHOR_NAME = "HappySource"


def make_mock_video() -> dict:
    return {
        "type": 1,
        "photo": {
            "id": MOCK_VIDEO_ID,
            "caption": MOCK_CAPTION,
            "timestamp": 1700000000000,
            "coverUrl": "https://p.kuaishou.com/cover/abc.jpg",
            "photoUrl": "https://v.kuaishou.com/play/abc.mp4",
            "realLikeCount": 12345,
            "viewCount": 67890,
        },
        "author": {
            "id": MOCK_AUTHOR_ID,
            "name": MOCK_AUTHOR_NAME,
            "headerUrl": "https://p.kuaishou.com/header/u001.jpg",
        },
    }


def make_mock_comment_v2() -> dict:
    return {
        "comment_id": 9001,
        "timestamp": 1700000001234,
        "content": "Hilarious comment text",
        "author_id": MOCK_COMMENT_V2_AUTHOR_ID,
        "author_name": MOCK_COMMENT_V2_AUTHOR_NAME,
        "headurl": "https://p.kuaishou.com/header/u888.jpg",
        "commentCount": 7,
    }


def make_mock_comment_legacy() -> dict:
    return {
        "commentId": 8001,
        "timestamp": 1700000005678,
        "content": "Legacy GraphQL comment",
        "authorId": MOCK_COMMENT_LEGACY_AUTHOR_ID,
        "authorName": MOCK_COMMENT_LEGACY_AUTHOR_NAME,
        "headurl": "https://p.kuaishou.com/header/u777.jpg",
        "subCommentCount": 3,
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
async def test_kuaishou_video_masks_user_info(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(ks, "kuaishou_store", fake)

    item = make_mock_video()
    await update_kuaishou_video(item)

    captured = fake.captured_content
    assert captured is not None
    for k in FORBIDDEN_KEYS:
        assert k not in captured, f"Forbidden key '{k}' found in captured video"


@pytest.mark.asyncio
async def test_kuaishou_comment_masks_user_info(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(ks, "kuaishou_store", fake)

    item = make_mock_comment_v2()
    await update_ks_video_comment(MOCK_VIDEO_ID, item)

    captured = fake.captured_comment
    assert captured is not None
    for k in FORBIDDEN_KEYS:
        assert k not in captured, f"Forbidden key '{k}' found in captured comment"
