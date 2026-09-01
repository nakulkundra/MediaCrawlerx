# MediaCrawler Usage Guide

## Project Documentation

- [Project Architecture Guide](architecture_guide.md) - System architecture, module design, and data flow (includes Mermaid diagrams)
- [CDP Mode Guide](cdp_mode_guide.md) - Using Chrome DevTools Protocol for anti-crawler bypass
- [Data Storage Guide](data_storage_guide.md) - SQLite, MySQL, PostgreSQL, MongoDB, JSON, and CSV storage
- [Excel Export Guide](excel_export_guide.md) - Exporting multi-sheet formatted Excel reports
- [FAQ](faq.md) - Frequently asked questions and troubleshooting
- [Proxy Configuration Guide](kuaidaili_proxy_guide.md) - Proxy pool setup and integration
- [Word Cloud Guide](wordcloud_guide.md) - Word cloud generator configuration
- [Project Code Structure](project_structure.md) - Detailed codebase layout and directory map

## Recommended: Managing Dependencies with `uv`

### 1. Prerequisites
- Install [uv](https://docs.astral.sh/uv/getting-started/installation) and verify with `uv --version`.
- Python version **3.11** is recommended.
- Install Node.js (required for Douyin and Zhihu signature generation), version `>= 16.0.0`.

### 2. Synchronize Python Dependencies
```shell
# Navigate to project root directory
cd MediaCrawler

# Sync dependencies using uv
uv sync
```

### 3. Install Playwright Browser Drivers
```shell
uv run playwright install
```
> The project supports connecting to local Chrome via Playwright. To use CDP mode, adjust the corresponding settings in `config/base_config.py`.

### 4. Run the Crawler
```shell
# By default comment crawling is disabled. To enable, update ENABLE_GET_COMMENTS in config/base_config.py
# All configuration toggles can be viewed and customized in config/base_config.py

# Search keywords and crawl posts with comments
uv run main.py --platform xhs --lt qrcode --type search

# Crawl specified post/video IDs from configuration
uv run main.py --platform xhs --lt qrcode --type detail

# Save data into SQLite database (recommended for personal use)
uv run main.py --platform xhs --lt qrcode --type search --save_data_option sqlite

# Save data into MySQL database
uv run main.py --platform xhs --lt qrcode --type search --save_data_option db

# View all available CLI arguments
uv run main.py --help
```

## Alternative: Python Native `venv`
> If crawling Douyin or Zhihu, ensure Node.js `>= 16` is installed.
```shell
# Navigate to project root directory
cd MediaCrawler

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Run crawler
python main.py --platform xhs --lt qrcode --type search
```
