"""
Main scraper orchestration logic.
"""

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
    """Complete scraper: Extract all product URLs from category and get EAN + price for each.
    
    Args:
        category_url: URL of the category page
        output_file: Name of the Excel file to save results
        start_page: Starting page number (1-indexed, default: 1)
        max_pages: Number of pages to scrape starting from start_page
                  (default: 2 for development, None for all pages)
    """
    driver, wait = create_driver()
    products_data = []
    
    try:
        _print_section_header("PART 1: Extracting Product URLs from Category")
        print(f"Category URL: {category_url}")
        print(f"Start Page: {start_page}, Max Pages: {max_pages}")
        _print_section_footer()
        
        # Part 1: Extract all product URLs from specified page range
        product_urls = extract_product_urls_from_category(
            category_url, driver, wait, start_page=start_page, max_pages=max_pages
        )
        print(f"\nTotal product URLs found: {len(product_urls)}\n")
        
        if not product_urls:
            print("No products found. Exiting.")
            return
        
        _print_section_header("PART 2: Extracting Product Details (EAN and Price)")
        _print_section_footer()
        
        # Part 2: Extract details for each product
        stats = _extract_product_details(driver, wait, product_urls)
        products_data = stats['products_data']
        
        # Retry failed products
        if stats['failed_products']:
            _retry_failed_products(driver, wait, stats)
        
        # Print summary and save
        _print_summary(stats)
        save_result_to_excel(products_data, output_file)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def _extract_product_details(
    driver, wait, product_urls: List[str]
) -> Dict[str, Any]:
    """Extract product details (EAN and Price) for all products.
    
    Args:
        driver: WebDriver instance
        wait: WebDriverWait instance
        product_urls: List of product URLs to process
    
    Returns:
        Dictionary containing products_data, failed_products, and statistics
    """
    products_data = []
    failed_products = []
    products_dict = {}
    missing_ean_count = 0
    missing_price_count = 0
    error_count = 0
    
    for idx, product_url in enumerate(product_urls, 1):
        print(f"\n[{idx}/{len(product_urls)}] Processing: {product_url}")
        
        try:
            navigate_to_page(driver, product_url)
            
            # Extract price and EAN with retry
            price = retry_extraction(get_product_price, driver, wait)
            ean = retry_extraction(get_product_ean, driver, wait)
            
            # Update statistics
            if not price:
                missing_price_count += 1
                print(f"  Price: [MISSING]")
            if not ean:
                missing_ean_count += 1
                print(f"  EAN: [MISSING]")
            
            # Mark for retry if any field is missing
            if not price or not ean:
                failed_products.append(product_url)
                if not price and not ean:
                    error_count += 1
            
            # Create product data
            product_data = {
                COL_PRODUCT_URL: product_url,
                COL_EAN: ean if ean else '',
                COL_PRICE: price if price else ''
            }
            products_data.append(product_data)
            products_dict[product_url] = product_data
            
            if price:
                print(f"  Price: {price}")
            if ean:
                print(f"  EAN: {ean}")
                
        except Exception as e:
            error_count += 1
            print(f"  [ERROR] Processing product: {e}")
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
    """Retry extraction for failed products.
    
    Args:
        driver: WebDriver instance
        wait: WebDriverWait instance
        stats: Statistics dictionary from _extract_product_details
    """
    failed_products = stats['failed_products']
    products_dict = stats['products_dict']
    missing_ean_count = stats['missing_ean_count']
    missing_price_count = stats['missing_price_count']
    
    _print_section_header(f"Retrying {len(failed_products)} failed products...")
    _print_section_footer()
    
    for idx, product_url in enumerate(failed_products, 1):
        print(f"\n[RETRY {idx}/{len(failed_products)}] Processing: {product_url}")
        
        try:
            navigate_to_page(driver, product_url, delay=RETRY_DELAY)
            product = products_dict.get(product_url)
            if not product:
                continue
            
            # Retry price extraction
            if not product[COL_PRICE]:
                price = retry_extraction(get_product_price, driver, wait)
                if price:
                    product[COL_PRICE] = price
                    missing_price_count -= 1
                    print(f"  Price: {price} [RETRIEVED]")
            
            # Retry EAN extraction
            if not product[COL_EAN]:
                ean = retry_extraction(get_product_ean, driver, wait)
                if ean:
                    product[COL_EAN] = ean
                    missing_ean_count -= 1
                    print(f"  EAN: {ean} [RETRIEVED]")
                    
        except Exception as e:
            print(f"  [ERROR] Retry failed: {e}")
    
    # Update stats
    stats['missing_ean_count'] = missing_ean_count
    stats['missing_price_count'] = missing_price_count


def _print_summary(stats: Dict[str, Any]) -> None:
    """Print extraction summary statistics.
    
    Args:
        stats: Statistics dictionary
    """
    products_data = stats['products_data']
    error_count = stats['error_count']
    missing_ean_count = stats['missing_ean_count']
    missing_price_count = stats['missing_price_count']
    
    _print_section_header("EXTRACTION SUMMARY")
    print(f"Total products processed: {len(products_data)}")
    print(f"Products with missing EAN: {missing_ean_count}")
    print(f"Products with missing Price: {missing_price_count}")
    print(f"Products with errors: {error_count}")
    
    if len(products_data) > 0:
        success_rate = ((len(products_data) - error_count) / len(products_data) * 100)
        print(f"Success rate: {success_rate:.1f}%")
    else:
        print("Success rate: N/A (no products processed)")
    _print_section_footer()
    
    print("\n" + "=" * 60)
    print("Saving results to Excel...")
    _print_section_footer()


def _print_section_header(text: str) -> None:
    """Print section header."""
    print("=" * 60)
    print(text)


def _print_section_footer() -> None:
    """Print section footer."""
    print("=" * 60)
