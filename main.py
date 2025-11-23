"""
Main entry point for Bol.com Product Scraper.
"""

from scraper import scrape_category_products


if __name__ == '__main__':
    # Scrapes product URLs from a category page, extracts EAN and price for each product,
    # and saves the results to an Excel file
    category_url = "https://www.bol.com/nl/nl/l/vlekkenreinigers-waterniveau-indicator/68305/"
    scrape_category_products(
        category_url,
        output_file='bol_products.xlsx',
        start_page=1,
        max_pages=None  # None = collect all pages, or set to a number to limit pages
    )
