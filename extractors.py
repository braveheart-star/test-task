"""
Product data extraction functions (EAN, Price).
"""

import re
import time
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import (
    EAN_PATTERN,
    SCROLL_WAIT,
    SHOW_MORE_WAIT,
    SELECTOR_PRICE,
    SELECTOR_PRICE_FRACTION,
    SELECTOR_SPEC_SECTION,
    SELECTOR_SHOW_MORE,
    SELECTOR_SPEC_ROW,
    SELECTOR_SPEC_TITLE,
    SELECTOR_SPEC_VALUE
)


def get_product_price(driver: WebDriver, wait: WebDriverWait) -> Optional[float]:
    """Extract price from product page.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    
    Returns:
        Price value as float, or None if extraction fails
    """
    try:
        # Wait for price element with timeout
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_PRICE)))
        price_element = driver.find_element(By.CSS_SELECTOR, SELECTOR_PRICE)
        
        # Get main price from first text node
        price_main_raw = driver.execute_script(
            "return arguments[0].childNodes[0].textContent.trim();",
            price_element
        )
        price_main = re.sub(r'[^\d]', '', price_main_raw)
        
        if not price_main:
            return None
        
        # Try to get fraction element
        try:
            price_fraction_element = driver.find_element(By.CSS_SELECTOR, SELECTOR_PRICE_FRACTION)
            price_fraction = price_fraction_element.text.strip()
            if price_fraction:
                return float(f"{price_main}.{price_fraction}")
        except Exception:
            pass
        
        # Return price with .00 if no fraction found
        return float(f"{price_main}.00")
        
    except Exception:
        return None


def get_product_ean(driver: WebDriver, wait: WebDriverWait) -> Optional[str]:
    """Extract EAN code from product specifications section.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    
    Returns:
        EAN code as string, or None if not found
    """
    try:
        # Wait for specifications section to be present
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_SPEC_SECTION)))
        spec_section = driver.find_element(By.CSS_SELECTOR, SELECTOR_SPEC_SECTION)
        
        # Scroll to the specifications section to ensure it's visible
        _scroll_to_element(driver, spec_section)
        
        # Try to find EAN without clicking show more
        ean = _extract_ean_from_specs(driver, spec_section)
        if ean:
            return ean
        
        # If EAN not found, click "show more" button to reveal hidden content
        ean = _try_show_more_and_extract(driver, spec_section)
        return ean
        
    except Exception as e:
        print(f"Error in get_product_ean: {e}")
        return None


def _scroll_to_element(driver: WebDriver, element) -> None:
    """Scroll element into view."""
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
        element
    )
    time.sleep(SCROLL_WAIT)


def _try_show_more_and_extract(driver: WebDriver, spec_section) -> Optional[str]:
    """Try clicking show more button and extract EAN.
    
    Args:
        driver: Selenium WebDriver instance
        spec_section: Specifications section element
    
    Returns:
        EAN code as string, or None if not found
    """
    try:
        show_more_button = spec_section.find_element(By.CSS_SELECTOR, SELECTOR_SHOW_MORE)
        _scroll_to_element(driver, show_more_button)
        driver.execute_script("arguments[0].click();", show_more_button)
        
        # Wait for additional content to load
        time.sleep(SHOW_MORE_WAIT)
        
        # Refresh the spec_section reference after content loads
        spec_section = driver.find_element(By.CSS_SELECTOR, SELECTOR_SPEC_SECTION)
        
        # Try to find EAN again after clicking show more
        return _extract_ean_from_specs(driver, spec_section)
    except Exception:
        return None


def _extract_ean_from_specs(driver: WebDriver, spec_section) -> Optional[str]:
    """Helper function to extract EAN from specifications section.
    
    Tries methods in order:
    1. Structured extraction using regular text (fastest, works for most cases)
    2. JavaScript text extraction (for dynamic content when .text fails)
    3. Regex pattern matching in full text (most robust fallback)
    
    Args:
        driver: Selenium WebDriver instance
        spec_section: Specifications section element
    
    Returns:
        EAN code as string, or None if not found
    """
    # Method 1: Structured extraction using regular text (fastest)
    ean = _extract_ean_structured(driver, spec_section)
    if ean:
        return ean
    
    # Method 2: JavaScript text extraction (for dynamic content)
    ean = _extract_ean_javascript(driver, spec_section)
    if ean:
        return ean
    
    # Method 3: Regex pattern matching in full text content (robust fallback)
    return _extract_ean_regex(driver, spec_section)


def _extract_ean_structured(driver: WebDriver, spec_section) -> Optional[str]:
    """Extract EAN using structured DOM elements."""
    try:
        spec_rows = spec_section.find_elements(By.CSS_SELECTOR, SELECTOR_SPEC_ROW)
        for row in spec_rows:
            try:
                dt = row.find_element(By.CSS_SELECTOR, SELECTOR_SPEC_TITLE)
                dd = row.find_element(By.CSS_SELECTOR, SELECTOR_SPEC_VALUE)
                dt_text = dt.text.strip()
                if dt_text and 'EAN' in dt_text.upper():
                    ean = dd.text.strip()
                    if ean:
                        return ean
            except Exception:
                continue
    except Exception:
        pass
    return None


def _extract_ean_javascript(driver: WebDriver, spec_section) -> Optional[str]:
    """Extract EAN using JavaScript text extraction."""
    try:
        spec_rows = spec_section.find_elements(By.CSS_SELECTOR, SELECTOR_SPEC_ROW)
        for row in spec_rows:
            try:
                dt = row.find_element(By.CSS_SELECTOR, SELECTOR_SPEC_TITLE)
                dd = row.find_element(By.CSS_SELECTOR, SELECTOR_SPEC_VALUE)
                dt_text = driver.execute_script(
                    "return arguments[0].textContent || arguments[0].innerText || '';",
                    dt
                )
                if dt_text and 'EAN' in dt_text.upper().strip():
                    ean = driver.execute_script(
                        "return arguments[0].textContent || arguments[0].innerText || '';",
                        dd
                    )
                    if ean and ean.strip():
                        return ean.strip()
            except Exception:
                continue
    except Exception:
        pass
    return None


def _extract_ean_regex(driver: WebDriver, spec_section) -> Optional[str]:
    """Extract EAN using regex pattern matching."""
    try:
        spec_section_text = driver.execute_script(
            "return arguments[0].textContent || arguments[0].innerText || '';",
            spec_section
        )
        match = re.search(EAN_PATTERN, spec_section_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None
