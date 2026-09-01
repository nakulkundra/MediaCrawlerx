# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/test/test_redis_cache.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Unit tests for RedisCache
"""

import time
import unittest
from cache.redis_cache import RedisCache


class TestRedisCache(unittest.TestCase):
    def setUp(self):
        try:
            self.cache = RedisCache()
            self.redis_available = True
        except Exception:
            self.redis_available = False

    def test_set_and_get(self):
        if not self.redis_available:
            self.skipTest("Redis server not available")
        self.cache.set("test_key", "test_value", ttl=10)
        self.assertEqual(self.cache.get("test_key"), "test_value")

    def test_delete(self):
        if not self.redis_available:
            self.skipTest("Redis server not available")
        self.cache.set("test_key_del", "val", ttl=10)
        self.cache.delete("test_key_del")
        self.assertIsNone(self.cache.get("test_key_del"))


if __name__ == "__main__":
    unittest.main()
