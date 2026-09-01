# MediaCrawler Architecture Guide

## 1. Overview

### 1.1 Introduction

MediaCrawler is a multi-platform social media crawling framework built using Python asynchronous programming. It supports scraping contents, comments, and creator profiles across major social media platforms.

### 1.2 Supported Platforms

| Platform | Code | Main Capabilities |
|----------|------|-------------------|
| Xiaohongshu | `xhs` | Note search, note details, creator profiles |
| Douyin | `dy` | Video search, video details, creator profiles |
| Kuaishou | `ks` | Video search, video details, creator profiles |
| Bilibili | `bili` | Video search, video details, UP master profiles |
| Weibo | `wb` | Post search, post details, blogger profiles |
| Baidu Tieba | `tieba` | Post search, post details |
| Zhihu | `zhihu` | Q&A search, answer details, author profiles |

### 1.3 Core Features

- **Multi-Platform Support**: Unified crawler interfaces for 7 major social media platforms.
- **Multiple Login Methods**: QR Code, Mobile SMS, and Cookie authentication.
- **Versatile Storage Options**: CSV, JSON, JSONL, SQLite, MySQL, PostgreSQL, MongoDB, and Excel formats.
- **Anti-Bot Countermeasures**: CDP mode, rotating IP proxy pool, and request signing engines.
- **Asynchronous Concurrency**: Built on `asyncio` for high-throughput concurrent scraping.
- **Word Cloud Generation**: Automated visualization for comment text analysis.

---

## 2. System Architecture

### 2.1 High-Level Architecture

```mermaid
flowchart TB
    subgraph Entry["Entry Layer"]
        main["main.py<br/>Application Entry"]
        cmdarg["cmd_arg<br/>CLI Arguments"]
        config["config<br/>Config Management"]
    end

    subgraph Core["Core Crawler Layer"]
        factory["CrawlerFactory<br/>Crawler Factory"]
        base["AbstractCrawler<br/>Base Crawler"]

        subgraph Platforms["Platform Implementations"]
            xhs["XiaoHongShuCrawler"]
            dy["DouYinCrawler"]
            ks["KuaishouCrawler"]
            bili["BilibiliCrawler"]
            wb["WeiboCrawler"]
            tieba["TieBaCrawler"]
            zhihu["ZhihuCrawler"]
        end
    end

    subgraph Client["API Client Layer"]
        absClient["AbstractApiClient<br/>Base Client"]
        xhsClient["XiaoHongShuClient"]
        dyClient["DouYinClient"]
        ksClient["KuaiShouClient"]
        biliClient["BilibiliClient"]
        wbClient["WeiboClient"]
        tiebaClient["BaiduTieBaClient"]
        zhihuClient["ZhiHuClient"]
    end

    subgraph Storage["Data Storage Layer"]
        storeFactory["StoreFactory<br/>Storage Factory"]
        csv["CSV Storage"]
        json["JSON Storage"]
        sqlite["SQLite Storage"]
        mysql["MySQL Storage"]
        mongodb["MongoDB Storage"]
        excel["Excel Storage"]
    end

    subgraph Infra["Infrastructure Layer"]
        browser["Browser Management<br/>Playwright / CDP"]
        proxy["Proxy IP Pool"]
        cache["Cache System"]
        login["Login Management"]
    end

    main --> factory
    cmdarg --> main
    config --> main
    factory --> base
    base --> Platforms
    Platforms --> Client
    Client --> Storage
    Client --> Infra
    Storage --> storeFactory
    storeFactory --> csv & json & sqlite & mysql & mongodb & excel
```

### 2.2 Data Flow

```mermaid
flowchart LR
    subgraph Input["Input"]
        keywords["Keywords / IDs"]
        config["Configuration"]
    end

    subgraph Process["Processing Flow"]
        browser["Launch Browser"]
        login["Authenticate"]
        search["Search / Crawl"]
        parse["Parse Data"]
        comment["Fetch Comments"]
    end

    subgraph Output["Output"]
        content["Content Data"]
        comments["Comments Data"]
        creator["Creator Profiles"]
        media["Media Files"]
    end

    subgraph Storage["Storage"]
        file["Files<br/>CSV / JSON / Excel"]
        db["Database<br/>SQLite / MySQL / PG"]
        nosql["NoSQL<br/>MongoDB"]
    end

    keywords --> browser
    config --> browser
    browser --> login
    login --> search
    search --> parse
    parse --> comment
    parse --> content
    comment --> comments
    parse --> creator
    parse --> media
    content & comments & creator --> file & db & nosql
    media --> file
```

