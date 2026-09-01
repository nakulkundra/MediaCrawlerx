# Local Native Environment Setup Guide

## Recommended Solution: Managing Dependencies with `uv`

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
# Comment scraping is disabled by default. Modify ENABLE_GET_COMMENTS in config/base_config.py if needed.
# All configuration toggles can be viewed and customized in config/base_config.py

# Search keywords and crawl posts with comments
uv run main.py --platform xhs --lt qrcode --type search

# Crawl specified post/video IDs from configuration
uv run main.py --platform xhs --lt qrcode --type detail

# Save data into SQLite database (recommended for personal use)
uv run main.py --platform xhs --lt qrcode --type search --save_data_option sqlite
```

## Alternative Solution: Python Native `venv`
> If crawling Douyin or Zhihu, ensure Node.js `>= 16` is installed.
```shell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Install Playwright browser drivers
playwright install

# Run crawler
python main.py --platform xhs --lt qrcode --type search
```
