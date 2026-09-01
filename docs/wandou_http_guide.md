# Wandou HTTP Proxy Integration Guide

## Overview
Wandou HTTP Proxy integration guide for enterprise dynamic IP rotating proxies.

## 1. Register & Verify
Sign up on the [Wandou HTTP Proxy Website](https://h.wandouip.com).

## 2. Obtain AppKey
Obtain your API AppKey from your Wandou dashboard.

## 3. Initialize Wandou Proxy Provider

```python
# proxy/providers/wandou_http_proxy.py
def new_wandou_proxy(app_key: str):
    """
    Initialize Wandou HTTP proxy provider instance
    """
    ...
```

Enable proxy in `config/base_config.py`:
```python
ENABLE_IP_PROXY = True
IP_PROXY_POOL_COUNT = 2
```
