# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/test/test_proxy_ip_pool.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Unit tests for ProxyIpPool and IP expiration logic
"""

import time
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from proxy.proxy_ip_pool import ProxyIpPool, create_ip_pool
from proxy.types import IpInfoModel


class TestIpPool(IsolatedAsyncioTestCase):
    async def test_ip_pool(self):
        pool = await create_ip_pool(ip_pool_count=1, enable_validate_ip=True)
        for _ in range(3):
            ip_proxy_info: IpInfoModel = await pool.get_proxy()
            self.assertIsNotNone(ip_proxy_info.ip, msg="Verify if IP is obtained successfully")

    async def test_ip_expiration(self):
        """Test IP proxy expiration detection functionality"""
        pool = await create_ip_pool(ip_pool_count=2, enable_validate_ip=True)
        ip_proxy_info: IpInfoModel = await pool.get_proxy()

        if ip_proxy_info.expired_time_ts:
            is_expired = ip_proxy_info.is_expired(buffer_seconds=30)
            self.assertFalse(is_expired, msg="Newly obtained IP should not be expired")

        current_ts = int(time.time())
        five_minutes_later = current_ts + 300
        ip_proxy_info.expired_time_ts = five_minutes_later

        is_expired_30s = ip_proxy_info.is_expired(buffer_seconds=30)
        self.assertFalse(is_expired_30s)

        ip_proxy_info.expired_time_ts = current_ts + 10
        is_expired_soon = ip_proxy_info.is_expired(buffer_seconds=30)
        self.assertTrue(is_expired_soon)
