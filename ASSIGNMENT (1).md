_# Web Scraping Assignment: Product Price Extraction

## The Problem

You need to build a tool that extracts product information from bol.com category pages.

**Input:** Category URLs (e.g., `https://www.bol.com/nl/nl/l/elektrische-steps/49880/`)

**Output:** An Excel file with three columns:
- Product URL
- EAN code
- Price

## Requirements

### Part 1: Extract Product URLs

Given a category URL:
1. Navigate to the category page
2. Extract all product URLs from the page
3. Handle pagination - categories can have multiple pages
4. Continue until you've collected all products from all pages

### Part 2: Extract Product Details

For each product URL collected:
1. Visit the product page
2. Extract the EAN code
3. Extract the current price
4. Save to Excel: one row per product with URL, EAN, and price


### Part 3: Configurability via Environment Variables

Your Docker container must support configuration through environment variables.
At a minimum, make the following settings configurable:
- START_PAGE – the first page to scrape
- MAX_PAGES – how many pages to scrape per category (default: a sensible limit such as 2–3 for development)
- OUTPUT_PATH – where the generated Excel file will be written inside the container 
- LOG_LEVEL – e.g., INFO, DEBUG, ERROR 
- CATEGORY_URLS – which category pages to scrape (comma-separated list)

The tool must read these values from environment variables at runtime and behave accordingly.
I also want you to think about which of these environment variables should have sensible defaults and what they are.

## Test Data

Use these category URLs for testing:
- `https://www.bol.com/nl/nl/l/analoge-instantcamera-s/20974/`
- `https://www.bol.com/nl/nl/l/vlekkenreinigers-waterniveau-indicator/68305/`

For development, limit yourself to the first 2-3 pages of each category.

## What We're Looking For

1. **Working solution** - Does it successfully extract the data?
2. **Code quality** - Is the code clean and readable?
3. **Error handling** - Does it handle missing data gracefully?
4. **Efficiency** - Does it avoid unnecessary work (e.g., duplicate URLs)?
5. **Containerization** - Can this run in a kubernetes environment without problems?

## Deliverables

1. Source code that solves the problem
2. Example output Excel file with real data
3. Docker Compose setup so the solution can be run locally with
4. Brief README explaining how to run your solution

## Hints

- bol.com shows a cookie consent banner on first visit
- Category pages use `?page=N` for pagination
- Products may appear on multiple pages - handle duplicates
- Not all products may have all data fields - handle missing values

## Time Estimate

This should take approximately 4-6 hours.

Good luck!_