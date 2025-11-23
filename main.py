"""
Main entry point for Bol.com Product Scraper.
"""

from logger_config import setup_logging
from scraper import scrape_category_products
from config import START_PAGE, MAX_PAGES, OUTPUT_PATH, CATEGORY_URLS


if __name__ == '__main__':
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("Bol.com Product Scraper - Starting")
    logger.info("=" * 60)
    logger.info(f"Configuration:")
    logger.info(f"  START_PAGE: {START_PAGE}")
    logger.info(f"  MAX_PAGES: {MAX_PAGES}")
    logger.info(f"  OUTPUT_PATH: {OUTPUT_PATH}")
    logger.info(f"  CATEGORY_URLS: {CATEGORY_URLS if CATEGORY_URLS else 'Not set (using default)'}")
    logger.info("=" * 60)
    
    # Get category URLs from environment or use default
    if CATEGORY_URLS:
        category_urls = CATEGORY_URLS
    else:
        # Default test URLs
        category_urls = [
            "https://www.bol.com/nl/nl/l/analoge-instantcamera-s/20974/",
            "https://www.bol.com/nl/nl/l/vlekkenreinigers-waterniveau-indicator/68305/"
        ]
        logger.info("Using default test category URLs")
    
    # Process each category
    for idx, category_url in enumerate(category_urls, 1):
        logger.info(f"\nProcessing category {idx}/{len(category_urls)}: {category_url}")
        
        # Generate output filename for each category if multiple categories
        if len(category_urls) > 1:
            import os
            base_name = os.path.splitext(OUTPUT_PATH)[0]
            ext = os.path.splitext(OUTPUT_PATH)[1] or '.xlsx'
            output_file = f"{base_name}_category_{idx}{ext}"
        else:
            output_file = OUTPUT_PATH
        
        scrape_category_products(
            category_url,
            output_file=output_file,
            start_page=START_PAGE,
            max_pages=MAX_PAGES
        )
    
    logger.info("\n" + "=" * 60)
    logger.info("All categories processed. Scraping completed.")
    logger.info("=" * 60)
