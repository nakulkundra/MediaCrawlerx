# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/zhihu/field.py
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
from typing import NamedTuple

from constant import zhihu as zhihu_constant


class SearchTime(Enum):
    """
    Search time range
    """
    DEFAULT = ""  # No time limit
    ONE_DAY = "a_day"
    ONE_WEEK = "a_week"
    ONE_MONTH = "a_month"
    THREE_MONTHS = "three_months"
    HALF_YEAR = "half_a_year"
    ONE_YEAR = "a_year"


class SearchSort(Enum):
    """
    Search sort type
    """
    DEFAULT = "default"  # Comprehensive sort
    TIME_DESC = "updated_time"  # Real-time sort (by update time)


class SearchType(Enum):
    """
    Search content type
    """
    ALL = "general"
    ARTICLE = zhihu_constant.ARTICLE_NAME
    ANSWER = zhihu_constant.ANSWER_NAME
    ZVIDEO = zhihu_constant.VIDEO_NAME
