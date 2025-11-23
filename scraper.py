"""
Main scraper orchestration logic.
"""

from browser import create_driver, navigate_to_page, retry_extraction
from extractors import get_product_price, get_product_ean
from url_extractor import extract_product_urls_from_category
from file_handler import save_result_to_excel
from config import RETRY_DELAY


def scrape_category_products(category_url, output_file='bol_products.xlsx', start_page=1, max_pages=2):
    """
    Complete scraper: Extract all product URLs from category and get EAN + price for each.
    
    Args:
        category_url: URL of the category page
        output_file: Name of the Excel file to save results
        start_page: Starting page number (1-indexed, default: 1)
        max_pages: Number of pages to scrape starting from start_page (default: 2 for development, None for all pages)
    """
    driver, wait = create_driver()
    
    products_data = []
    
    try:
        print("=" * 60)
        print("PART 1: Extracting Product URLs from Category")
        print(f"Category URL: {category_url}")
        print(f"Start Page: {start_page}, Max Pages: {max_pages}")
        print("=" * 60)
        
        # Part 1: Extract all product URLs from specified page range
        product_urls = extract_product_urls_from_category(category_url, driver, wait, start_page=start_page, max_pages=max_pages)
        print(f"\nTotal product URLs found: {len(product_urls)}\n")
        
        if not product_urls:
            print("No products found. Exiting.")
            return
        
        print("=" * 60)
        print("PART 2: Extracting Product Details (EAN and Price)")
        print("=" * 60)
        
        # Part 2: Extract details for each product
        failed_products = []  # Track failed products for retry
        missing_ean_count = 0
        missing_price_count = 0
        error_count = 0
        # Use dict for O(1) lookup during retry phase
        products_dict = {}
        
        for idx, product_url in enumerate(product_urls, 1):
            print(f"\n[{idx}/{len(product_urls)}] Processing: {product_url}")
            
            try:
                # Load page with timeout handling
                navigate_to_page(driver, product_url)
                
                # Extract price with retry
                price = retry_extraction(get_product_price, driver, wait)
                if not price:
                    missing_price_count += 1
                    print(f"  Price: [MISSING]")
                
                # Extract EAN with retry
                ean = retry_extraction(get_product_ean, driver, wait)
                if not ean:
                    missing_ean_count += 1
                    print(f"  EAN: [MISSING]")
                
                # Mark for retry if any field is missing
                if not price or not ean:
                    failed_products.append(product_url)
                    if not price and not ean:
                        error_count += 1
                
                product_data = {
                    'Product URL': product_url,
                    'EAN': ean if ean else '',
                    'Price': price if price else ''
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
                    'Product URL': product_url,
                    'EAN': '',
                    'Price': ''
                }
                products_data.append(product_data)
                products_dict[product_url] = product_data
        
        # Retry failed products once more
        if failed_products:
            print(f"\n{'=' * 60}")
            print(f"Retrying {len(failed_products)} failed products...")
            print(f"{'=' * 60}")
            
            for idx, product_url in enumerate(failed_products, 1):
                print(f"\n[RETRY {idx}/{len(failed_products)}] Processing: {product_url}")
                
                try:
                    # Load page with timeout handling (longer delay for retry)
                    navigate_to_page(driver, product_url, delay=RETRY_DELAY)
                    
                    # Get product data from dict (O(1) lookup)
                    product = products_dict.get(product_url)
                    if not product:
                        continue
                    
                    # Retry price extraction
                    if not product['Price']:
                        price = retry_extraction(get_product_price, driver, wait)
                        if price:
                            product['Price'] = price
                            missing_price_count -= 1
                            print(f"  Price: {price} [RETRIEVED]")
                    
                    # Retry EAN extraction
                    if not product['EAN']:
                        ean = retry_extraction(get_product_ean, driver, wait)
                        if ean:
                            product['EAN'] = ean
                            missing_ean_count -= 1
                            print(f"  EAN: {ean} [RETRIEVED]")
                            
                except Exception as e:
                    print(f"  [ERROR] Retry failed: {e}")
        
        # Print summary statistics
        print(f"\n{'=' * 60}")
        print("EXTRACTION SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total products processed: {len(products_data)}")
        print(f"Products with missing EAN: {missing_ean_count}")
        print(f"Products with missing Price: {missing_price_count}")
        print(f"Products with errors: {error_count}")
        if len(products_data) > 0:
            success_rate = ((len(products_data) - error_count) / len(products_data) * 100)
            print(f"Success rate: {success_rate:.1f}%")
        else:
            print("Success rate: N/A (no products processed)")
        print(f"{'=' * 60}")
        
        # Save to Excel
        print("\n" + "=" * 60)
        print("Saving results to Excel...")
        print("=" * 60)
        
        save_result_to_excel(products_data, output_file)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass
