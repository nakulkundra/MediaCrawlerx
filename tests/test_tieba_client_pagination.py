# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_tieba_client_pagination.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import pytest
from media_platform.tieba.client import BaiduTieBaClient
from model.m_baidu_tieba import TiebaComment, TiebaNote


class DummyPage:
    url = "https://tieba.baidu.com/"


@pytest.mark.asyncio
async def test_search_uses_requested_page_number():
    client = BaiduTieBaClient(playwright_page=DummyPage())
    calls = []

    async def fake_fetch(uri, method="GET", params=None, data=None, use_sign=False):
        calls.append((uri, params))
        return {"no": 0, "data": {"card_list": []}}

    client._fetch_json_by_browser = fake_fetch

    await client.get_notes_by_keyword("programming", page=2, page_size=10)

    assert calls[0][0] == "/mo/q/search/multsearch"
    assert calls[0][1]["pn"] == 2


@pytest.mark.asyncio
async def test_comments_walk_pages_until_total_reply_page():
    client = BaiduTieBaClient(playwright_page=DummyPage())
    pages = []
    note = TiebaNote(
        note_id="9835114923",
        title="title",
        note_url="https://tieba.baidu.com/p/9835114923",
        tieba_name="MachiningBar",
        tieba_link="https://tieba.baidu.com/f?kw=machining",
        total_replay_page=2,
    )

    async def fake_get_comments(note_item, page=1):
        pages.append(page)
        return [
            TiebaComment(
                comment_id=f"comment_{page}",
                note_id=note_item.note_id,
                content=f"Comment page {page}",
            )
        ]

    client.get_comments_by_note = fake_get_comments

    collected = []
    async def cb(note_id, comments):
        collected.extend(comments)

    await client.get_note_all_comments(note, callback=cb)

    assert pages == [1, 2]
    assert len(collected) == 2
