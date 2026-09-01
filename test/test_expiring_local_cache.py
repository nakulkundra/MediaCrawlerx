# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/test/test_expiring_local_cache.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Unit tests for ExpiringLocalCache
"""

import time
import unittest
from cache.local_cache import ExpiringLocalCache


class TestExpiringLocalCache(unittest.TestCase):
    def setUp(self):
        self.cache = ExpiringLocalCache(maxsize=10, default_ttl=2)

    def test_set_and_get(self):
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")

    def test_expiration(self):
        self.cache.set("key2", "value2", ttl=1)
        self.assertEqual(self.cache.get("key2"), "value2")
        time.sleep(1.2)
        self.assertIsNone(self.cache.get("key2"))

    def test_delete(self):
        self.cache.set("key3", "value3")
        self.cache.delete("key3")
        self.assertIsNone(self.cache.get("key3"))

    def test_keys(self):
        self.cache.set("k1", "v1")
        self.cache.set("k2", "v2")
        self.assertIn("k1", self.cache.keys())
        self.assertIn("k2", self.cache.keys())


if __name__ == "__main__":
    unittest.main()
