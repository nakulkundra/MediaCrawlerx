# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_static_proxy_provider.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import pytest
import config
from proxy.proxy_ip_pool import StaticProxyProvider, create_ip_pool
from proxy.types import ProviderNameEnum


def test_default_proxy_provider_remains_existing_provider():
    assert config.IP_PROXY_PROVIDER_NAME == ProviderNameEnum.KUAI_DAILI_PROVIDER.value
    assert config.IP_PROXY_POOL_COUNT == 2
    assert config.STATIC_PROXY_URL == ""


@pytest.mark.asyncio
async def test_static_proxy_provider_parses_proxy_url(monkeypatch):
    monkeypatch.setattr(config, "STATIC_PROXY_URL", "http://user:p%40ss@example.com:8080")

    proxies = await StaticProxyProvider().get_proxies(count=1)

    assert len(proxies) == 1
    proxy = proxies[0]
    assert proxy.ip == "example.com"
    assert proxy.port == 8080
    assert proxy.user == "user"
    assert proxy.password == "p@ss"
    assert proxy.protocol == "http"
