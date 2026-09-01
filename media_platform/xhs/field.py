# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/xhs/field.py
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


class FeedType(Enum):
    # Recommend
    RECOMMEND = "homefeed_recommend"
    # Fashion
    FASION = "homefeed.fashion_v3"
    # Food
    FOOD = "homefeed.food_v3"
    # Cosmetics
    COSMETICS = "homefeed.cosmetics_v3"
    # Movie and TV
    MOVIE = "homefeed.movie_and_tv_v3"
    # Career
    CAREER = "homefeed.career_v3"
    # Emotion
    EMOTION = "homefeed.love_v3"
    # House
    HOURSE = "homefeed.house_v3"
    # Game
    GAME = "homefeed.gaming_v3"
    # Travel
    TRAVEL = "homefeed.travel_v3"
    # Fitness
    FITNESS = "homefeed.fitness_v3"


class NoteType(Enum):
    NORMAL = "normal"
    VIDEO = "video"


class SearchSortType(Enum):
    """search sort type"""
    # General
    GENERAL = "general"
    # Most popular
    MOST_POPULAR = "popularity_descending"
    # Latest
    LATEST = "time_descending"


class SearchNoteType(Enum):
    """search note type"""
    # All
    ALL = 0
    # Video
    VIDEO = 1
    # Image
    IMAGE = 2


class NoteChannel(NamedTuple):
    type: FeedType
    name: str
