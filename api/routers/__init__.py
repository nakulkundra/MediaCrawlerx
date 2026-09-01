# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/api/routers/__init__.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# Disclaimer: This code is for learning and research purposes only. Users should comply with the following principles:
# 1. Do not use for any commercial purposes.
# 2. Comply with the target platform's terms of service and robots.txt rules when using.
# 3. Do not conduct large-scale scraping or cause operational disruption to the platform.
# 4. Request frequency should be reasonably controlled to avoid placing unnecessary burden on the target platform.
# 5. Do not use for any illegal or improper purposes.
#
# For detailed license terms, please refer to the LICENSE file in the project root directory.
# Using this code indicates that you agree to abide by the above principles and all terms in the LICENSE.

from .crawler import router as crawler_router
from .data import router as data_router
from .websocket import router as websocket_router

__all__ = ["crawler_router", "data_router", "websocket_router"]
