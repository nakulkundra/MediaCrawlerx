# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/xhs/extractor.py
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

import json
import re
from typing import Dict, Optional

import humps


class XiaoHongShuExtractor:
    def __init__(self):
        pass

    def extract_note_detail_from_html(self, note_id: str, html: str) -> Optional[Dict]:
        """Extract note details from HTML

        Args:
            note_id (str): Note ID
            html (str): HTML string

        Returns:
            Dict: Note details dictionary
        """
        if not html:
            return None
        match = re.search(r'<script>window\.__INITIAL_STATE__\s*=\s*(.*?)</script>', html, re.DOTALL)
        if match:
            raw_json = match.group(1).replace(":undefined", ":null")
            try:
                state = json.loads(raw_json)
                note_data = state.get("note", {}).get("noteDetailMap", {}).get(note_id, {})
                if note_data:
                    return note_data.get("note")
            except Exception:
                pass
        return None
