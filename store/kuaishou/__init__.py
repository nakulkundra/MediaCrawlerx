# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/store/kuaishou/__init__.py
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
# @Time    : 2024/1/14 20:03
# @Desc    :
from typing import List, Dict

import config
from var import source_keyword_var
from tools.user_hash import anonymize_user_id, mask_nickname

from ._store_impl import *


class KuaishouStoreFactory:
    STORES = {
        "csv": KuaishouCsvStoreImplement,
        "db": KuaishouDbStoreImplement,
        "postgres": KuaishouDbStoreImplement,
        "json": KuaishouJsonStoreImplement,
        "jsonl": KuaishouJsonlStoreImplement,
        "sqlite": KuaishouSqliteStoreImplement,
        "mongodb": KuaishouMongoStoreImplement,
        "excel": KuaishouExcelStoreImplement,
    }

    @staticmethod
    def create_store() -> AbstractStore:
        store_class = KuaishouStoreFactory.STORES.get(config.SAVE_DATA_OPTION)
        if not store_class:
            raise ValueError(
                "[KuaishouStoreFactory.create_store] Invalid save option only supported csv or db or json or sqlite or mongodb or excel ..."
            )
        return store_class()


async def update_kuaishou_video(video_item: Dict):
    photo_info: Dict = video_item.get("photo", {})
    video_id = photo_info.get("id")
    if not video_id:
        return
    user_info = video_item.get("author", {})
    save_content_item = {
        "video_id": video_id,
        "video_type": str(video_item.get("type")),
        "title": photo_info.get("caption", "")[:500],
        "desc": photo_info.get("caption", "")[:500],
        "create_time": photo_info.get("timestamp"),
        "creator_hash": anonymize_user_id(user_info.get("id")),  # Creator anonymous hash (does not store original user_id)
        "nickname": mask_nickname(user_info.get("name")),  # User nickname (masked)
        "liked_count": str(photo_info.get("realLikeCount")),
        "viewd_count": str(photo_info.get("viewCount")),
        "last_modify_ts": utils.get_current_timestamp(),
        "video_url": f"https://www.kuaishou.com/short-video/{video_id}",
        "video_cover_url": photo_info.get("coverUrl", ""),
        "video_play_url": photo_info.get("photoUrl", ""),
        "source_keyword": source_keyword_var.get(),
    }
    utils.logger.info(
        f"[store.kuaishou.update_kuaishou_video] Kuaishou video id:{video_id}, title:{save_content_item.get('title')}"
    )
    await KuaishouStoreFactory.create_store().store_content(content_item=save_content_item)


async def batch_update_ks_video_comments(video_id: str, comments: List[Dict]):
    utils.logger.info(f"[store.kuaishou.batch_update_ks_video_comments] video_id:{video_id}, comments:{comments}")
    if not comments:
        return
    for comment_item in comments:
        await update_ks_video_comment(video_id, comment_item)


async def update_ks_video_comment(video_id: str, comment_item: Dict):
    # V2 API uses snake_case field names and comment_id is int type
    # Old GraphQL API used camelCase field names
    # Support both formats for backward compatibility
    comment_id = comment_item.get("comment_id") or comment_item.get("commentId")
    save_comment_item = {
        "comment_id": str(comment_id) if comment_id else None,  # Convert to string for storage
        "create_time": comment_item.get("timestamp"),
        "video_id": video_id,
        "content": comment_item.get("content"),
        # Creator anonymous hash (does not store original user_id): V2: author_id, Old: authorId
        "creator_hash": anonymize_user_id(comment_item.get("author_id") or comment_item.get("authorId")),
        # User nickname (masked): V2: author_name, Old: authorName
        "nickname": mask_nickname(comment_item.get("author_name") or comment_item.get("authorName")),
        # V2: commentCount, Old: subCommentCount
        "sub_comment_count": str(comment_item.get("commentCount") or comment_item.get("subCommentCount", 0)),
        "last_modify_ts": utils.get_current_timestamp(),
    }
    utils.logger.info(
        f"[store.kuaishou.update_ks_video_comment] Kuaishou video comment: {comment_id}, content: {save_comment_item.get('content')}"
    )
    await KuaishouStoreFactory.create_store().store_comment(comment_item=save_comment_item)


async def save_creator(user_id: str, creator: Dict):
    # Educational version: Creator personal profile (nickname/gender/avatar/signature/IP/follower count, etc.) is no longer persisted in the database to prevent harassment.
    return
