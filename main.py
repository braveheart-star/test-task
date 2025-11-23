"""
Main entry point for Bol.com Product Scraper.
"""

from scraper import scrape_category_products
from file_handler import update_missing_ean_codes


if __name__ == '__main__':
    # Option 1: Update missing EAN codes in existing Excel file
    # update_missing_ean_codes('bol_products.xlsx')
    
    # Option 2: Run full scraper
    category_url = "https://www.bol.com/nl/nl/l/vlekkenreinigers-waterniveau-indicator/68305/"
    scrape_category_products(category_url, output_file='bol_products.xlsx', start_page=1, max_pages=2)
