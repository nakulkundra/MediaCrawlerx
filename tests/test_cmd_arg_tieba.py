# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_cmd_arg_tieba.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import pytest
import config
from cmd_arg import parse_cmd
from media_platform.tieba import TieBaCrawler


@pytest.mark.asyncio
async def test_tieba_detail_cli_sets_specified_ids():
    await parse_cmd(
        [
            "--platform",
            "tieba",
            "--type",
            "detail",
            "--specified_id",
            "https://tieba.baidu.com/p/10451142633,9835114923",
        ]
    )

    assert config.TIEBA_SPECIFIED_ID_LIST == ["10451142633", "9835114923"]


@pytest.mark.asyncio
async def test_tieba_creator_cli_sets_creator_ids():
    await parse_cmd(
        [
            "--platform",
            "tieba",
            "--type",
            "creator",
            "--creator_id",
            "creator123,creator456",
        ]
    )

    assert config.TIEBA_CREATOR_ID_LIST == ["creator123", "creator456"]
