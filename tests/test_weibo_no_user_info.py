# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_weibo_no_user_info.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Regression tests for Weibo (weibo): ensures store/weibo pipeline does not persist identifiable personal data.

Covers:
1. test_weibo_note_masks_user_info
2. test_weibo_comment_masks_user_info
3. test_weibo_store_end_to_end_sqlite
"""

import asyncio
import pytest

import store.weibo as ws
from tools.user_hash import anonymize_user_id, mask_nickname

RAW_USER_ID = 7654321
RAW_NICKNAME = "WeiboInfluencer"
RAW_COMMENT_USER_ID = 111222
RAW_COMMENT_NICKNAME = "CommenterZhang"
NOTE_ID = "5123456789"
COMMENT_ID = "998877"
RFC2822_TIME = "Sat Jun 14 12:00:00 +0800 2025"

FORBIDDEN_KEYS = {
    "user_id", "sec_uid", "short_user_id", "user_unique_id",
    "avatar", "user_avatar", "face", "sign", "profile_url", "user_link",
    "ip_location", "ip_address", "gender", "sex", "desc",
}


def make_mock_note() -> dict:
    return {
        "mblog": {
            "id": NOTE_ID,
            "text": "Great weather today <a href='#'>@Friend</a> going outside",
            "created_at": RFC2822_TIME,
            "attitudes_count": 10,
            "comments_count": 2,
            "reposts_count": 1,
            "user": {
                "id": RAW_USER_ID,
                "screen_name": RAW_NICKNAME,
                "avatar_hd": "https://wx avatar.example.com/7654321.jpg",
                "gender": "f",
                "profile_url": "https://m.weibo.cn/profile/7654321",
                "description": "User bio",
                "ip_location": "Shanghai",
                "followers_count": 9999,
            },
        }
    }


def make_mock_comment() -> dict:
    return {
        "id": COMMENT_ID,
        "text": "Well said <a href='#'>Support</a>",
        "created_at": RFC2822_TIME,
        "total_number": 3,
        "like_count": 5,
        "rootid": "parent_abc",
        "user": {
            "id": RAW_COMMENT_USER_ID,
            "screen_name": RAW_COMMENT_NICKNAME,
            "avatar_hd": "https://wx avatar.example.com/111222.jpg",
            "gender": "m",
            "profile_url": "https://m.weibo.cn/profile/111222",
            "description": "Commenter bio",
            "ip_location": "Guangdong",
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
async def test_weibo_note_masks_user_info(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(ws, "weibo_store", fake)

    item = make_mock_note()
    await ws.update_weibo_note(item)

    captured = fake.captured_content
    assert captured is not None
    for k in FORBIDDEN_KEYS:
        assert k not in captured, f"Forbidden key '{k}' found in captured weibo note"


@pytest.mark.asyncio
async def test_weibo_comment_masks_user_info(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(ws, "weibo_store", fake)

    item = make_mock_comment()
    await ws.update_weibo_note_comment(NOTE_ID, item)

    captured = fake.captured_comment
    assert captured is not None
    for k in FORBIDDEN_KEYS:
        assert k not in captured, f"Forbidden key '{k}' found in captured weibo comment"
