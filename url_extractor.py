"""
URL extraction functions for product and category pages.
"""

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


def extract_all_page_urls_from_pagination(driver: WebDriver) -> List[str]:
    """Extract all page URLs from pagination by finding max page number.
    
    Since pagination uses ellipsis (...) to hide some pages, we find the maximum
    page number from the last <li> element that contains an <a> tag and generate
    all page URLs manually.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        List of page URLs
    """
    page_urls = []
    try:
        current_url = driver.current_url
        base_url = current_url.split('?')[0]  # Remove query parameters
        
        # Find pagination and extract max page number
        max_page = _get_max_page_number(driver)
        
        # Generate URLs for all pages from 1 to max_page
        page_urls.append(base_url)  # Page 1 is the base URL without ?page= parameter
        page_urls.extend(f"{base_url}?page={num}" for num in range(2, max_page + 1))
        
    except Exception as e:
        print(f"Error extracting pagination: {e}")
        # Fallback: return at least the current page
        try:
            current_url = driver.current_url
            base_url = current_url.split('?')[0]
            if base_url and base_url not in page_urls:
                page_urls.append(base_url)
        except Exception:
            pass
    
    return page_urls


def _get_max_page_number(driver: WebDriver) -> int:
    """Extract maximum page number from pagination.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        Maximum page number (default: 1)
    """
    try:
        pagination_div = driver.find_element(By.CSS_SELECTOR, SELECTOR_PAGINATION)
        ul_element = pagination_div.find_element(By.TAG_NAME, 'ul')
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
        
        # Find the last li element that contains an <a> tag with href containing ?page=
        # Iterate in reverse to find the maximum page number quickly
        for li in reversed(li_elements):
            try:
                link = li.find_element(By.TAG_NAME, 'a')
                href = link.get_attribute('href')
                if href and '?page=' in href:
                    # Extract page number from URL like "?page=8"
                    page_num_str = href.split('?page=')[1].split('&')[0]
                    return int(page_num_str)
            except Exception:
                continue
    except Exception:
        pass
    
    return 1  # Default to page 1


def extract_product_urls(driver: WebDriver, wait: WebDriverWait, page_url: str) -> List[str]:
    """Extract product URLs from a single page.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        page_url: URL of the page to extract product URLs from
    
    Returns:
        List of product URLs found on the page
    """
    try:
        # Use consistent navigation function
        if not navigate_to_page(driver, page_url):
            return []
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_PRODUCT_LINK)))
        
        # Extract product URLs
        product_links = driver.find_elements(By.CSS_SELECTOR, SELECTOR_PRODUCT_LINK)
        product_urls = []
        
        for link in product_links:
            try:
                href = link.get_attribute('href')
                if href:
                    full_url = urljoin(BOL_BASE_URL, href)
                    clean_url = full_url.split('?')[0]
                    
                    # Only count actual product URLs (not category or other pages)
                    if PRODUCT_URL_PATH in clean_url and CATEGORY_URL_PATH not in clean_url:
                        product_urls.append(clean_url)
            except Exception:
                continue
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(product_urls))
        
    except Exception as e:
        print(f"Error extracting product URLs from {page_url}: {e}")
        return []


def extract_product_urls_from_category(
    category_url: str,
    driver: WebDriver,
    wait: WebDriverWait,
    start_page: int = 1,
    max_pages: Optional[int] = 2
) -> List[str]:
    """Extract all product URLs from a category page, handling pagination.
    
    Args:
        category_url: URL of the category page
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        start_page: Starting page number (1-indexed, default: 1)
        max_pages: Number of pages to scrape starting from start_page
                  (default: 2 for development, None for all pages)
    
    Returns:
        List of all unique product URLs from specified page range
    """
    all_product_urls = set()
    
    try:
        # Load first page to get all page URLs from pagination
        print(f"Loading category page: {category_url}")
        if not navigate_to_page(driver, category_url):
            print("Failed to load category page")
            return []
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_PRODUCT_LINK)))
        
        # Get all page URLs from pagination
        page_urls = extract_all_page_urls_from_pagination(driver)
        total_pages = len(page_urls)
        print(f"Found {total_pages} page(s) in pagination")
        
        # Validate and calculate page range
        start_page = max(1, start_page)  # Ensure start_page >= 1
        if start_page > total_pages:
            print(f"Warning: start_page ({start_page}) exceeds total pages ({total_pages}). No pages to process.")
            return []
        
        end_page = total_pages if max_pages is None else min(start_page + max_pages - 1, total_pages)
        page_urls_to_process = page_urls[start_page - 1:end_page]
        
        print(f"Processing pages {start_page} to {end_page} ({len(page_urls_to_process)} page(s))")
        
        # Extract product URLs from each page
        for idx, page_url in enumerate(page_urls_to_process, start=start_page):
            print(f"Page {idx}: {page_url}")
            
            page_product_urls = extract_product_urls(driver, wait, page_url)
            all_product_urls.update(page_product_urls)  # Use update() for better performance
            
            print(f"  Found {len(page_product_urls)} products (Total: {len(all_product_urls)})")
        
        return list(all_product_urls)
        
    except Exception as e:
        print(f"Error extracting product URLs: {e}")
        return list(all_product_urls)