---

## 3. Directory Layout

```
MediaCrawler/
├── main.py                 # Application entry point
├── var.py                  # Global context variables
├── pyproject.toml          # Project configuration & dependencies
│
├── base/                   # Abstract base classes
│   └── base_crawler.py     # Base crawler, login, store, and client definitions
│
├── config/                 # Configuration management
│   ├── base_config.py      # Core crawler settings
│   ├── db_config.py        # Database settings
│   └── {platform}_config.py # Platform-specific settings
│
├── media_platform/         # Platform crawler implementations
│   ├── xhs/                # Xiaohongshu
│   ├── douyin/             # Douyin
│   ├── kuaishou/           # Kuaishou
│   ├── bilibili/           # Bilibili
│   ├── weibo/              # Weibo
│   ├── tieba/              # Baidu Tieba
│   └── zhihu/              # Zhihu
│
├── store/                  # Data storage layer
│   ├── excel_store_base.py # Excel export base
│   └── {platform}/         # Platform-specific storage handlers
│
├── database/               # Relational & NoSQL database models
│   ├── models.py           # SQLAlchemy ORM models
│   ├── db_session.py       # Session management
│   └── mongodb_store_base.py # MongoDB storage base
│
├── proxy/                  # Proxy management
│   ├── proxy_ip_pool.py    # IP pool manager
│   ├── proxy_mixin.py      # Proxy refresh mixin
│   └── providers/          # Third-party proxy vendors (Kuaidaili, Wandou)
│
├── cache/                  # Caching engines
│   ├── abs_cache.py        # Abstract cache base
│   ├── local_cache.py      # Memory-based LRU/TTL cache
│   └── redis_cache.py      # Redis cache
│
├── tools/                  # Utility modules
│   ├── app_runner.py       # Application lifecycle runner
│   ├── browser_launcher.py # Playwright browser launcher
│   ├── cdp_browser.py      # CDP browser manager
│   ├── crawler_util.py     # Helper utilities
│   └── async_file_writer.py # Asynchronous buffered file writer
│
├── model/                  # Data models
│   └── m_{platform}.py     # Pydantic schemas
│
├── libs/                   # JavaScript libraries
│   └── stealth.min.js      # Playwright anti-detection script
│
└── cmd_arg/                # Command line argument parser
    └── arg.py              # CLI definitions
```

---

## 4. Core Class Hierarchy

```mermaid
classDiagram
    class AbstractCrawler {
        <<abstract>>
        +start()*
        +search()*
        +launch_browser()
        +launch_browser_with_cdp()
    }

    class AbstractLogin {
        <<abstract>>
        +begin()*
        +login_by_qrcode()*
        +login_by_mobile()*
        +login_by_cookies()*
    }

    class AbstractStore {
        <<abstract>>
        +store_content()*
        +store_comment()*
        +store_creator()*
        +store_image()*
        +store_video()*
    }

    class AbstractApiClient {
        <<abstract>>
        +request()*
        +update_cookies()*
    }

    class ProxyRefreshMixin {
        +init_proxy_pool()
        +_refresh_proxy_if_expired()
    }

    class XiaoHongShuCrawler {
        +xhs_client: XiaoHongShuClient
        +start()
        +search()
        +get_specified_notes()
        +get_creators_and_notes()
    }

    class XiaoHongShuClient {
        +playwright_page: Page
        +cookie_dict: dict
        +get_note_by_id()
        +get_comments()
        +get_creator_info()
    }

    AbstractCrawler <|-- XiaoHongShuCrawler
    AbstractApiClient <|-- XiaoHongShuClient
    ProxyRefreshMixin <|-- XiaoHongShuClient
    XiaoHongShuCrawler --> XiaoHongShuClient
```
