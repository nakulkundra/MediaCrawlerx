# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_store_factory.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Unit tests for Store Factory functionality
"""

from unittest.mock import MagicMock, patch
import pytest

from store.excel_store_base import ExcelStoreBase
from store.xhs import XhsStoreFactory
from store.xhs._store_impl import (
    XhsCsvStoreImplement,
    XhsDbStoreImplement,
    XhsExcelStoreImplement,
    XhsJsonStoreImplement,
    XhsJsonlStoreImplement,
    XhsMongoStoreImplement,
    XhsSqliteStoreImplement,
)


class TestXhsStoreFactory:
    """Test cases for XhsStoreFactory"""

    @patch('config.SAVE_DATA_OPTION', 'csv')
    def test_create_csv_store(self):
        store = XhsStoreFactory.create_store()
        assert isinstance(store, XhsCsvStoreImplement)

    @patch('config.SAVE_DATA_OPTION', 'json')
    def test_create_json_store(self):
        store = XhsStoreFactory.create_store()
        assert isinstance(store, XhsJsonStoreImplement)

    @patch('config.SAVE_DATA_OPTION', 'jsonl')
    def test_create_jsonl_store(self):
        store = XhsStoreFactory.create_store()
        assert isinstance(store, XhsJsonlStoreImplement)

    @patch('config.SAVE_DATA_OPTION', 'sqlite')
    def test_create_sqlite_store(self):
        store = XhsStoreFactory.create_store()
        assert isinstance(store, XhsSqliteStoreImplement)

    @patch('config.SAVE_DATA_OPTION', 'db')
    def test_create_db_store(self):
        store = XhsStoreFactory.create_store()
        assert isinstance(store, XhsDbStoreImplement)

    @patch('config.SAVE_DATA_OPTION', 'excel')
    def test_create_excel_store(self):
        store = XhsStoreFactory.create_store()
        assert isinstance(store, XhsExcelStoreImplement)
