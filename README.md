# Bol.com Product Scraper

A web scraping tool that extracts product information (URL, EAN code, and price) from bol.com category pages and saves the results to an Excel file.

## Features

- Extracts all product URLs from category pages
- Handles pagination automatically
- Extracts EAN codes with multiple fallback methods
- Extracts current product prices
- Saves results to Excel file
- Retry mechanism for failed extractions
- Duplicate URL prevention

## Requirements

- Python 3.11+
- Chrome browser (for Selenium)
- Required Python packages (see `requirements.txt`)

## Installation

### Option 1: Local Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Edit `main.py` to set your category URL:

```python
if __name__ == '__main__':
    category_url = "https://www.bol.com/nl/nl/l/your-category/12345/"
    scrape_category_products(
        category_url,
        output_file='bol_products.xlsx',
        start_page=1,
        max_pages=None  # None = all pages, or set a number to limit
    )
```

Then run:
```bash
python main.py
```

## Output

The scraper generates an Excel file (`bol_products.xlsx` by default) with three columns:

- **Product URL**: Full URL of the product page
- **EAN**: EAN code (barcode) of the product
- **Price**: Current price of the product

## Project Structure

```
scraping-2.0/
├── main.py              # Entry point
├── scraper.py           # Main orchestration logic
├── browser.py           # Browser setup and navigation
├── extractors.py       # Product data extraction (EAN, Price)
├── url_extractor.py    # URL extraction from pages/categories
├── file_handler.py     # Excel file operations
├── config.py           # Configuration constants
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Notes

- **Technical Challenge - Anti-Bot Detection**: The most technical challenge was avoiding anti-bot detection. This was solved by using `undetected-chromedriver`, which bypasses common bot detection mechanisms.
- Uses `undetected-chromedriver` to avoid bot detection
- Includes retry mechanism for failed extractions
- Automatically handles pagination
- Prevents duplicate URLs using efficient set operations

## Troubleshooting

**Chrome driver issues:**
- Ensure Chrome browser is installed
- `undetected-chromedriver` should auto-download compatible driver

**Missing data:**
- Some products may not have EAN codes or prices
- The scraper will retry failed extractions once
- Empty values are saved as empty strings in Excel

## License

MIT

