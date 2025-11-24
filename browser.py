import time
import random
from typing import Callable, Optional, Tuple, Any
import undetected_chromedriver as uc
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from config import (
    PAGE_LOAD_TIMEOUT,
    WEBDRIVER_WAIT_TIMEOUT,
    PAGE_LOAD_DELAY,
    PAGE_ERROR_WAIT,
    RETRY_ATTEMPTS,
    BOL_BASE_URL
)


def create_driver() -> Tuple[WebDriver, WebDriverWait]:
    """Creates and configures Chrome WebDriver instance."""
    options = uc.ChromeOptions()
    options.add_argument('--lang=nl-NL')
    options.add_argument('--start-maximized')
    
    driver = uc.Chrome(options=options, version_main=None)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT)
    
    navigate_to_page(driver, BOL_BASE_URL, delay=random.uniform(3, 5))
    
    # Stealth: Human-like scrolling to avoid bot detection
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
    time.sleep(random.uniform(1, 2))
    
    # Stealth: Initialize by visiting bol.com homepage first (anti-bot detection)
    
    return driver, wait


def navigate_to_page(driver: WebDriver, page_url: str, delay: float = PAGE_LOAD_DELAY) -> bool:
    """Navigates to a page with error handling."""
    try:
        driver.get(page_url)
        time.sleep(delay)
        return True
    except Exception as e:
        print(f"Navigation failed for {page_url}: {e}")
        time.sleep(PAGE_ERROR_WAIT)
        return False


def retry_extraction(
    extraction_func: Callable[[WebDriver, WebDriverWait], Any],
    driver: WebDriver,
    wait: WebDriverWait,
    max_attempts: int = RETRY_ATTEMPTS
) -> Optional[Any]:
    """Retries extraction function with delays until success or max attempts."""
    for attempt in range(max_attempts):
        result = extraction_func(driver, wait)
        if result:
            return result
        if attempt < max_attempts - 1:
            time.sleep(PAGE_LOAD_DELAY)
    return None
