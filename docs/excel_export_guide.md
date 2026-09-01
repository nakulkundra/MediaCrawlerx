# Excel Export Guide

## Overview

MediaCrawler supports exporting crawled data to formatted Excel files (`.xlsx`) with professional styling and multiple sheets for contents, comments, and creators.

## Features

- **Multi-sheet workbooks**: Separate sheets for Contents, Comments, and Creators
- **Professional formatting**:
  - Styled headers with clean background and clear text
  - Auto-adjusted column widths
  - Cell borders and text wrapping
  - Clean, readable layout
- **Smart export**: Empty sheets are automatically removed
- **Organized storage**: Files saved to `data/{platform}/` directory with timestamps

## Installation

Excel export requires the `openpyxl` library:

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install openpyxl
```

## Usage

### Basic Usage

1. **Configure Excel export** in `config/base_config.py`:

```python
SAVE_DATA_OPTION = "excel"  # Change from jsonl/json/csv/db to excel
```

2. **Run the crawler**:

```bash
# Xiaohongshu example
uv run main.py --platform xhs --lt qrcode --type search

# Douyin example
uv run main.py --platform dy --lt qrcode --type search

# Bilibili example
uv run main.py --platform bili --lt qrcode --type search
```

3. **Find your Excel file** in `data/{platform}/` directory:
   - Filename format: `{platform}_{crawler_type}_{timestamp}.xlsx`
   - Example: `xhs_search_20250128_143025.xlsx`

### Command Line Examples

```bash
# Search by keywords and export to Excel
uv run main.py --platform xhs --lt qrcode --type search --save_data_option excel

# Crawl specific posts and export to Excel
uv run main.py --platform xhs --lt qrcode --type detail --save_data_option excel

# Crawl creator profile and export to Excel
uv run main.py --platform xhs --lt qrcode --type creator --save_data_option excel
```

## Excel File Structure

### Contents Sheet
Contains post/video information:
- `note_id`: Unique post identifier
- `title`: Post title
- `desc`: Post description
- `user_id`: Author user ID
- `nickname`: Author nickname
- `liked_count`: Number of likes
- `comment_count`: Number of comments
- `share_count`: Number of shares
- `ip_location`: IP location
- `image_list`: Comma-separated image URLs
- `tag_list`: Comma-separated tags
- `note_url`: Direct link to post
- And additional platform-specific metadata...

### Comments Sheet
Contains comment information:
- `comment_id`: Unique comment identifier
- `note_id`: Associated post ID
- `content`: Comment text
- `user_id`: Commenter user ID
- `nickname`: Commenter nickname
- `like_count`: Comment likes
- `create_time`: Comment timestamp
- `ip_location`: Commenter IP location

### Creators Sheet
Contains creator profile details:
- `user_id`: Unique creator ID
- `nickname`: Creator nickname
- `avatar`: Profile picture URL
- `desc`: Biography / bio description
- `gender`: Gender
- `fans`: Follower / fan count
- `follows`: Following count
- `notes_count`: Number of published posts / videos
