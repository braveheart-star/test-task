"""
Main entry point for Bol.com Product Scraper.
Supports both environment variables (for Docker) and direct configuration.
"""

import re
import logging
from datetime import datetime
from scraper import scrape_category_products
from config import START_PAGE, MAX_PAGES, OUTPUT_PATH, CATEGORY_URLS, LOG_LEVEL


def setup_logging():
    """Configure logging based on LOG_LEVEL environment variable."""
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def generate_output_filename(category_url: str) -> str:
    """Generates output filename with category name and timestamp."""
    # Extract category name from URL
    # Example: https://www.bol.com/nl/nl/l/analoge-instantcamera-s/20974/
    # Result: analoge-instantcamera-s
    match = re.search(r'/l/([^/]+)/\d+/', category_url)
    if match:
        category_name = match.group(1)
    else:
        category_name = "products"
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create filename: category_name_timestamp.xlsx
    filename = f"{category_name}_{timestamp}.xlsx"
    return filename


if __name__ == '__main__':
    # Setup logging from environment variable
    setup_logging()
    
    # Use environment variables if CATEGORY_URLS is set (Docker mode)
    # Otherwise use hardcoded values (local development)
    if CATEGORY_URLS:
        # Docker mode: process all category URLs from environment variable
        for category_url in CATEGORY_URLS:
            # Generate filename with timestamp
            filename = generate_output_filename(category_url)
            
            # Use OUTPUT_PATH as directory if it doesn't end with .xlsx, otherwise use it as full path
            if OUTPUT_PATH and OUTPUT_PATH.endswith('.xlsx'):
                # Single file mode: use OUTPUT_PATH directly (overwrites for each category)
                output_file = OUTPUT_PATH
            else:
                # Directory mode: use OUTPUT_PATH as directory, or current directory
                output_dir = OUTPUT_PATH.rstrip('/') if OUTPUT_PATH else ''
                output_file = f"{output_dir}/{filename}" if output_dir else filename
            
            scrape_category_products(
                category_url,
                output_file=output_file,
                start_page=START_PAGE,
                max_pages=MAX_PAGES
            )
    else:
        # Local development mode: use hardcoded values
        category_url = "https://www.bol.com/nl/nl/l/vlekkenreinigers-waterniveau-indicator/68305/"
        output_file = generate_output_filename(category_url)
        
        scrape_category_products(
            category_url,
            output_file=output_file,
            start_page=START_PAGE,
            max_pages=MAX_PAGES
        )
