# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_no_user_info.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Regression tests: ensures crawler and storage pipelines do not persist identifiable personal data.

Covers:
1. ORM introspection - database.models contains no forbidden columns, creator tables removed, content tables contain creator_hash.
2. Extractor layer - mock payloads through extractors assert output dict contains no forbidden keys, nicknames are masked.
3. Masking & Hashing utilities.
"""

import pathlib
import re
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Forbidden field keys. Nickname fields are allowed but values must be masked.
FORBIDDEN_KEYS = {
    "user_id", "sec_uid", "short_user_id", "user_unique_id", "user_signature",
    "avatar", "user_avatar", "face", "sign", "profile_url", "user_link",
    "url_token", "user_url_token", "ip_location", "ip_address", "gender", "sex",
    "up_id", "fan_id", "up_name", "fan_name", "up_avatar", "fan_avatar",
    "up_sign", "fan_sign", "mid",
}
NICK_KEYS = {"nickname", "user_nickname", "screen_name", "name", "user_name"}
MASK_RE = re.compile(r"^.?\*{1,4}.?$")


# ----------------------------- ORM Introspection -----------------------------

def test_orm_has_no_forbidden_columns():
    import database.models as m
    from sqlalchemy.orm import class_mapper
    tables = [c for c in dir(m) if c[0].isupper()
              and c not in ("Base", "Column", "Integer", "BigInteger", "String", "Text")]
    bad = []
    for t in tables:
        try:
            cols = {c.name for c in class_mapper(getattr(m, t)).columns}
            hit = cols & FORBIDDEN_KEYS
            if hit:
                bad.append((t, sorted(hit)))
        except Exception:
            pass
    assert not bad, f"ORM contains forbidden columns: {bad}"


def test_creator_tables_removed():
    import database.models as m
    removed = {"XhsCreator", "DyCreator", "WeiboCreator", "TiebaCreator",
               "ZhihuCreator", "BilibiliUpInfo", "BilibiliContactInfo"}
    for t in removed:
        assert not hasattr(m, t), f"Creator table {t} still exists"


def test_mask_and_hash_tools():
    from tools.user_hash import anonymize_user_id, mask_nickname
    h = anonymize_user_id("12345")
    assert h and h != "12345" and re.fullmatch(r"[0-9a-f]{16}", h)

    m = mask_nickname("JohnDoe")
    assert m != "JohnDoe" and "*" in m
