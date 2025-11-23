import time
from typing import Callable, Optional, Tuple, Any
import undetected_chromedriver as uc
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from config import (
    PAGE_LOAD_TIMEOUT,
    WEBDRIVER_WAIT_TIMEOUT,
    PAGE_LOAD_DELAY,
    PAGE_ERROR_WAIT,
    RETRY_ATTEMPTS
)


def create_driver() -> Tuple[WebDriver, WebDriverWait]:
    """Creates and configures Chrome WebDriver instance."""
    import os
    
    options = uc.ChromeOptions()
    options.add_argument('--lang=nl-NL')
    
    # Headless mode for Docker/CI environments
    if os.getenv('DOCKER_ENV') or not os.getenv('DISPLAY'):
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
    else:
        options.add_argument('--start-maximized')
    
    driver = uc.Chrome(options=options, version_main=None)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    wait = WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT)
    
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
