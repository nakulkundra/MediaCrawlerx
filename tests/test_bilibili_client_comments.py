# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_bilibili_client_comments.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Regression test for Bilibili client comments: ensures pinned comments and sub-replies are fetched without duplicates.

Covers:
1. When top/top_replies overlap with replies, pinned comments are called back once and trigger sub-reply extraction.
2. Compatibility with different top comment API payload structures.
"""

import pytest
from media_platform.bilibili.client import BilibiliClient


@pytest.mark.asyncio
async def test_video_comments_include_pinned_comment_once_and_fetch_replies():
    client = object.__new__(BilibiliClient)
    pinned = {"rpid": 193769108192, "rcount": 6}
    regular = {"rpid": 193434771680, "rcount": 0}
    callbacks = []
    sub_comment_calls = []

    async def get_video_comments(video_id, order_mode, next_page):
        return {
            "cursor": {"is_end": True, "next": 0},
            "replies": [pinned.copy(), regular],
            "top": {"upper": pinned},
            "top_replies": [pinned],
        }

    async def get_video_all_level_two_comments(
        video_id, comment_id, order_mode, ps, crawl_interval, callback
    ):
        sub_comment_calls.append(comment_id)

    async def callback(video_id, comments):
        callbacks.append([comment["rpid"] for comment in comments])

    client.get_video_comments = get_video_comments
    client.get_video_all_level_two_comments = get_video_all_level_two_comments

    await client.get_video_all_comments(
        video_id="323112345",
        crawl_interval=0,
        is_fetch_sub_comments=True,
        callback=callback,
    )

    assert callbacks == [[pinned["rpid"], regular["rpid"]]]
    assert sub_comment_calls == [pinned["rpid"]]
