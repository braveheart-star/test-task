# Bol.com Product Scraper

A web scraping tool that extracts product information (URL, EAN code, and price) from bol.com category pages and saves the results to an Excel file with automatic filename generation.

## Features

- ✅ Extracts all product URLs from category pages with pagination support
- ✅ Handles pagination automatically across multiple pages
- ✅ Extracts EAN codes with multiple fallback methods
- ✅ Extracts current product prices
- ✅ Automatic output filename generation (category name + timestamp)
- ✅ Retry mechanism for failed extractions
- ✅ Duplicate URL prevention at multiple levels
- ✅ Stealth features to avoid bot detection (homepage visit, human-like scrolling)
- ✅ Progress tracking and detailed summary statistics
- ✅ Graceful error handling with empty value fallbacks

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

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Edit `main.py` to set your category URL:

```python
if __name__ == '__main__':
    category_url = "https://www.bol.com/nl/nl/l/your-category/12345/"
    output_file = generate_output_filename(category_url)  # Auto-generates: category_name_YYYYMMDD_HHMMSS.xlsx
    
    scrape_category_products(
        category_url,
        output_file=output_file,
        start_page=1,
        max_pages=3  # None = collect all pages, or set a number to limit pages
    )
```

Then run:
```bash
python main.py
```

### Parameters

- `category_url`: The bol.com category page URL
- `output_file`: Excel file path (auto-generated if using `generate_output_filename()`)
- `start_page`: First page to scrape (default: 1)
- `max_pages`: Maximum number of pages to scrape (default: 2, use `None` for all pages)

## Output

The scraper generates an Excel file with automatic naming: `{category_name}_{timestamp}.xlsx`

**Example:** `vlekkenreinigers-waterniveau-indicator_20251124_110313.xlsx`

The Excel file contains three columns:

- **Product URL**: Full URL of the product page
- **EAN**: EAN code (barcode) of the product
- **Price**: Current price of the product

### Console Output

During execution, you'll see:
- Progress indicators: `[1/77] Processing: https://...`
- Retry notifications for failed products
- Summary statistics:
  ```
  ============================================================
  Scraping completed!
  Total products: 77
  Successful (both EAN & Price): 77
  Missing EAN: 0
  Missing Price: 0
  Complete failures: 1
  ============================================================
  ```

## Project Structure

```
app/
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

## Technical Details

### Anti-Bot Detection

The most technical challenge was avoiding anti-bot detection. This was solved using multiple strategies:

1. **undetected-chromedriver**: Bypasses common bot detection mechanisms by patching ChromeDriver
2. **Stealth Initialization**: Visits bol.com homepage first to establish a legitimate session
3. **Human-like Behavior**: 
   - Random delays (3-5 seconds for homepage, 5-7 seconds for product pages)
   - Human-like scrolling behavior
   - Non-headless mode (maximized window)


### EAN Extraction Strategy

The scraper uses a three-tier fallback approach:
1. **Structured extraction**: Parses HTML structure (dt/dd elements)
2. **JavaScript extraction**: Uses JavaScript to extract text content
3. **Regex extraction**: Pattern matching as final fallback

### Duplicate Prevention

- URL deduplication at page level using `dict.fromkeys()`
- Set-based deduplication across multiple pages
- Additional duplicate check during product processing

## Troubleshooting

### Chrome Driver Issues
- Ensure Chrome browser is installed and up to date
- `undetected-chromedriver` should auto-download compatible driver
- If issues persist, try updating Chrome browser

### Missing Data
- Some products may not have EAN codes or prices available on the page
- The scraper automatically retries failed extractions once
- Empty values are saved as empty strings in Excel
- Check the summary statistics to see how many products have missing data

### Timeout Errors
- If you see "Navigation failed" errors, the page may be loading slowly
- The scraper will continue processing other products
- Failed products are retried automatically

### Performance
- Processing time depends on number of products and page load times
- Average: ~5-7 seconds per product (includes stealth delays)
- For 77 products: approximately 6-9 minutes total

## License

MIT

