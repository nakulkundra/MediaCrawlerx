# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/xhs/playwright_sign.py
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

# Xiaohongshu signature generation using xhshow pure-algorithm library
#
# Acknowledgements: This signature implementation depends on the xhshow open source library, provided by Cloxl
# Repository URL: https://github.com/Cloxl/xhshow
# License: MIT License
#
# Requires xhshow>=0.2.0: This version natively fixes the bug in a3_hash calculation for GET requests
# (https://github.com/Cloxl/xhshow/issues/104), monkey-patch is no longer needed locally.

from typing import Any, Dict, Optional, Union

try:
    from xhshow import Xhshow
except ImportError:
    Xhshow = None

from .xhs_sign import get_trace_id

_xhshow_client: Optional[Any] = None


def _get_xhshow_client():
    global _xhshow_client
    if _xhshow_client is None and Xhshow is not None:
        _xhshow_client = Xhshow()
    return _xhshow_client


def sign_with_xhshow(
    uri: str,
    data: Optional[Union[Dict, str]] = None,
    a1: str = "",
    web_session: str = "",
) -> Dict[str, str]:
    """
    Generate signature headers using xhshow library
    """
    client = _get_xhshow_client()
    if not client:
        return {
            "x-s": "",
            "x-t": "",
            "x-s-common": "",
            "x-b3-traceid": get_trace_id(),
        }

    cookies = {
        "a1": a1,
        "web_session": web_session,
    }
    if isinstance(data, dict):
        sign_headers = client.sign_headers_post(uri=uri, cookies=cookies, data=data)
    else:
        sign_headers = client.sign_headers_get(uri=uri, cookies=cookies, params=data)

    return {
        "x-s": sign_headers.get("x-s", ""),
        "x-t": str(sign_headers.get("x-t", "")),
        "x-s-common": sign_headers.get("x-s-common", ""),
        "x-b3-traceid": sign_headers.get("x-b3-traceid", get_trace_id()),
    }
