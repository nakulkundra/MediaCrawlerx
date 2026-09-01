# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of the MediaCrawler educational edition.
# For educational and anti-harassment/doxxing purposes, scraped results do not preserve
# any personal information that could identify real persons
# (User ID, IP location, avatar, profile link, signature/bio, gender, etc. are not collected;
# nicknames are preserved but masked in the middle). This module provides anonymization and masking utilities.
import hashlib


def anonymize_user_id(user_id) -> str:
    """Converts original user ID to anonymous hash for grouping content/comments by the same creator,
    without exposing real identity. Returns sha256 truncated 16-character hexadecimal string."""
    if user_id is None:
        return ""
    s = str(user_id).strip()
    if not s:
        return ""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def mask_nickname(name) -> str:
    """Nickname middle masking: keeps 1 character at start and end, replaces middle with asterisks.
    - length <= 1: return "*"
    - length == 2: first char + "*"
    - length >= 3: first char + "***" + last char
    This preserves the semantic context needed for educational analysis while preventing identification of real individuals by nickname.
    """
    if name is None:
        return ""
    s = str(name)
    if len(s) <= 1:
        return "*"
    if len(s) == 2:
        return s[0] + "*"
    return s[0] + "***" + s[-1]
