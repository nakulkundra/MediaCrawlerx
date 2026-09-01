# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/conftest.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Pytest configuration and shared fixtures
"""

import sys
from pathlib import Path
import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """Return project root path"""
    return project_root


@pytest.fixture
def sample_xhs_note():
    """Sample Xiaohongshu note data for testing"""
    return {
        "note_id": "test_note_123",
        "type": "normal",
        "title": "Test Title",
        "desc": "This is a test note description",
        "user_id": "test_user_456",
        "nickname": "TestUser",
        "liked_count": 100,
        "collected_count": 50,
        "comment_count": 20,
        "share_count": 5,
        "ip_location": "Beijing",
        "image_list": "http://example.com/img1.jpg,http://example.com/img2.jpg",
        "tag_list": "tag1,tag2",
        "note_url": "https://www.xiaohongshu.com/explore/test_note_123",
    }


@pytest.fixture
def sample_comment():
    """Sample comment data for testing"""
    return {
        "comment_id": "comment_123",
        "note_id": "test_note_123",
        "content": "Test comment content",
        "user_id": "user_789",
        "nickname": "Commenter",
        "like_count": 10,
        "create_time": 1700000000,
        "ip_location": "Shanghai",
    }
