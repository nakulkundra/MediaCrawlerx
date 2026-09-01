# Kuaidaili Proxy Integration Guide

## Overview
Kuaidaili proxy service integration supports personal and enterprise rotating proxy pools.

## 1. Prepare Proxy Information
Register and complete verification on the [Kuaidaili Website](https://www.kuaidaili.com/).

## 2. Obtain API Key Information
Obtain your secret ID, secret key, and endpoint credentials from the dashboard.

Choose **Private Rotating Proxy** (私密代理).

## 3. Initialize Proxy Provider

Configure your provider in `config/base_config.py` or directly in `proxy/providers/kuai_daili_proxy.py`:

```python
# proxy/providers/kuai_daili_proxy.py
def new_kuaidaili_proxy(
    secret_id: str,
    signature: str,
    order_id: str,
    api_url: str = "https://dps.kdlapi.com/api/getdps/"
):
    """
    Initialize Kuaidaili proxy provider instance
    """
    ...
```

Enable proxy pool in `config/base_config.py`:
```python
ENABLE_IP_PROXY = True
IP_PROXY_POOL_COUNT = 2
```
