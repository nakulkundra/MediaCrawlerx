# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/recv_sms.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# Statement: This code is for learning and research purposes only. Users should abide by the following principles:
# 1. Do not use for any commercial purposes.
# 2. Comply with the target platform's Terms of Service and robots.txt rules when using.
# 3. Do not engage in large-scale scraping or cause operational disruption to the platform.
# 4. Reasonably control request frequencies to avoid placing unnecessary burden on the target platform.
# 5. Do not use for any illegal or improper purposes.
#
# For detailed license terms, please refer to the LICENSE file in the project root directory.
# By using this code, you agree to abide by the above principles and all terms in LICENSE.

import re
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

import config
from cache.abs_cache import AbstractCache
from cache.cache_factory import CacheFactory
from tools import utils

app = FastAPI()

cache_client: AbstractCache = CacheFactory.create_cache(cache_type=config.CACHE_TYPE_MEMORY)


class SmsNotification(BaseModel):
    platform: str
    current_number: str
    from_number: str
    sms_content: str
    timestamp: str


def extract_verification_code(message: str) -> str:
    """
    Extract verification code of 6 digits from the SMS.
    """
    pattern = re.compile(r'\b[0-9]{6}\b')
    codes: List[str] = pattern.findall(message)
    return codes[0] if codes else ""


@app.post("/")
def receive_sms_notification(sms: SmsNotification):
    """
    Receive SMS notification and send it to Redis.
    Args:
        sms:
            {
                "platform": "xhs",
                "from_number": "1069421xxx134",
                "sms_content": "[RED] Your verification code is: 171959, valid for 3 minutes. Please do not share it with others. If not operated by yourself, ignore this message.",
                "timestamp": "1686720601614",
                "current_number": "13152442222"
            }

    Returns:

    """
    utils.logger.info(f"Received SMS notification: {sms.platform}, {sms.current_number}")
    sms_code = extract_verification_code(sms.sms_content)
    if sms_code:
        # Save the verification code in Redis and set the expiration time to 3 minutes.
        key = f"{sms.platform}_{sms.current_number}"
        cache_client.set(key, sms_code, expire_time=60 * 3)

    return {"status": "ok"}


@app.get("/", status_code=status.HTTP_404_NOT_FOUND)
async def not_found():
    raise HTTPException(status_code=404, detail="Not Found")


if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')
