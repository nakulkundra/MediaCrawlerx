# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/model/m_baidu_tieba.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# Disclaimer: This code is for educational and research purposes only. Users must adhere to the following principles:
# 1. Do not use for any commercial purposes.
# 2. Comply with the target platform's Terms of Service and robots.txt rules during use.
# 3. Do not conduct large-scale scraping or cause operational disruptions to the platform.
# 4. Reasonably control request frequencies to avoid placing unnecessary burdens on target platforms.
# 5. Do not use for any illegal or inappropriate purposes.
#
# For detailed license terms, please refer to the LICENSE file in the project root directory.
# Using this code indicates that you agree to abide by the above principles and all terms in LICENSE.

from typing import Optional
from pydantic import BaseModel, Field


class TiebaNote(BaseModel):
    """
    Baidu Tieba post
    """
    note_id: str = Field(..., description="Post ID")
    title: str = Field(..., description="Post title")
    desc: str = Field(default="", description="Post description")
    note_url: str = Field(..., description="Post link")
    publish_time: str = Field(default="", description="Publish time")
    creator_hash: str = Field(default="", description="Creator anonymous hash (original user link is not stored)")
    user_nickname: str = Field(default="", description="User nickname (masked)")
    tieba_name: str = Field(..., description="Tieba name")
    tieba_link: str = Field(..., description="Tieba link")
    total_replay_num: int = Field(default=0, description="Total reply count")
    total_replay_page: int = Field(default=0, description="Total reply pages")
    source_keyword: str = Field(default="", description="Source keyword")


class TiebaComment(BaseModel):
    """
    Baidu Tieba comment
    """
    comment_id: str = Field(..., description="Comment ID")
    parent_comment_id: str = Field(default="", description="Parent comment ID")
    content: str = Field(..., description="Comment content")
    creator_hash: str = Field(default="", description="Creator anonymous hash (original user link is not stored)")
    user_nickname: str = Field(default="", description="User nickname (masked)")
    publish_time: str = Field(default="", description="Publish time")
    sub_comment_count: int = Field(default=0, description="Sub-comment count")
    note_id: str = Field(..., description="Post ID")
    note_url: str = Field(..., description="Post link")
    tieba_id: str = Field(..., description="Tieba ID")
    tieba_name: str = Field(..., description="Tieba name")
    tieba_link: str = Field(..., description="Tieba link")


class TiebaCreator(BaseModel):
    """
    Baidu Tieba creator (Educational version: personal data is no longer persisted, only kept as in-memory object)
    """
    creator_hash: str = Field(default="", description="Creator anonymous hash (original user link is not stored)")
    user_nickname: str = Field(default="", description="User nickname (masked)")
    follows: int = Field(default=0, description="Follows count")
    fans: int = Field(default=0, description="Fans count")
    registration_duration: str = Field(default="", description="Registration duration")
