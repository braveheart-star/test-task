# Bol.com Product Scraper

A web scraping tool that extracts product information (URL, EAN code, and price) from bol.com category pages and saves the results to an Excel file.

## Docker Configuration

The scraper supports configuration via environment variables for Docker deployment. However, **scraping cannot be fully implemented in Docker** due to anti-bot detection mechanisms.

### Environment Variables

- **START_PAGE**: The first page to scrape (default: `1`)
- **MAX_PAGES**: Maximum number of pages to scrape per category (default: `2`, use `None` for all pages)
- **OUTPUT_PATH**: Where the generated Excel file will be written (default: `/app/bol_products.xlsx`)
- **LOG_LEVEL**: Logging level - `INFO`, `DEBUG`, or `ERROR` (default: `INFO`)
- **CATEGORY_URLS**: Comma-separated list of category URLs to scrape (default: empty)

### Docker Compose Example

```yaml
version: '3.8'

services:
  scraper:
    build: .
    container_name: bol-scraper
    volumes:
      - .:/app
    environment:
      - START_PAGE=1
      - MAX_PAGES=2
      - OUTPUT_PATH=/app/bol_products.xlsx
      - LOG_LEVEL=INFO
      - CATEGORY_URLS=https://www.bol.com/nl/nl/l/analoge-instantcamera-s/20974/,https://www.bol.com/nl/nl/l/vlekkenreinigers-waterniveau-indicator/68305/
    shm_size: '2gb'
    restart: "no"
```

## Why Scraping Cannot Be Implemented in Docker

**The scraper cannot run effectively in Docker due to bol.com's anti-bot detection system.**

When running Chrome in Docker, you typically need to use headless mode (`--headless` flag) because Docker containers don't have a display server. However, **headless browsers are easily detected by modern anti-bot systems** like those used by bol.com.

### Detection Mechanisms

Headless browsers expose several indicators that anti-bot systems use to identify automated browsers:

1. **`navigator.webdriver` property**: Set to `true` in headless mode
2. **Missing browser plugins and extensions**: Headless browsers lack typical user-installed extensions
3. **Different user agent patterns**: Headless mode often has different user agent signatures
4. **Absence of typical browser behaviors**: Missing mouse movements, realistic timing, and interaction patterns
5. **Canvas fingerprinting differences**: Headless browsers produce different canvas fingerprints
6. **WebGL vendor/renderer mismatches**: WebGL parameters differ in headless mode

### The Solution

The scraper uses `undetected-chromedriver` which bypasses some detection mechanisms, but it **must run in non-headless mode** (with a visible browser window) to effectively avoid detection. This requires:

- A display server (X server on Linux, native display on Windows/Mac)
- Browser window visibility
- Human-like interaction patterns (scrolling, delays)

### Why Docker Doesn't Work

Docker containers typically:
- Don't have a display server
- Require headless mode (`--headless` flag)
- Cannot show browser windows
- Are easily detected by anti-bot systems when using headless mode

Even with `undetected-chromedriver`, running in headless mode within Docker triggers bol.com's anti-bot detection, causing blocked requests, CAPTCHA challenges, rate limiting, and failed page loads.

### Recommended Approach

**Run the scraper locally** (not in Docker) where:
- The browser can run in non-headless mode (maximized window)
- `undetected-chromedriver` can effectively bypass detection
- Human-like behaviors (scrolling, random delays) work naturally
- The scraper appears as a regular browser session

The Docker configuration is provided for reference and environment variable management, but **the actual scraping should be performed in a local environment** where the browser can run in non-headless mode.
