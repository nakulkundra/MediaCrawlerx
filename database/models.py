# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/database/models.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# Disclaimer: This code is for educational and research purposes only. Users must adhere to the following principles:
# 1. Do not use for any commercial purposes.
# 2. Comply with the target platform's Terms of Service and robots.txt rules during use.
# 3. Do not conduct large-scale scraping or cause operational disruptions to the platform.
# 4. Reasonably control request frequencies to avoid placing unnecessary burdens on target platforms.
# 5. Do not use for any illegal or inappropriate purposes.
#
# For detailed license terms, please refer to the LICENSE file in the project root directory.
# Using this code indicates that you agree to abide by the above principles and all terms in LICENSE.
#
# Educational edition note: To prevent scraped user personal information from being used to locate real individuals and send unsolicited harassment,
# this ORM no longer persists any identifiable user fields (user ID, IP location, avatar,
# profile URL, bio/signature, gender, etc. are completely omitted). Original user IDs are converted into anonymous creator_hash
# via tools.user_hash.anonymize_user_id at the extraction layer before being written,
# used solely for content grouping of the "same creator"; nicknames are retained but masked via mask_nickname.
# Creator profile tables (XhsCreator/DyCreator/WeiboCreator/TiebaCreator/
# ZhihuCreator/BilibiliUpInfo/BilibiliContactInfo) have been completely removed.

from sqlalchemy import create_engine, Column, Integer, Text, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class BilibiliVideo(Base):
    __tablename__ = 'bilibili_video'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    video_id = Column(String(64), nullable=False, index=True, unique=True, comment='Video ID')
    video_url = Column(Text, nullable=False, comment='Video URL')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    liked_count = Column(Integer, comment='Liked count')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    video_type = Column(Text, comment='Video type')
    title = Column(Text, comment='Video title')
    desc = Column(Text, comment='Video description')
    create_time = Column(BigInteger, index=True, comment='Created timestamp')
    disliked_count = Column(Text, comment='Disliked count')
    video_play_count = Column(Text, comment='Play count')
    video_favorite_count = Column(Text, comment='Favorite count')
    video_share_count = Column(Text, comment='Share count')
    video_coin_count = Column(Text, comment='Coin count')
    video_danmaku = Column(Text, comment='Danmaku count')
    video_comment = Column(Text, comment='Comment count')
    video_cover_url = Column(Text, comment='Video cover URL')
    source_keyword = Column(Text, default='', comment='Source keyword')


class BilibiliVideoComment(Base):
    __tablename__ = 'bilibili_video_comment'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    comment_id = Column(String(128), index=True, comment='Comment ID')
    video_id = Column(String(64), index=True, comment='Video ID')
    content = Column(Text, comment='Comment content')
    create_time = Column(BigInteger, comment='Created timestamp')
    sub_comment_count = Column(Text, comment='Sub-comment count')
    parent_comment_id = Column(String(255), comment='Parent comment ID')
    like_count = Column(Text, default='0', comment='Like count')


