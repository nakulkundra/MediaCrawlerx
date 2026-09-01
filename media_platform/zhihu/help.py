# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/zhihu/help.py
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

# -*- coding: utf-8 -*-
import json
import re
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import execjs
from parsel import Selector

from constant import zhihu as zhihu_constant
from model.m_zhihu import ZhihuComment, ZhihuContent, ZhihuCreator
from tools import utils
from tools.crawler_util import extract_text_from_html
from tools.user_hash import anonymize_user_id, mask_nickname

ZHIHU_SGIN_JS = None


def sign(url: str, cookies: str) -> Dict:
    """
    zhihu sign algorithm
    Args:
        url: request url with query string
        cookies: request cookies with d_c0 key

    Returns:

    """
    global ZHIHU_SGIN_JS
    if not ZHIHU_SGIN_JS:
        with open("libs/zhihu.js", mode="r", encoding="utf-8-sig") as f:
            ZHIHU_SGIN_JS = execjs.compile(f.read())

    return ZHIHU_SGIN_JS.call("get_sign", url, cookies)


def judge_zhihu_url(url: str) -> Dict[str, str]:
    """
    Determine the type and ID of a Zhihu URL
    Args:
        url: Zhihu URL

    Returns:
        Dict: {"type": content_type, "id": content_id, "url_token": url_token}
    """
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/")

    res = {"type": "", "id": "", "url_token": ""}
    if "question" in parts and "answer" in parts:
        res["type"] = zhihu_constant.ANSWER_NAME
        res["id"] = parts[parts.index("answer") + 1]
    elif "p" in parts:
        res["type"] = zhihu_constant.ARTICLE_NAME
        res["id"] = parts[parts.index("p") + 1]
    elif "zvideo" in parts:
        res["type"] = zhihu_constant.VIDEO_NAME
        res["id"] = parts[parts.index("zvideo") + 1]
    elif "people" in parts:
        res["type"] = "creator"
        res["url_token"] = parts[parts.index("people") + 1]
    return res


