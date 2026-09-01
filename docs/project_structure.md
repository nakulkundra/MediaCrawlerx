# Project Code Structure

```
MediaCrawler
├── base
│   └── base_crawler.py         # Abstract base classes for crawler, login, store, client
├── cache
│   ├── abs_cache.py            # Abstract cache interface
│   ├── cache_factory.py        # Cache factory
│   ├── local_cache.py          # In-memory local TTL cache implementation
│   └── redis_cache.py          # Redis cache implementation
├── cmd_arg
│   └── arg.py                  # CLI argument definitions
├── config
│   ├── base_config.py          # Core crawler configuration
│   ├── db_config.py            # Relational & NoSQL database configuration
│   └── ...                     # Platform-specific configuration files
├── constant
│   └── ...                     # Platform-specific constant definitions
├── database
│   ├── db.py                   # Database ORM wrappers (CRUD helpers)
│   ├── db_session.py           # Database session lifecycle management
│   ├── models.py               # SQLAlchemy ORM models
│   └── mongodb_store_base.py   # MongoDB storage base
├── docs
│   └── ...                     # Project documentation
├── libs
│   ├── stealth.min.js          # Playwright anti-detection script
│   └── ...                     # JavaScript signing libraries (Douyin, Zhihu)
├── media_platform
│   ├── bilibili/               # Bilibili crawler, client, login, field extractor
│   ├── douyin/                 # Douyin crawler, client, login, field extractor
│   ├── kuaishou/               # Kuaishou crawler, client, login, field extractor
│   ├── tieba/                  # Baidu Tieba crawler, client, login, field extractor
│   ├── weibo/                  # Weibo crawler, client, login, field extractor
│   ├── xhs/                    # Xiaohongshu crawler, client, login, field extractor
│   └── zhihu/                  # Zhihu crawler, client, login, field extractor
├── model
│   └── ...                     # Platform Pydantic data schemas
├── proxy
│   ├── proxy_ip_pool.py        # Proxy IP pool manager
│   ├── proxy_mixin.py          # Proxy refresh mixin
│   └── providers/              # Third-party proxy vendors (Kuaidaili, Wandou)
├── store
│   ├── excel_store_base.py     # Multi-worksheet Excel export engine
│   └── {platform}/             # Platform storage handlers (CSV, JSON, DB, Excel)
├── tools
│   ├── app_runner.py           # Application execution orchestrator
│   ├── async_file_writer.py    # Asynchronous buffered file writer
│   ├── browser_launcher.py     # Playwright browser launcher
│   ├── cdp_browser.py          # CDP browser manager
│   └── crawler_util.py         # Utility helper functions
├── webui/                      # Modern cyberpunk React web control panel
├── main.py                     # CLI entry point
└── var.py                      # Global context variables
```
