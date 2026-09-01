# Frequently Asked Questions (FAQ)

## Missing Node.js Environment Issues
**Q**: Crawling Douyin or Zhihu raises error: `execjs._exceptions.ProgramError: SyntaxError: Unexpected token` or missing `;`  
**A**: This error occurs when the Node.js environment is missing. Install Node.js (`>= v16.0.0`) from [Node.js Official Site](https://nodejs.org/).

**Q**: Crawling Douyin with Cookie raises error: `execjs._exceptions.ProgramError: TypeError: Cannot read property 'JS_MD5_NO_COMMON_JS' of null`  
**A**: On Windows, install Node.js (version 16 or higher) using the official Windows 64-bit installer.

---

## Xiaohongshu (XHS) Slider Verification Issues
**Q**: After QR code login on Xiaohongshu, the slider captcha loops or fails verification?  
**A**: Xiaohongshu employs strict anti-bot detection. **We strongly recommend enabling CDP mode to connect to your real Chrome browser** (the default configuration). Connecting to your real browser reuses existing cookies, login state, and browsing history, drastically reducing risk scores. If issues persist, delete the `browser_data/` folder in the project root and log in again.

---

## Specifying Search Keywords
**Q**: Can I specify custom search keywords?  
**A**: In `config/base_config.py`, configure the `KEYWORDS` parameter (comma-separated string, e.g. `"fashion,travel"`).

---

## Specifying Post/Video IDs
**Q**: Can I crawl specific posts or videos by ID?  
**A**: In `config/base_config.py`, set `CRAWLER_TYPE = "detail"` and configure the corresponding platform ID list (e.g. `XHS_SPECIFIED_ID_LIST`).

---

## Crawling Suddenly Stops Working
**Q**: Data crawls fine initially, but fails after a short period?  
**A**: This is usually caused by triggering platform rate-limiting or anti-scraping risk controls. Please avoid high-frequency large-scale scraping, add delays between requests, and utilize rotating proxies or CDP mode.

---

## Switching / Changing Accounts
**Q**: How do I switch to a different account?  
**A**: Delete the `browser_data/` directory located in the project root to clear stored session contexts and cookies, then re-authenticate.

---

## Playwright Timeout Errors
**Q**: Error: `playwright._impl._api_types.TimeoutError: Timeout 30000ms exceeded.`  
**A**: Check your network connectivity, proxy settings, or firewall configurations. Ensure external platform servers are reachable from your network.

---

## Passing Captcha Manually in Playwright
**Q**: How do I solve captcha manually during login?  
**A**: In `config/base_config.py`, set `HEADLESS = False`. When the browser launches, solve the slider or puzzle captcha manually in the browser window.

---

## Word Cloud Generation
**Q**: How do I generate word clouds from collected post data?  
**A**: Refer to `docs/wordcloud_guide.md` to configure stopwords, font files, and trigger the word cloud generator tool.
