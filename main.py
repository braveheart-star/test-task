"""
Main entry point for Bol.com Product Scraper.
"""

from scraper import scrape_category_products


if __name__ == '__main__':
    category_url = "https://www.bol.com/nl/nl/l/vlekkenreinigers-waterniveau-indicator/68305/"
    scrape_category_products(
        category_url,
        output_file='bol_products.xlsx',
        start_page=1,
        max_pages=2
    )