class BilibiliUpDynamic(Base):
    __tablename__ = 'bilibili_up_dynamic'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    dynamic_id = Column(String(128), index=True, comment='Dynamic ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    user_name = Column(Text, comment='User name (masked)')
    text = Column(Text, comment='Dynamic content')
    type = Column(Text, comment='Dynamic type')
    pub_ts = Column(BigInteger, comment='Published timestamp')
    total_comments = Column(Integer, comment='Total comments')
    total_forwards = Column(Integer, comment='Total forwards')
    total_liked = Column(Integer, comment='Total likes')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')


class DouyinAweme(Base):
    __tablename__ = 'douyin_aweme'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    aweme_id = Column(String(255), index=True, comment='Aweme ID')
    aweme_type = Column(Text, comment='Aweme type')
    title = Column(Text, comment='Aweme title')
    desc = Column(Text, comment='Aweme description')
    create_time = Column(BigInteger, index=True, comment='Created timestamp')
    liked_count = Column(Text, comment='Liked count')
    comment_count = Column(Text, comment='Comment count')
    share_count = Column(Text, comment='Share count')
    collected_count = Column(Text, comment='Collected count')
    aweme_url = Column(Text, comment='Aweme URL')
    cover_url = Column(Text, comment='Cover URL')
    video_download_url = Column(Text, comment='Video download URL')
    music_download_url = Column(Text, comment='Music download URL')
    note_download_url = Column(Text, comment='Note download URL')
    source_keyword = Column(Text, default='', comment='Source keyword')


class DouyinAwemeComment(Base):
    __tablename__ = 'douyin_aweme_comment'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    comment_id = Column(String(255), index=True, comment='Comment ID')
    aweme_id = Column(String(255), index=True, comment='Aweme ID')
    content = Column(Text, comment='Comment content')
    create_time = Column(BigInteger, comment='Created timestamp')
    sub_comment_count = Column(Text, comment='Sub-comment count')
    parent_comment_id = Column(String(255), comment='Parent comment ID')
    like_count = Column(Text, default='0', comment='Like count')
    pictures = Column(Text, default='', comment='Pictures')


class KuaishouVideo(Base):
    __tablename__ = 'kuaishou_video'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    video_id = Column(String(255), index=True, comment='Video ID')
    video_type = Column(Text, comment='Video type')
    title = Column(Text, comment='Video title')
    desc = Column(Text, comment='Video description')
    create_time = Column(BigInteger, index=True, comment='Created timestamp')
    liked_count = Column(Text, comment='Liked count')
    viewd_count = Column(Text, comment='Viewed count')
    video_url = Column(Text, comment='Video URL')
    video_cover_url = Column(Text, comment='Video cover URL')
    video_play_url = Column(Text, comment='Video play URL')
    source_keyword = Column(Text, default='', comment='Source keyword')


class KuaishouVideoComment(Base):
    __tablename__ = 'kuaishou_video_comment'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    comment_id = Column(String(255), index=True, comment='Comment ID')
    video_id = Column(String(255), index=True, comment='Video ID')
    content = Column(Text, comment='Comment content')
    create_time = Column(BigInteger, comment='Created timestamp')
    sub_comment_count = Column(Text, comment='Sub-comment count')


class WeiboNote(Base):
    __tablename__ = 'weibo_note'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    note_id = Column(String(64), index=True, comment='Note ID')
    content = Column(Text, comment='Note content')
    create_time = Column(BigInteger, index=True, comment='Created timestamp')
    create_date_time = Column(String(255), index=True, comment='Created date time')
    liked_count = Column(Text, comment='Liked count')
    comments_count = Column(Text, comment='Comments count')
    shared_count = Column(Text, comment='Shared count')
    note_url = Column(Text, comment='Note URL')
    source_keyword = Column(Text, default='', comment='Source keyword')


class WeiboNoteComment(Base):
    __tablename__ = 'weibo_note_comment'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    comment_id = Column(String(64), index=True, comment='Comment ID')
    note_id = Column(String(64), index=True, comment='Note ID')
    content = Column(Text, comment='Comment content')
    create_time = Column(BigInteger, comment='Created timestamp')
    create_date_time = Column(String(255), index=True, comment='Created date time')
    comment_like_count = Column(Text, comment='Comment like count')
    sub_comment_count = Column(Text, comment='Sub-comment count')
    parent_comment_id = Column(String(255), comment='Parent comment ID')


class XhsNote(Base):
    __tablename__ = 'xhs_note'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    note_id = Column(String(255), index=True, comment='Note ID')
    type = Column(Text, comment='Note type')
    title = Column(Text, comment='Note title')
    desc = Column(Text, comment='Note description')
    video_url = Column(Text, comment='Video URL')
    time = Column(BigInteger, index=True, comment='Timestamp')
    last_update_time = Column(BigInteger, comment='Last update timestamp')
    liked_count = Column(Text, comment='Liked count')
    collected_count = Column(Text, comment='Collected count')
    comment_count = Column(Text, comment='Comment count')
    share_count = Column(Text, comment='Share count')
    image_list = Column(Text, comment='Image list')
    tag_list = Column(Text, comment='Tag list')
    note_url = Column(Text, comment='Note URL')
    source_keyword = Column(Text, default='', comment='Source keyword')
    xsec_token = Column(Text, comment='Xsec Token')


class XhsNoteComment(Base):
    __tablename__ = 'xhs_note_comment'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    comment_id = Column(String(255), index=True, comment='Comment ID')
    create_time = Column(BigInteger, index=True, comment='Created timestamp')
    note_id = Column(String(255), comment='Note ID')
    content = Column(Text, comment='Comment content')
    sub_comment_count = Column(Integer, comment='Sub-comment count')
    pictures = Column(Text, comment='Pictures')
    parent_comment_id = Column(String(255), comment='Parent comment ID')
    like_count = Column(Text, comment='Like count')


class TiebaNote(Base):
    __tablename__ = 'tieba_note'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    note_id = Column(String(644), index=True, comment='Note ID')
    title = Column(Text, comment='Note title')
    desc = Column(Text, comment='Note description')
    note_url = Column(Text, comment='Note URL')
    publish_time = Column(String(255), index=True, comment='Publish time')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    user_nickname = Column(Text, default='', comment='User nickname (masked)')
    tieba_id = Column(String(255), default='', comment='Tieba ID')
    tieba_name = Column(Text, comment='Tieba name')
    tieba_link = Column(Text, comment='Tieba link')
    total_replay_num = Column(Integer, default=0, comment='Total reply count')
    total_replay_page = Column(Integer, default=0, comment='Total reply pages')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
    source_keyword = Column(Text, default='', comment='Source keyword')


class TiebaComment(Base):
    __tablename__ = 'tieba_comment'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    comment_id = Column(String(255), index=True, comment='Comment ID')
    parent_comment_id = Column(String(255), default='', comment='Parent comment ID')
    content = Column(Text, comment='Comment content')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    user_nickname = Column(Text, default='', comment='User nickname (masked)')
    tieba_id = Column(String(255), default='', comment='Tieba ID')
    tieba_name = Column(Text, comment='Tieba name')
    tieba_link = Column(Text, comment='Tieba link')
    publish_time = Column(String(255), index=True, comment='Publish time')
    sub_comment_count = Column(Integer, default=0, comment='Sub-comment count')
    note_id = Column(String(255), index=True, comment='Note ID')
    note_url = Column(Text, comment='Note URL')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')


class ZhihuContent(Base):
    __tablename__ = 'zhihu_content'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    content_id = Column(String(64), index=True, comment='Content ID')
    content_type = Column(Text, comment='Content type')
    content_text = Column(Text, comment='Content text')
    content_url = Column(Text, comment='Content URL')
    question_id = Column(String(255), comment='Question ID')
    title = Column(Text, comment='Title')
    desc = Column(Text, comment='Description')
    created_time = Column(String(32), index=True, comment='Created time')
    updated_time = Column(Text, comment='Updated time')
    voteup_count = Column(Integer, default=0, comment='Voteup count')
    comment_count = Column(Integer, default=0, comment='Comment count')
    source_keyword = Column(Text, comment='Source keyword')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    user_nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')


class ZhihuComment(Base):
    __tablename__ = 'zhihu_comment'
    id = Column(Integer, primary_key=True, comment='Primary key ID')
    comment_id = Column(String(64), index=True, comment='Comment ID')
    parent_comment_id = Column(String(64), comment='Parent comment ID')
    content = Column(Text, comment='Comment content')
    publish_time = Column(String(32), index=True, comment='Publish time')
    sub_comment_count = Column(Integer, default=0, comment='Sub-comment count')
    like_count = Column(Integer, default=0, comment='Like count')
    dislike_count = Column(Integer, default=0, comment='Dislike count')
    content_id = Column(String(64), index=True, comment='Content ID')
    content_type = Column(Text, comment='Content type')
    creator_hash = Column(String(64), index=True, comment='Creator anonymous hash')
    user_nickname = Column(Text, comment='User nickname (masked)')
    add_ts = Column(BigInteger, comment='Added timestamp')
    last_modify_ts = Column(BigInteger, comment='Last modified timestamp')
