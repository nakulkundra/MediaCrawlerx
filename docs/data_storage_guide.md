# Data Storage Guide

### 💾 Data Storage

MediaCrawler supports multiple data storage options. You can choose the most suitable solution based on your requirements:

#### Storage Options

- **CSV Files**: Supports saving to CSV format (under the `data/` directory)
- **JSON Files**: Supports saving to JSON format (under the `data/` directory)
- **JSONL Files**: Supports saving to JSONL format (under the `data/` directory) — Default format, one JSON object per line, excellent append performance
- **Excel Files**: Supports saving to formatted Excel files (under the `data/` directory) ✨ Feature
  - Multi-worksheet support (content, comments, creators)
  - Professional formatting (header styling, auto-column widths, cell borders)
  - Easy for analysis and reporting
- **Database Storage**:
  - Use the `--init_db` flag to initialize the database (no other optional parameters needed when initializing)
  - **SQLite Database**: Lightweight database, zero configuration, ideal for personal use (Recommended)
    1. Initialize: `python main.py --init_db sqlite`
    2. Save data: `python main.py --save_data_option sqlite`
  - **MySQL Database**: Supports relational databases for enterprise and multi-user environments
    1. Configure connection settings in `config/db_config.py`
    2. Initialize: `python main.py --init_db mysql`
    3. Save data: `python main.py --save_data_option mysql`
  - **MongoDB Database**: Document database suited for flexible JSON schemas
    1. Configure connection settings in `config/db_config.py`
    2. Save data: `python main.py --save_data_option mongodb`
  - **PostgreSQL Database**:
    1. Configure connection settings in `config/db_config.py`
    2. Initialize: `python main.py --init_db pgsql`
    3. Save data: `python main.py --save_data_option pgsql`