class ZhihuExtractor:
    def __init__(self):
        pass

    def extract_contents_from_search(self, json_data: Dict) -> List[ZhihuContent]:
        """
        extract zhihu contents
        Args:
            json_data: zhihu json data

        Returns:

        """
        if not json_data:
            return []

        search_result: List[Dict] = json_data.get("data", [])
        search_result = [s_item for s_item in search_result if s_item.get("type") in ['search_result', 'zvideo']]
        return self._extract_content_list([sr_item.get("object") for sr_item in search_result if sr_item.get("object")])

    def _extract_content_list(self, content_list: List[Dict]) -> List[ZhihuContent]:
        """
        extract zhihu content list
        Args:
            content_list:

        Returns:

        """
        if not content_list:
            return []

        res: List[ZhihuContent] = []
        for content in content_list:
            if content.get("type") == zhihu_constant.ANSWER_NAME:
                res.append(self._extract_answer_content(content))
            elif content.get("type") == zhihu_constant.ARTICLE_NAME:
                res.append(self._extract_article_content(content))
            elif content.get("type") == zhihu_constant.VIDEO_NAME:
                res.append(self._extract_zvideo_content(content))
            else:
                continue
        return res

    def _extract_answer_content(self, answer: Dict) -> ZhihuContent:
        """
        extract zhihu answer content
        Args:
            answer: zhihu answer

        Returns:
        """
        res = ZhihuContent()
        res.content_id = str(answer.get("id") or "")
        res.content_type = answer.get("type")
        res.content_text = extract_text_from_html(answer.get("content", ""))
        res.question_id = str(answer.get("question", {}).get("id") or "")
        res.content_url = f"{zhihu_constant.ZHIHU_URL}/question/{res.question_id}/answer/{res.content_id}"
        res.title = extract_text_from_html(answer.get("question", {}).get("title", ""))
        res.desc = extract_text_from_html(answer.get("excerpt", ""))
        author = answer.get("author", {})
        res.user_id = anonymize_user_id(author.get("id", ""))
        res.user_nickname = mask_nickname(author.get("name", ""))
        res.user_avatar = author.get("avatar_url", "")
        res.user_url = f"{zhihu_constant.ZHIHU_URL}/people/{author.get('url_token', '')}"
        res.url_token = author.get("url_token", "")
        res.user_gender = "male" if author.get("gender") == 1 else "female"
        res.created_time = answer.get("created_time", 0)
        res.updated_time = answer.get("updated_time", 0)
        res.voteup_count = answer.get("voteup_count", 0)
        res.comment_count = answer.get("comment_count", 0)
        return res

    def _extract_article_content(self, article: Dict) -> ZhihuContent:
        """
        extract zhihu article content
        Args:
            article: zhihu article

        Returns:
        """
        res = ZhihuContent()
        res.content_id = str(article.get("id") or "")
        res.content_type = article.get("type")
        res.content_text = extract_text_from_html(article.get("content", ""))
        res.content_url = f"{zhihu_constant.ZHIHU_ZHUANLAN_URL}/p/{res.content_id}"
        res.title = extract_text_from_html(article.get("title", ""))
        res.desc = extract_text_from_html(article.get("excerpt", ""))
        author = article.get("author", {})
        res.user_id = anonymize_user_id(author.get("id", ""))
        res.user_nickname = mask_nickname(author.get("name", ""))
        res.user_avatar = author.get("avatar_url", "")
        res.user_url = f"{zhihu_constant.ZHIHU_URL}/people/{author.get('url_token', '')}"
        res.url_token = author.get("url_token", "")
        res.user_gender = "male" if author.get("gender") == 1 else "female"
        res.created_time = article.get("created", 0)
        res.updated_time = article.get("updated", 0)
        res.voteup_count = article.get("voteup_count", 0)
        res.comment_count = article.get("comment_count", 0)
        return res

    def _extract_zvideo_content(self, video: Dict) -> ZhihuContent:
        """
        extract zhihu video content
        Args:
            video: zhihu video

        Returns:
        """
        res = ZhihuContent()
        res.content_id = str(video.get("id") or "")
        res.content_type = video.get("type")
        res.content_text = extract_text_from_html(video.get("description", ""))
        res.content_url = f"{zhihu_constant.ZHIHU_URL}/zvideo/{res.content_id}"
        res.title = extract_text_from_html(video.get("title", ""))
        res.desc = extract_text_from_html(video.get("description", ""))
        author = video.get("author", {})
        res.user_id = anonymize_user_id(author.get("id", ""))
        res.user_nickname = mask_nickname(author.get("name", ""))
        res.user_avatar = author.get("avatar_url", "")
        res.user_url = f"{zhihu_constant.ZHIHU_URL}/people/{author.get('url_token', '')}"
        res.url_token = author.get("url_token", "")
        res.user_gender = "male" if author.get("gender") == 1 else "female"
        res.created_time = video.get("created_at", 0)
        res.updated_time = video.get("updated_at", 0)
        res.voteup_count = video.get("voteup_count", 0)
        res.comment_count = video.get("comment_count", 0)
        return res

    def extract_comments(self, json_data: Dict, content_id: str) -> List[ZhihuComment]:
        """
        extract zhihu comments
        Args:
            json_data:
            content_id:

        Returns:

        """
        if not json_data:
            return []

        res: List[ZhihuComment] = []
        for item in json_data.get("data", []):
            comment = ZhihuComment()
            comment.comment_id = str(item.get("id", ""))
            comment.content_id = content_id
            comment.content = extract_text_from_html(item.get("content", ""))
            author = item.get("author", {}).get("member", {})
            comment.user_id = anonymize_user_id(author.get("id", ""))
            comment.user_nickname = mask_nickname(author.get("name", ""))
            comment.user_avatar = author.get("avatar_url", "")
            comment.user_url = f"{zhihu_constant.ZHIHU_URL}/people/{author.get('url_token', '')}"
            comment.url_token = author.get("url_token", "")
            comment.user_gender = "male" if author.get("gender") == 1 else "female"
            comment.created_time = item.get("created_time", 0)
            comment.voteup_count = item.get("vote_count", 0)
            comment.reply_to_comment_id = str(item.get("reply_to_comment_id", "") or "")
            comment.parent_comment_id = str(item.get("ancestor_id", "") or "")
            res.append(comment)
        return res

    def extract_creator_info(self, json_data: Dict) -> ZhihuCreator:
        """
        extract zhihu creator info
        Args:
            json_data:

        Returns:

        """
        res = ZhihuCreator()
        res.user_id = anonymize_user_id(json_data.get("id", ""))
        res.user_nickname = mask_nickname(json_data.get("name", ""))
        res.user_avatar = json_data.get("avatar_url", "")
        res.url_token = json_data.get("url_token", "")
        res.user_url = f"{zhihu_constant.ZHIHU_URL}/people/{res.url_token}"
        res.headline = json_data.get("headline", "")
        res.description = json_data.get("description", "")
        res.gender = "male" if json_data.get("gender") == 1 else "female"
        res.follower_count = json_data.get("follower_count", 0)
        res.following_count = json_data.get("following_count", 0)
        res.answer_count = json_data.get("answer_count", 0)
        res.article_count = json_data.get("articles_count", 0)
        res.zvideo_count = json_data.get("zvideo_count", 0)
        res.voteup_count = json_data.get("voteup_count", 0)
        return res

    def extract_creator_contents(self, json_data: Dict) -> List[ZhihuContent]:
        """
        extract creator contents from user profile
        Args:
            json_data:

        Returns:

        """
        if not json_data:
            return []
        return self._extract_content_list(json_data.get("data", []))
