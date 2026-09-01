# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/kuaishou/help.py
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

import re

from playwright.async_api import Page

from model.m_kuaishou import VideoUrlInfo, CreatorUrlInfo

# Kuaishou web end signature (__NS_hxfalcon) support.
# Kuaishou web end has migrated batch list interfaces to REST endpoints with signatures,
# obtain the calling entry of the page's built-in signing environment via a capture script injected at page load,
# then call $encode to generate the signature. Only reuses the JS environment already loaded by the page itself,
# without introducing extra signature code files.

KS_SIGN_CAPTURE_SCRIPT = """
// Capture the calling entry of Kuaishou page built-in signing environment (for learning purposes)
(() => {
  if (window.__ks_realm) return;
  let done = false;
  const setter = function (v) {
    if (!done && this && typeof this === "object" && this !== window &&
        typeof this.$encode === "function" &&
        typeof this.$getCatVersion === "function") {
      done = true;
      window.__ks_realm = this;
      // After capturing successfully, remove the hook to avoid affecting other page behaviors
      try { delete Object.prototype.caver; } catch (e) {}
    }
    Object.defineProperty(this, "caver", {
      value: v, writable: true, enumerable: true, configurable: true,
    });
  };
  try {
    Object.defineProperty(Object.prototype, "caver", { set: setter, configurable: true });
  } catch (e) {}
})();
"""


async def get_ks_sign_from_playwright(page: Page, url: str, query: dict, body: dict) -> str:
    """
    Generate Kuaishou __NS_hxfalcon signature via browser page
    Args:
        page: playwright page that loaded Kuaishou page (needs KS_SIGN_CAPTURE_SCRIPT injected beforehand)
        url: request path, e.g. /rest/v/profile/feed
        query: request query parameters, e.g. {"caver": 2}
        body: request body (JSON object)
    Returns:
        Signature string
    """
    try:
        await page.wait_for_function("() => !window.__ks_realm", timeout=15000)
    except Exception:
        # The page may have loaded before cookie injection (unlogged-in state), at which time the signing environment is uninitialized,
        # reload the page so it loads in logged-in state and triggers signing requests; the capture script will take effect with the new document
        await page.reload(wait_until="domcontentloaded")
        await page.wait_for_function("() => !window.__ks_realm", timeout=20000)
    return await page.evaluate(
        """([u, q, b]) => new Promise((resolve, reject) => {
            window.__ks_realm.call('$encode', [
                { url: u, query: q, form: {}, requestBody: b },
                { suc: s => resolve(s), err: e => reject(new Error(String(e))) }
            ]);
        })""",
        [url, query, body],
    )


def parse_video_info_from_url(url: str) -> VideoUrlInfo:
    """
    Parse video ID from Kuaishou video URL
    Supports the following formats:
    1. Full video URL: "https://www.kuaishou.com/short-video/3x3zxz4mjrsc8ke?authorId=3x84qugg4ch9zhs&streamSource=search"
    2. Pure video ID: "3x3zxz4mjrsc8ke"

    Args:
        url: Kuaishou video link or video ID
    Returns:
        VideoUrlInfo: Object containing video ID
    """
    # If it doesn't contain http and doesn't contain kuaishou.com, consider it as pure ID
    if not url.startswith("http") and "kuaishou.com" not in url:
        return VideoUrlInfo(video_id=url, url_type="normal")

    # Extract ID from standard video URL: /short-video/video_ID
    video_pattern = r'/short-video/([a-zA-Z0-9_-]+)'
    match = re.search(video_pattern, url)
    if match:
        video_id = match.group(1)
        return VideoUrlInfo(video_id=video_id, url_type="normal")

    raise ValueError(f"Unable to parse video ID from URL: {url}")


def parse_creator_info_from_url(url: str) -> CreatorUrlInfo:
    """
    Parse creator ID from Kuaishou creator homepage URL
    Supports the following formats:
    1. Creator homepage: "https://www.kuaishou.com/profile/3x84qugg4ch9zhs"
    2. Pure ID: "3x4sm73aye7jq7i"

    Args:
        url: Kuaishou creator homepage link or user_id
    Returns:
        CreatorUrlInfo: Object containing creator ID
    """
    # If it doesn't contain http and doesn't contain kuaishou.com, consider it as pure ID
    if not url.startswith("http") and "kuaishou.com" not in url:
        return CreatorUrlInfo(user_id=url)

    # Extract user_id from creator homepage URL: /profile/xxx
    user_pattern = r'/profile/([a-zA-Z0-9_-]+)'
    match = re.search(user_pattern, url)
    if match:
        user_id = match.group(1)
        return CreatorUrlInfo(user_id=user_id)

    raise ValueError(f"Unable to parse creator ID from URL: {url}")


if __name__ == '__main__':
    # Test video URL parsing
    print("=== Video URL Parsing Test ===")
    test_video_urls = [
        "https://www.kuaishou.com/short-video/3x3zxz4mjrsc8ke?authorId=3x84qugg4ch9zhs&streamSource=search&area=searchxxnull&searchKey=python",
        "3xf8enb8dbj6uig",
    ]
    for url in test_video_urls:
        try:
            result = parse_video_info_from_url(url)
            print(f"✓ URL: {url[:80]}...")
            print(f"  Result: {result}\n")
        except Exception as e:
            print(f"✗ URL: {url}")
            print(f"  Error: {e}\n")

    # Test creator URL parsing
    print("=== Creator URL Parsing Test ===")
    test_creator_urls = [
        "https://www.kuaishou.com/profile/3x84qugg4ch9zhs",
        "3x4sm73aye7jq7i",
    ]
    for url in test_creator_urls:
        try:
            result = parse_creator_info_from_url(url)
            print(f"✓ URL: {url[:80]}...")
            print(f"  Result: {result}\n")
        except Exception as e:
            print(f"✗ URL: {url}")
            print(f"  Error: {e}\n")
