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

1. Clone the repository:
```bash
git clone <repository-url>
cd scraping-2.0
```

2. Create and activate virtual environment:
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

### Option 2: Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

Or using Docker directly:
```bash
docker build -t bol-scraper .
docker run -v $(pwd)/output:/app/output bol-scraper
```

## Usage

### Basic Usage

**Using Environment Variables (Recommended):**
```bash
# Set environment variables and run
export CATEGORY_URLS="https://www.bol.com/nl/nl/l/your-category/12345/"
export MAX_PAGES=2
export LOG_LEVEL=INFO
python main.py
```

**Or using command line:**
```bash
CATEGORY_URLS="https://www.bol.com/nl/nl/l/your-category/12345/" MAX_PAGES=2 python main.py
```

The scraper will automatically use the test category URLs if `CATEGORY_URLS` is not set.

### Advanced Usage

```python
from scraper import scrape_category_products

# Scrape all pages from a category
scrape_category_products(
    category_url="https://www.bol.com/nl/nl/l/elektrische-steps/49880/",
    output_file='products.xlsx',
    start_page=1,
    max_pages=None  # None = all pages
)

# Scrape specific page range
scrape_category_products(
    category_url="https://www.bol.com/nl/nl/l/elektrische-steps/49880/",
    output_file='products.xlsx',
    start_page=1,
    max_pages=5  # Only first 5 pages
)
```

## Output

The scraper generates an Excel file (`bol_products.xlsx` by default) with three columns:

- **Product URL**: Full URL of the product page
- **EAN**: EAN code (barcode) of the product
- **Price**: Current price of the product

**Note:** A sample output file (`sample_output.xlsx`) is included to demonstrate the expected format. Run `python create_sample_output.py` to regenerate it.

## Project Structure

```
scraping-2.0/
├── main.py              # Entry point
├── scraper.py           # Main orchestration logic
├── browser.py           # Browser setup and navigation
├── extractors.py        # Product data extraction (EAN, Price)
├── url_extractor.py     # URL extraction from pages/categories
├── file_handler.py      # Excel file operations
├── config.py            # Configuration constants and env var handling
├── logger_config.py     # Logging configuration
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
└── README.md            # This file
```

## Configuration

### Environment Variables

The scraper can be configured via environment variables. These are especially useful when running in Docker/Kubernetes:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `START_PAGE` | First page to scrape | `1` | `1` |
| `MAX_PAGES` | Maximum pages to scrape per category (use `none` for all pages) | `2` | `3` or `none` |
| `OUTPUT_PATH` | Path where Excel file will be saved | `/app/bol_products.xlsx` | `/app/output/products.xlsx` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CATEGORY_URLS` | Comma-separated list of category URLs to scrape | (uses test URLs) | `https://www.bol.com/nl/nl/l/category1/,https://www.bol.com/nl/nl/l/category2/` |

### Using Environment Variables

**Docker Compose:**
```yaml
environment:
  - START_PAGE=1
  - MAX_PAGES=3
  - OUTPUT_PATH=/app/output/products.xlsx
  - LOG_LEVEL=DEBUG
  - CATEGORY_URLS=https://www.bol.com/nl/nl/l/category1/,https://www.bol.com/nl/nl/l/category2/
```

**Command Line:**
```bash
START_PAGE=1 MAX_PAGES=3 LOG_LEVEL=DEBUG python main.py
```

**Kubernetes:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: bol-scraper
spec:
  containers:
  - name: scraper
    image: bol-scraper:latest
    env:
    - name: START_PAGE
      value: "1"
    - name: MAX_PAGES
      value: "3"
    - name: OUTPUT_PATH
      value: "/app/output/products.xlsx"
    - name: LOG_LEVEL
      value: "INFO"
    - name: CATEGORY_URLS
      value: "https://www.bol.com/nl/nl/l/category1/,https://www.bol.com/nl/nl/l/category2/"
    - name: DOCKER_ENV
      value: "true"
    volumeMounts:
    - name: output
      mountPath: /app/output
  volumes:
  - name: output
    emptyDir: {}
```

### Advanced Configuration

Edit `config.py` to adjust:
- Timeouts and delays
- Retry attempts
- CSS selectors (if website structure changes)

## Error Handling

- Missing EAN codes: Returns empty string, retries once
- Missing prices: Returns empty string, retries once
- Page load failures: Gracefully handles and continues
- Network issues: Automatic retry with delays

## Notes

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

**Docker issues:**
- Ensure Docker has enough memory (2GB+ recommended)
- Check that volumes are mounted correctly

## License

MIT

