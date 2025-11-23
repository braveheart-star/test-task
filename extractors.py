"""
Product data extraction functions (EAN, Price).
"""

import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from config import EAN_PATTERN, SCROLL_WAIT, SHOW_MORE_WAIT


def get_product_price(driver, wait):
    """Extract price from product page.
    
    Returns:
        float: Price value, or None if extraction fails
    """
    try:
        # Wait for price element with timeout
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-test="price"]')))
        price_element = driver.find_element(By.CSS_SELECTOR, 'span[data-test="price"]')
        
        # Get main price from first text node
        price_main_raw = driver.execute_script("return arguments[0].childNodes[0].textContent.trim();", price_element)
        price_main = re.sub(r'[^\d]', '', price_main_raw)
        
        if not price_main:
            return None
        
        # Try to get fraction element
        try:
            price_fraction_element = driver.find_element(By.CSS_SELECTOR, 'sup[data-test="price-fraction"]')
            price_fraction = price_fraction_element.text.strip()
            if price_fraction:
                return float(f"{price_main}.{price_fraction}")
        except Exception:
            # No fraction element - add .00
            pass
        
        # Return price with .00 if no fraction found
        return float(f"{price_main}.00")
        
    except Exception:
        # Silently return None - error handling is done at higher level
        return None


def get_product_ean(driver, wait):
    """Extract EAN code from product specifications section.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    
    Returns:
        EAN code as string, or None if not found
    """
    try:
        # Wait for specifications section to be present
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section[data-group-name="ProductSpecification"]')))
        
        # Find the specifications section
        spec_section = driver.find_element(By.CSS_SELECTOR, 'section[data-group-name="ProductSpecification"]')
        
        # Scroll to the specifications section to ensure it's visible
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", spec_section)
        time.sleep(SCROLL_WAIT)
        
        # Try to find EAN without clicking show more (in case it's already visible)
        ean = _extract_ean_from_specs(driver, spec_section)
        if ean:
            return ean
        
        # If EAN not found, click "show more" button to reveal hidden content
        try:
            show_more_button = spec_section.find_element(By.CSS_SELECTOR, 'a[data-test="show-more"]')
            # Scroll to button and click using JavaScript to avoid interception
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", show_more_button)
            time.sleep(SCROLL_WAIT)
            driver.execute_script("arguments[0].click();", show_more_button)
            
            # Wait for additional content to load
            time.sleep(SHOW_MORE_WAIT)
            
            # Refresh the spec_section reference after content loads
            spec_section = driver.find_element(By.CSS_SELECTOR, 'section[data-group-name="ProductSpecification"]')
            
            # Try to find EAN again after clicking show more
            ean = _extract_ean_from_specs(driver, spec_section)
            if ean:
                return ean
        except Exception:
            # Button might not exist, already clicked, or page structure is different
            pass
        
        return None
    except Exception as e:
        print(f"Error in get_product_ean: {e}")
        return None


def _extract_ean_from_specs(driver, spec_section):
    """Helper function to extract EAN from specifications section.
    
    Tries methods in order:
    1. Structured extraction using regular text (fastest, works for most cases)
    2. JavaScript text extraction (for dynamic content when .text fails)
    3. Regex pattern matching in full text (most robust fallback)
    """
    # Method 1: Structured extraction using regular text (fastest)
    try:
        spec_rows = spec_section.find_elements(By.CSS_SELECTOR, 'div.specs__row')
        for row in spec_rows:
            try:
                dt = row.find_element(By.CSS_SELECTOR, 'dt.specs__title')
                dd = row.find_element(By.CSS_SELECTOR, 'dd.specs__value')
                dt_text = dt.text.strip()
                if dt_text and 'EAN' in dt_text.upper():
                    ean = dd.text.strip()
                    if ean:
                        return ean
            except Exception:
                continue
    except Exception:
        pass
    
    # Method 2: JavaScript text extraction (for dynamic content)
    try:
        spec_rows = spec_section.find_elements(By.CSS_SELECTOR, 'div.specs__row')
        for row in spec_rows:
            try:
                dt = row.find_element(By.CSS_SELECTOR, 'dt.specs__title')
                dd = row.find_element(By.CSS_SELECTOR, 'dd.specs__value')
                dt_text = driver.execute_script("return arguments[0].textContent || arguments[0].innerText || '';", dt)
                if dt_text and 'EAN' in dt_text.upper().strip():
                    ean = driver.execute_script("return arguments[0].textContent || arguments[0].innerText || '';", dd)
                    if ean and ean.strip():
                        return ean.strip()
            except Exception:
                continue
    except Exception:
        pass
    
    # Method 3: Regex pattern matching in full text content (robust fallback)
    try:
        spec_section_text = driver.execute_script("return arguments[0].textContent || arguments[0].innerText || '';", spec_section)
        # Pattern to find EAN: followed by numbers (8-14 digits, standard EAN length)
        # Handles variations like "EAN:", "EAN ", "EAN-", etc.
        match = re.search(EAN_PATTERN, spec_section_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    
    return None
