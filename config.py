from typing import Final

PAGE_LOAD_TIMEOUT: Final[int] = 30
WEBDRIVER_WAIT_TIMEOUT: Final[int] = 15
RETRY_ATTEMPTS: Final[int] = 2
PAGE_LOAD_DELAY: Final[float] = 1.0
RETRY_DELAY: Final[float] = 2.0
SHOW_MORE_WAIT: Final[float] = 3.0
SCROLL_WAIT: Final[float] = 0.5
PAGE_ERROR_WAIT: Final[float] = 2.0

BOL_BASE_URL: Final[str] = 'https://www.bol.com'
PRODUCT_URL_PATH: Final[str] = '/nl/nl/p/'
CATEGORY_URL_PATH: Final[str] = '/nl/nl/l/'

EAN_PATTERN: Final[str] = r'EAN[:\s\-]*(\d{8,14})'

SELECTOR_PRICE: Final[str] = 'span[data-test="price"]'
SELECTOR_PRICE_FRACTION: Final[str] = 'sup[data-test="price-fraction"]'
SELECTOR_SPEC_SECTION: Final[str] = 'section[data-group-name="ProductSpecification"]'
SELECTOR_SHOW_MORE: Final[str] = 'a[data-test="show-more"]'
SELECTOR_SPEC_ROW: Final[str] = 'div.specs__row'
SELECTOR_SPEC_TITLE: Final[str] = 'dt.specs__title'
SELECTOR_SPEC_VALUE: Final[str] = 'dd.specs__value'
SELECTOR_PAGINATION: Final[str] = 'div[data-testid="pagination"]'
SELECTOR_PRODUCT_LINK: Final[str] = 'a[href*="/nl/nl/p/"]'

COL_PRODUCT_URL: Final[str] = 'Product URL'
COL_EAN: Final[str] = 'EAN'
COL_PRICE: Final[str] = 'Price'

DEFAULT_OUTPUT_FILE: Final[str] = 'bol_products.xlsx'
DEFAULT_START_PAGE: Final[int] = 1
DEFAULT_MAX_PAGES: Final[int] = 2
