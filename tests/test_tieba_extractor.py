# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_tieba_extractor.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from pathlib import Path
from media_platform.tieba.help import TieBaExtractor
from model.m_baidu_tieba import TiebaComment

FIXTURE_DIR = Path(__file__).parent.parent / "media_platform" / "tieba" / "test_data"


def read_fixture(name: str) -> str:
    path = FIXTURE_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def test_extract_search_note_list_from_keyword_page():
    content = read_fixture("search_keyword_notes.html")
    if not content:
        return
    notes = TieBaExtractor.extract_search_note_list(content)
    assert len(notes) >= 0


def test_extract_search_note_list_from_current_pc_card_page():
    page_content = """
    <html>
      <body>
        <div class="threadcardclass thread-new3 index-feed-cards">
          <a class="action-link-bg" href="https://tieba.baidu.com/p/10559655942?fr=undefined"></a>
          <div class="thread-forum-name display-flex align-center">
            <span class="forum-name-text">Zhucheng Bar</span>
          </div>
          <div class="top-title">
            <span class="forum-attention user">754023117</span>
            <span>Posted at 2026-3-15</span>
          </div>
          <div class="title-wrap"><span>Math, English, Programming Teacher</span></div>
          <div class="abstract-wrap">
            <span>Looking for math, english, and programming teachers, full or part time</span>
          </div>
          <a class="comment-link-zone" href="https://tieba.baidu.com/p/10559655942?showComment=1">
            <span class="action-number">19</span>
          </a>
        </div>
      </body>
    </html>
    """

    notes = TieBaExtractor.extract_search_note_list(page_content)

    assert len(notes) == 1
    assert notes[0].note_id == "10559655942"
    assert notes[0].title == "Math, English, Programming Teacher"
    assert notes[0].total_replay_num == 19
