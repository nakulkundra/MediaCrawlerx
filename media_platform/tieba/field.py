# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/tieba/field.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# Statement: This code is for learning and research purposes only. Users should abide by the following principles:
# 1. Shall not be used for any commercial purposes.
# 2. When using, please abide by the terms of use and robots.txt rules of the target platform.
# 3. Do not conduct large-scale crawling or disrupt platform operations.
# 4. Request frequency should be reasonably controlled to avoid placing unnecessary burden on the target platform.
# 5. Must not be used for any illegal or improper purposes.
#
# For detailed license terms, please refer to the LICENSE file in the project root directory.
# Using this code indicates that you agree to abide by the above principles and all terms in the LICENSE.

from enum import Enum


class SearchSortType(Enum):
    """search sort type"""
    # Sort by time in descending order
    TIME_DESC = "1"
    # Sort by time in ascending order
    TIME_ASC = "0"
    # Sort by relevance
    RELEVANCE_ORDER = "2"


class SearchNoteType(Enum):
    # Only view main posts
    MAIN_THREAD = "1"
    # Mixed mode (posts + replies)
    FIXED_THREAD = "0"
