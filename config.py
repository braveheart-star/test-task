"""
Configuration constants for Bol.com scraper.
"""

# Timeout and delay constants
PAGE_LOAD_TIMEOUT = 30  # seconds
WEBDRIVER_WAIT_TIMEOUT = 15  # seconds
RETRY_ATTEMPTS = 2
PAGE_LOAD_DELAY = 1  # seconds
RETRY_DELAY = 2  # seconds
SHOW_MORE_WAIT = 3.0  # seconds
SCROLL_WAIT = 0.5  # seconds (wait after scrolling)
PAGE_ERROR_WAIT = 2  # seconds (wait when page load has errors)

# URL Constants
BOL_BASE_URL = 'https://www.bol.com'
PRODUCT_URL_PATH = '/nl/nl/p/'
CATEGORY_URL_PATH = '/nl/nl/l/'

# Regex Patterns
EAN_PATTERN = r'EAN[:\s\-]*(\d{8,14})'  # Pattern to match EAN codes (8-14 digits)
