# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/model/m_douyin.py
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


class VideoUrlInfo(BaseModel):
    """Douyin video URL information"""
    aweme_id: str = Field(title="aweme id (video id)")
    url_type: str = Field(default="normal", title="url type: normal, short, modal")


class CreatorUrlInfo(BaseModel):
    """Douyin creator URL information"""
    sec_user_id: str = Field(title="sec_user_id (creator id)")
