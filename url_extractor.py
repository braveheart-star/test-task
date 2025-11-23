"""
URL extraction functions for product and category pages.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from config import BOL_BASE_URL, PRODUCT_URL_PATH, CATEGORY_URL_PATH


def extract_all_page_urls_from_pagination(driver):
    """Extract all page URLs from pagination by finding max page number from last li element.
    
    Since pagination uses ellipsis (...) to hide some pages, we find the maximum
    page number from the last <li> element that contains an <a> tag and generate all page URLs manually.
    """
    page_urls = []
    try:
        # Get current page URL to extract base URL
        current_url = driver.current_url
        base_url = current_url.split('?')[0]  # Remove query parameters
        
        # Find pagination div
        pagination_div = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="pagination"]')
        # Find ul element inside pagination
        ul_element = pagination_div.find_element(By.TAG_NAME, 'ul')
        # Find all li elements
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
        
        max_page = 1  # Default to page 1
        
        # Find the last li element that contains an <a> tag with href containing ?page=
        # Iterate in reverse to find the maximum page number quickly
        for li in reversed(li_elements):
            try:
                link = li.find_element(By.TAG_NAME, 'a')
                href = link.get_attribute('href')
                if href and '?page=' in href:
                    # Extract page number from URL like "?page=8"
                    page_num_str = href.split('?page=')[1].split('&')[0]
                    max_page = int(page_num_str)
                    break  # Found the last page link, exit loop
            except Exception:
                continue
        
        # Generate URLs for all pages from 1 to max_page
        page_urls.append(base_url)  # Page 1 is the base URL without ?page= parameter
        for page_num in range(2, max_page + 1):
            page_urls.append(f"{base_url}?page={page_num}")
        
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


def extract_product_urls(driver, wait, page_url):
    """Extract product URLs from a single page/link.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        page_url: URL of the page to extract product URLs from
    
    Returns:
        List of product URLs found on the page
    """
    product_urls = []
    
    try:
        driver.get(page_url)
        product_link_selector = f'a[href*="{PRODUCT_URL_PATH}"]'
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, product_link_selector)))
        
        # Extract product URLs
        product_links = driver.find_elements(By.CSS_SELECTOR, product_link_selector)
        
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
        
        # Remove duplicates while preserving order (Python 3.7+ dict maintains insertion order)
        return list(dict.fromkeys(product_urls))
        
    except Exception as e:
        print(f"Error extracting product URLs from {page_url}: {e}")
        return []


def extract_product_urls_from_category(category_url, driver, wait, start_page=1, max_pages=2):
    """Extract all product URLs from a category page, handling pagination.
    
    Args:
        category_url: URL of the category page
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        start_page: Starting page number (1-indexed, default: 1)
        max_pages: Number of pages to scrape starting from start_page (default: 2 for development, None for all pages)
    
    Returns:
        List of all unique product URLs from specified page range
    """
    all_product_urls = set()
    
    try:
        # Load first page to get all page URLs from pagination
        print(f"Loading category page: {category_url}")
        driver.get(category_url)
        product_link_selector = f'a[href*="{PRODUCT_URL_PATH}"]'
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, product_link_selector)))
        
        # Get all page URLs from pagination
        page_urls = extract_all_page_urls_from_pagination(driver)
        total_pages = len(page_urls)
        print(f"Found {total_pages} page(s) in pagination")
        
        # Validate start_page
        if start_page < 1:
            start_page = 1
        if start_page > total_pages:
            print(f"Warning: start_page ({start_page}) exceeds total pages ({total_pages}). No pages to process.")
            return []
        
        # Calculate end_page based on start_page + max_pages
        if max_pages is None:
            # Scrape all pages from start_page to end
            end_page = total_pages
        else:
            end_page = start_page + max_pages - 1
            end_page = min(end_page, total_pages)  # Cap at total available pages
        
        # Slice page_urls based on start_page and end_page (1-indexed to 0-indexed)
        page_urls_to_process = page_urls[start_page - 1:end_page]
        print(f"Processing pages {start_page} to {end_page} ({len(page_urls_to_process)} page(s))")
        
        # Extract product URLs from each page
        for idx, page_url in enumerate(page_urls_to_process, start=start_page):
            print(f"Page {idx}: {page_url}")
            
            # Extract product URLs from this page (function handles navigation)
            page_product_urls = extract_product_urls(driver, wait, page_url)
            page_products = len(page_product_urls)
            
            # Add to set to avoid duplicates
            for url in page_product_urls:
                all_product_urls.add(url)
            
            print(f"  Found {page_products} products (Total: {len(all_product_urls)})")
        
        return list(all_product_urls)
        
    except Exception as e:
        print(f"Error extracting product URLs: {e}")
        return list(all_product_urls)
