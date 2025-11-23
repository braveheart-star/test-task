from typing import Dict, List, Any, Optional
from browser import create_driver, navigate_to_page, retry_extraction
from extractors import get_product_price, get_product_ean
from url_extractor import extract_product_urls_from_category
from file_handler import save_result_to_excel
from config import (
    RETRY_DELAY,
    COL_PRODUCT_URL,
    COL_EAN,
    COL_PRICE,
    DEFAULT_OUTPUT_FILE,
    DEFAULT_START_PAGE,
    DEFAULT_MAX_PAGES
)


def scrape_category_products(
    category_url: str,
    output_file: str = DEFAULT_OUTPUT_FILE,
    start_page: int = DEFAULT_START_PAGE,
    max_pages: Optional[int] = DEFAULT_MAX_PAGES
) -> None:
    """Scrapes products from a category page, extracts EAN and price, saves to Excel."""
    driver, wait = create_driver()
    products_data = []
    
    try:
        product_urls = extract_product_urls_from_category(
            category_url, driver, wait, start_page=start_page, max_pages=max_pages
        )
        
        if not product_urls:
            return
        
        stats = _extract_product_details(driver, wait, product_urls)
        products_data = stats['products_data']
        
        if stats['failed_products']:
            _retry_failed_products(driver, wait, stats)
        
        save_result_to_excel(products_data, output_file)
        
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def _extract_product_details(
    driver, wait, product_urls: List[str]
) -> Dict[str, Any]:
    products_data = []
    failed_products = []
    products_dict = {}
    missing_ean_count = 0
    missing_price_count = 0
    error_count = 0
    
    for product_url in product_urls:
        try:
            navigate_to_page(driver, product_url)
            
            price = retry_extraction(get_product_price, driver, wait)
            ean = retry_extraction(get_product_ean, driver, wait)
            
            if not price:
                missing_price_count += 1
            if not ean:
                missing_ean_count += 1
            
            if not price or not ean:
                failed_products.append(product_url)
                if not price and not ean:
                    error_count += 1
            
            product_data = {
                COL_PRODUCT_URL: product_url,
                COL_EAN: ean if ean else '',
                COL_PRICE: price if price else ''
            }
            products_data.append(product_data)
            products_dict[product_url] = product_data
                
        except Exception:
            error_count += 1
            failed_products.append(product_url)
            product_data = {
                COL_PRODUCT_URL: product_url,
                COL_EAN: '',
                COL_PRICE: ''
            }
            products_data.append(product_data)
            products_dict[product_url] = product_data
    
    return {
        'products_data': products_data,
        'products_dict': products_dict,
        'failed_products': failed_products,
        'missing_ean_count': missing_ean_count,
        'missing_price_count': missing_price_count,
        'error_count': error_count
    }


def _retry_failed_products(driver, wait, stats: Dict[str, Any]) -> None:
    failed_products = stats['failed_products']
    products_dict = stats['products_dict']
    missing_ean_count = stats['missing_ean_count']
    missing_price_count = stats['missing_price_count']
    
    for product_url in failed_products:
        try:
            navigate_to_page(driver, product_url, delay=RETRY_DELAY)
            product = products_dict.get(product_url)
            if not product:
                continue
            
            if not product[COL_PRICE]:
                price = retry_extraction(get_product_price, driver, wait)
                if price:
                    product[COL_PRICE] = price
                    missing_price_count -= 1
            
            if not product[COL_EAN]:
                ean = retry_extraction(get_product_ean, driver, wait)
                if ean:
                    product[COL_EAN] = ean
                    missing_ean_count -= 1
                    
        except Exception:
            pass
    
    stats['missing_ean_count'] = missing_ean_count
    stats['missing_price_count'] = missing_price_count
