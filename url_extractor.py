import logging
from typing import List, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urljoin

from config import (
    BOL_BASE_URL,
    PRODUCT_URL_PATH,
    CATEGORY_URL_PATH,
    SELECTOR_PAGINATION,
    SELECTOR_PRODUCT_LINK
)
from browser import navigate_to_page

logger = logging.getLogger('bol_scraper')


def extract_all_page_urls_from_pagination(driver: WebDriver) -> List[str]:
    """Extracts all page URLs from pagination by finding max page number."""
    page_urls = []
    try:
        current_url = driver.current_url
        base_url = current_url.split('?')[0]
        
        max_page = _get_max_page_number(driver)
        
        page_urls.append(base_url)
        page_urls.extend(f"{base_url}?page={num}" for num in range(2, max_page + 1))
        
    except Exception:
        try:
            current_url = driver.current_url
            base_url = current_url.split('?')[0]
            if base_url and base_url not in page_urls:
                page_urls.append(base_url)
        except Exception:
            pass
    
    return page_urls


def _get_max_page_number(driver: WebDriver) -> int:
    try:
        pagination_div = driver.find_element(By.CSS_SELECTOR, SELECTOR_PAGINATION)
        ul_element = pagination_div.find_element(By.TAG_NAME, 'ul')
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
        
        for li in reversed(li_elements):
            try:
                link = li.find_element(By.TAG_NAME, 'a')
                href = link.get_attribute('href')
                if href and '?page=' in href:
                    page_num_str = href.split('?page=')[1].split('&')[0]
                    return int(page_num_str)
            except Exception:
                continue
    except Exception:
        pass
    
    return 1


def extract_product_urls(driver: WebDriver, wait: WebDriverWait, page_url: str) -> List[str]:
    """Extracts product URLs from a single category page."""
    try:
        if not navigate_to_page(driver, page_url):
            return []
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_PRODUCT_LINK)))
        
        product_links = driver.find_elements(By.CSS_SELECTOR, SELECTOR_PRODUCT_LINK)
        product_urls = []
        
        for link in product_links:
            try:
                href = link.get_attribute('href')
                if href:
                    full_url = urljoin(BOL_BASE_URL, href)
                    clean_url = full_url.split('?')[0]
                    
                    if PRODUCT_URL_PATH in clean_url and CATEGORY_URL_PATH not in clean_url:
                        product_urls.append(clean_url)
            except Exception:
                continue
        
        return list(dict.fromkeys(product_urls))
        
    except Exception:
        return []


def extract_product_urls_from_category(
    category_url: str,
    driver: WebDriver,
    wait: WebDriverWait,
    start_page: int = 1,
    max_pages: Optional[int] = 2
) -> List[str]:
    """Extracts all product URLs from a category page, handling pagination."""
    all_product_urls = set()
    
    try:
        logger.debug(f"Navigating to category: {category_url}")
        if not navigate_to_page(driver, category_url):
            logger.warning(f"Failed to navigate to category: {category_url}")
            return []
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_PRODUCT_LINK)))
        
        page_urls = extract_all_page_urls_from_pagination(driver)
        total_pages = len(page_urls)
        logger.info(f"Found {total_pages} page(s) in category")
        
        start_page = max(1, start_page)
        if start_page > total_pages:
            logger.warning(f"start_page ({start_page}) exceeds total pages ({total_pages})")
            return []
        
        end_page = total_pages if max_pages is None else min(start_page + max_pages - 1, total_pages)
        page_urls_to_process = page_urls[start_page - 1:end_page]
        logger.info(f"Processing pages {start_page} to {end_page} ({len(page_urls_to_process)} page(s))")
        
        for idx, page_url in enumerate(page_urls_to_process, start=start_page):
            logger.debug(f"Extracting products from page {idx}/{end_page}")
            page_product_urls = extract_product_urls(driver, wait, page_url)
            all_product_urls.update(page_product_urls)
            logger.debug(f"Found {len(page_product_urls)} products on page {idx} (Total: {len(all_product_urls)})")
        
        logger.info(f"Total unique product URLs extracted: {len(all_product_urls)}")
        return list(all_product_urls)
        
    except Exception as e:
        logger.error(f"Error extracting product URLs: {e}", exc_info=True)
        return list(all_product_urls)
