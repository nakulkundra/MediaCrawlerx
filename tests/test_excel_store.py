# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_excel_store.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Unit tests for Excel export functionality
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path
import pytest

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from store.excel_store_base import ExcelStoreBase


@pytest.mark.skipif(not EXCEL_AVAILABLE, reason="openpyxl not installed")
class TestExcelStoreBase:
    """Test cases for ExcelStoreBase"""

    @pytest.fixture(autouse=True)
    def clear_singleton_state(self):
        """Clear singleton state before and after each test"""
        ExcelStoreBase._instances.clear()
        yield
        ExcelStoreBase._instances.clear()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def excel_store(self, temp_dir, monkeypatch):
        """Create ExcelStoreBase instance for testing"""
        monkeypatch.chdir(temp_dir)
        store = ExcelStoreBase(platform="test", crawler_type="search")
        yield store

    def test_initialization(self, excel_store):
        """Test Excel store initialization"""
        assert excel_store.platform == "test"
        assert excel_store.crawler_type == "search"
        assert excel_store.workbook is not None
        assert excel_store.contents_sheet is not None
        assert excel_store.comments_sheet is not None
        assert excel_store.creators_sheet is not None

    @pytest.mark.asyncio
    async def test_store_content(self, excel_store):
        """Test storing content data"""
        content_item = {
            "note_id": "test123",
            "title": "Test Title",
            "desc": "Test Description",
            "user_id": "user456",
            "nickname": "Test User",
            "liked_count": 10,
        }
        await excel_store.store_content(content_item)
        assert excel_store.has_content is True

    @pytest.mark.asyncio
    async def test_store_comment(self, excel_store):
        """Test storing comment data"""
        comment_item = {
            "comment_id": "comm123",
            "note_id": "test123",
            "content": "Great post!",
            "user_id": "user789",
            "nickname": "Commenter",
        }
        await excel_store.store_comment(comment_item)
        assert excel_store.has_comments is True

    @pytest.mark.asyncio
    async def test_store_creator(self, excel_store):
        """Test storing creator data"""
        creator_item = {
            "user_id": "user456",
            "nickname": "Test Creator",
            "desc": "Creator Bio",
            "fans": 1000,
        }
        await excel_store.store_creator(creator_item)
        assert excel_store.has_creators is True
