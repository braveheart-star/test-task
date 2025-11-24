"""
Main entry point for Bol.com Product Scraper.
"""

import re
from datetime import datetime
from scraper import scrape_category_products
from config import START_PAGE, MAX_PAGES, OUTPUT_PATH, CATEGORY_URLS


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
    # Scrapes product URLs from a category page, extracts EAN and price for each product,
    # and saves the results to an Excel file
    category_url = "https://www.bol.com/nl/nl/l/vlekkenreinigers-waterniveau-indicator/68305/"
    output_file = generate_output_filename(category_url)
    
    scrape_category_products(
        category_url,
        output_file=output_file,
        start_page=1,
        max_pages=3  # None = collect all pages, or set to a number to limit pages
    )
