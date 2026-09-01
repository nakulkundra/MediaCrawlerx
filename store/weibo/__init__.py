# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/store/weibo/__init__.py
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

# -*- coding: utf-8 -*-
# @Author  : relakkes@gmail.com
# @Time    : 2024/1/14 21:34
# @Desc    :

import re
from typing import List, Dict

from tools.user_hash import anonymize_user_id, mask_nickname
from var import source_keyword_var

from .weibo_store_media import *
from ._store_impl import *


class WeibostoreFactory:
    STORES = {
        "csv": WeiboCsvStoreImplement,
        "db": WeiboDbStoreImplement,
        "postgres": WeiboDbStoreImplement,
        "json": WeiboJsonStoreImplement,
        "jsonl": WeiboJsonlStoreImplement,
        "sqlite": WeiboSqliteStoreImplement,
        "mongodb": WeiboMongoStoreImplement,
        "excel": WeiboExcelStoreImplement,
    }

    @staticmethod
    def create_store() -> AbstractStore:
        store_class = WeibostoreFactory.STORES.get(config.SAVE_DATA_OPTION)
        if not store_class:
            raise ValueError("[WeibostoreFactory.create_store] Invalid save option only supported csv or db or json or sqlite or mongodb or excel ...")
        return store_class()


async def batch_update_weibo_notes(note_list: List[Dict]):
    """
    Batch update weibo notes
    Args:
        note_list:

    Returns:

    """
    if not note_list:
        return
    for note_item in note_list:
        await update_weibo_note(note_item)


async def update_weibo_note(note_item: Dict):
    """
    Update weibo note
    Args:
        note_item:

    Returns:

    """
    if not note_item:
        return

    mblog: Dict = note_item.get("mblog") or {}
    user_info: Dict = mblog.get("user") or {}
    note_id = mblog.get("id")
    content_text = mblog.get("text")
    clean_text = re.sub(r"<.*?>", "", content_text)
    # Educational version: Original user_id anonymized to creator_hash, nickname masked;
    # Does not collect avatar/homepage link/gender/IP location and other information that can identify real people.
    save_content_item = {
        # Weibo information
        "note_id": note_id,
        "content": clean_text,
        "create_time": utils.rfc2822_to_timestamp(mblog.get("created_at")),
        "create_date_time": str(utils.rfc2822_to_china_datetime(mblog.get("created_at"))),
        "liked_count": str(mblog.get("attitudes_count", 0)),
        "comments_count": str(mblog.get("comments_count", 0)),
        "shared_count": str(mblog.get("reposts_count", 0)),
        "last_modify_ts": utils.get_current_timestamp(),
        "note_url": f"https://m.weibo.cn/detail/{note_id}",

        # Creator information (anonymized/masked, does not include original user_id/avatar/gender/profile_url/ip_location)
        "creator_hash": anonymize_user_id(user_info.get("id")),
        "nickname": mask_nickname(user_info.get("screen_name", "")),
        "source_keyword": source_keyword_var.get(),
    }
    utils.logger.info(f"[store.weibo.update_weibo_note] weibo note id:{note_id}, title:{save_content_item.get('content')[:24]} ...")
    await WeibostoreFactory.create_store().store_content(content_item=save_content_item)


async def batch_update_weibo_note_comments(note_id: str, comments: List[Dict]):
    """
    Batch update weibo note comments
    Args:
        note_id:
        comments:

    Returns:

    """
    if not comments:
        return
    for comment_item in comments:
        await update_weibo_note_comment(note_id, comment_item)


async def update_weibo_note_comment(note_id: str, comment_item: Dict):
    """
    Update weibo note comment
    Args:
        note_id: weibo note id
        comment_item: weibo comment item

    Returns:

    """
    if not comment_item or not note_id:
        return
    comment_id = str(comment_item.get("id"))
    user_info: Dict = comment_item.get("user") or {}
    content_text = comment_item.get("text")
    clean_text = re.sub(r"<.*?>", "", content_text)
    # Educational version: Original user_id anonymized to creator_hash, nickname masked;
    # Does not collect avatar/homepage link/gender/IP location and other information that can identify real people.
    save_comment_item = {
        "comment_id": comment_id,
        "create_time": utils.rfc2822_to_timestamp(comment_item.get("created_at")),
        "create_date_time": str(utils.rfc2822_to_china_datetime(comment_item.get("created_at"))),
        "note_id": note_id,
        "content": clean_text,
        "sub_comment_count": str(comment_item.get("total_number", 0)),
        "comment_like_count": str(comment_item.get("like_count", 0)),
        "last_modify_ts": utils.get_current_timestamp(),
        "parent_comment_id": comment_item.get("rootid", ""),

        # Creator information (anonymized/masked, does not include original user_id/avatar/gender/profile_url/ip_location)
        "creator_hash": anonymize_user_id(user_info.get("id")),
        "nickname": mask_nickname(user_info.get("screen_name", "")),
    }
    utils.logger.info(f"[store.weibo.update_weibo_note_comment] Weibo note comment: {comment_id}, content: {save_comment_item.get('content', '')[:24]} ...")
    await WeibostoreFactory.create_store().store_comment(comment_item=save_comment_item)


async def update_weibo_note_image(picid: str, pic_content, extension_file_name):
    """
    Save weibo note image to local
    Args:
        picid:
        pic_content:
        extension_file_name:

    Returns:

    """
    await WeiboStoreImage().store_image({"pic_id": picid, "pic_content": pic_content, "extension_file_name": extension_file_name})


async def save_creator(user_id: str, user_info: Dict):
    """
    Save creator information to local
    Educational version: To prevent harassment, creator personal information (nickname/gender/avatar/bio/IP/follower count, etc.) is no longer collected/persisted.
    This entry is kept as a no-op for caller compatibility. user_id is only used locally by callers to fetch the creator's weibo posts.
    Args:
        user_id:
        user_info:

    Returns:

    """
    # Educational version: Creator personal information is neither collected nor persisted
    return
