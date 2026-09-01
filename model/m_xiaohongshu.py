# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/model/m_xiaohongshu.py
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

from pydantic import BaseModel, Field


class NoteUrlInfo(BaseModel):
    note_id: str = Field(title="note id")
    xsec_token: str = Field(title="xsec token")
    xsec_source: str = Field(title="xsec source")


class CreatorUrlInfo(BaseModel):
    """Xiaohongshu creator URL information"""
    user_id: str = Field(title="user id (creator id)")
    xsec_token: str = Field(default="", title="xsec token")
    xsec_source: str = Field(default="", title="xsec source")
