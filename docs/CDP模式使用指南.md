# CDP Mode User Guide

## Overview

CDP (Chrome DevTools Protocol) mode is an advanced anti-detection scraping technique that controls an existing Chrome/Edge browser instance. Compared to traditional Playwright automation, CDP mode offers key advantages:

### 🎯 Key Advantages

1. **Real Browser Environment**: Uses your actual installed browser, including extensions, plugins, and custom configurations.
2. **Superior Anti-Detection**: Generates genuine browser fingerprints that are difficult for platforms to flag as automation bots.
3. **Preserves User State**: Automatically inherits user login sessions, cookies, and browsing history.
4. **Extension Support**: Leverages installed ad blockers, proxy switchers, and developer tools.
5. **Natural Behavior**: Emulates realistic human browsing behaviors.

### 📌 Two CDP Modes

CDP mode supports two operation modes:

| Mode | Description | Recommended Scenarios |
|------|-------------|-----------------------|
| **Connect to Existing Browser** (Default / Recommended) | Connects to an already running Chrome browser, reusing cookies, extensions, and history | High anti-crawler protection, minimizing risk of account flags |
| **Launch New Browser** | Automatically detects and launches a fresh Chrome/Edge browser instance | Scenarios where browser state reuse is not required |

## Quick Start

### Method 1: Connect to Existing Browser (Recommended)

This is the **default and recommended** method. Directly connects to your active Chrome browser for optimal anti-detection.

#### Step 1: Verify Chrome Version

Requires Chrome **144 or newer**. Enter `chrome://version` in the address bar to check your version.

If your version is older, download the latest version from the [Chrome Official Website](https://www.google.com/chrome/).

#### Step 2: Enable Remote Debugging

1. In Chrome address bar, open: `chrome://inspect/#remote-debugging`
2. Check the box **"Allow remote debugging for this browser instance"**
3. The page will display `Server running at: 127.0.0.1:9222`, indicating readiness.

#### Step 3: Run the Crawler

```bash
uv run main.py --platform xhs --lt qrcode --type search
```

When started, Chrome will show a confirmation prompt. Click "Accept". The crawler waits for confirmation (default 60s timeout).

#### Configuration Details

Default settings in `config/base_config.py`:

```python
# Enable CDP mode
ENABLE_CDP_MODE = True

# Connect to existing browser (default: enabled)
CDP_CONNECT_EXISTING = True

# CDP debugging port (matching the port in chrome://inspect)
CDP_DEBUG_PORT = 9222
```

### Method 2: Launch New Browser

To launch a fresh browser instance instead of attaching to an existing one:

```python
ENABLE_CDP_MODE = True
CDP_CONNECT_EXISTING = False  # Disable connecting to existing; launch new instance instead
```

## Configuration Options

### Basic Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ENABLE_CDP_MODE` | bool | True | Whether to enable CDP mode |
| `CDP_CONNECT_EXISTING` | bool | True | Whether to connect to existing browser (Recommended) |
| `CDP_DEBUG_PORT` | int | 9222 | CDP debugging port |
| `CDP_HEADLESS` | bool | False | Headless mode under CDP |
| `AUTO_CLOSE_BROWSER` | bool | True | Whether to close browser on completion |

### Advanced Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `CUSTOM_BROWSER_PATH` | str | "" | Custom browser executable path (New browser mode only) |
| `BROWSER_LAUNCH_TIMEOUT` | int | 60 | Browser connection timeout in seconds |

### Custom Browser Path

If automatic detection cannot locate your browser, specify the path manually:

```python
# Windows Example
CUSTOM_BROWSER_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# macOS Example
CUSTOM_BROWSER_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Linux Example
CUSTOM_BROWSER_PATH = "/usr/bin/google-chrome"
```

## Supported Browsers

### Windows
- Google Chrome (Stable, Beta, Dev, Canary)
- Microsoft Edge

### macOS
- Google Chrome (Stable, Beta, Dev, Canary)
- Microsoft Edge
- Chromium

### Linux
- Google Chrome (Stable, Beta, Unstable)
- Chromium
