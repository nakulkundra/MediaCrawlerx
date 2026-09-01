# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/xhs/help.py
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

import ctypes
import json
import random
import time
import urllib.parse
from urllib.parse import parse_qs, urlparse

from model.m_xiaohongshu import CreatorUrlInfo, NoteUrlInfo
from tools.crawler_util import extract_url_params_to_dict

from .xhs_sign import BASE64_CHARS, CRC32_TABLE


def get_b3_trace_id():
    re = "abcdef0123456789"
    je = 16
    e = ""
    for t in range(16):
        e += re[random.randint(0, je - 1)]
    return e


def mrc(e):
    t = 0 ^ -1
    for r in range(len(e)):
        t = (t >> 8) ^ CRC32_TABLE[(t ^ ord(e[r])) & 255]
    return ctypes.c_uint32(t ^ -1).value


def encodeUtf8(e):
    return urllib.parse.quote(e, safe="~()*!.'")


def b64Encode(e):
    chars = "".join(BASE64_CHARS)
    res = []
    i = 0
    while i < len(e):
        c1 = ord(e[i]) if i < len(e) else 0
        c2 = ord(e[i + 1]) if i + 1 < len(e) else 0
        c3 = ord(e[i + 2]) if i + 2 < len(e) else 0

        e1 = c1 >> 2
        e2 = ((c1 & 3) << 4) | (c2 >> 4)
        e3 = ((c2 & 15) << 2) | (c3 >> 6)
        e4 = c3 & 63

        if i + 1 >= len(e):
            e3 = 64
            e4 = 64
        elif i + 2 >= len(e):
            e4 = 64

        res.append(chars[e1])
        res.append(chars[e2])
        if e3 < 64:
            res.append(chars[e3])
        else:
            res.append("=")
        if e4 < 64:
            res.append(chars[e4])
        else:
            res.append("=")
        i += 3
    return "".join(res)


def sign(a1="", b1="", x_s="", x_t=""):
    """
    takes in a URI (uniform resource identifier), an optional data dictionary, and an optional ctime parameter. It returns a dictionary containing two keys: "x-s" and "x-t".
    """
    common = {
        "s0": 3,  # getPlatformCode
        "s1": "",
        "x0": "1",  # localStorage.getItem("b1b1")
        "x1": "4.2.2",  # version
        "x2": "Mac OS",
        "x3": "xhs-pc-web",
        "x4": "4.74.0",
        "x5": a1,  # cookie of a1
        "x6": x_t,
        "x7": x_s,
        "x8": b1,  # localStorage.getItem("b1")
        "x9": mrc(x_t + x_s + b1),
        "x10": 154,  # getSigCount
        "x11": "normal",
    }
    encode_str = encodeUtf8(json.dumps(common, separators=(',', ':')))
    x_s_common = b64Encode(encode_str)
    x_b3_traceid = get_b3_trace_id()
    return {
        "x-s": x_s,
        "x-t": x_t,
        "x-s-common": x_s_common,
        "x-b3-traceid": x_b3_traceid,
    }


def parse_video_info_from_url(url: str) -> NoteUrlInfo:
    """
    parse video info from url
    :param url:
    :return:
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    note_id = path_parts[-1] if path_parts else ""
    xsec_token = parse_qs(parsed_url.query).get("xsec_token", [""])[0]
    return NoteUrlInfo(
        note_id=note_id,
        xsec_token=xsec_token,
    )


def parse_note_info_from_note_url(url: str) -> NoteUrlInfo:
    """
    parse note info from note url
    :param url:
    :return:
    """
    return parse_video_info_from_url(url)


def parse_creator_info_from_url(url: str) -> CreatorUrlInfo:
    """
    parse creator info from url
    :param url:
    :return:
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    user_id = path_parts[-1] if path_parts else ""
    xsec_token = parse_qs(parsed_url.query).get("xsec_token", [""])[0]
    return CreatorUrlInfo(
        user_id=user_id,
        xsec_token=xsec_token,
    )


def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
    base36 = ''
    sign_prefix = ''
    if number < 0:
        sign_prefix = '-'
        number = -number
    if 0 <= number < len(alphabet):
        return sign_prefix + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign_prefix + base36


def get_search_id():
    e = int(time.time() * 1000) << 64
    t = int(random.uniform(0, 2147483646))
    return base36encode((e + t))
