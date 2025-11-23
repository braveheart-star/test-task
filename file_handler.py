from typing import List, Dict, Any
import pandas as pd

from browser import create_driver, navigate_to_page, retry_extraction
from extractors import get_product_ean
from config import (
    COL_PRODUCT_URL,
    COL_EAN,
    COL_PRICE,
    DEFAULT_OUTPUT_FILE
)


def save_result_to_excel(products_data: List[Dict[str, Any]], output_file: str = DEFAULT_OUTPUT_FILE) -> None:
    if not products_data:
        return
    
    df = pd.DataFrame(products_data)
    df.to_excel(output_file, index=False, engine='openpyxl')


def update_missing_ean_codes(excel_file: str = DEFAULT_OUTPUT_FILE) -> None:
    try:
        df = pd.read_excel(excel_file)
        df[COL_EAN] = df[COL_EAN].astype(str).replace('nan', '').replace('None', '')
        
        missing_ean_mask = (
            df[COL_EAN].isna() |
            (df[COL_EAN] == '') |
            (df[COL_EAN].astype(str).str.strip() == '')
        )
        missing_ean_df = df[missing_ean_mask].copy()
        
        if len(missing_ean_df) == 0:
            return
        
        driver, wait = create_driver()
        updated_count = 0
        
        try:
            for idx, row in missing_ean_df.iterrows():
                product_url = row[COL_PRODUCT_URL]
                
                try:
                    navigate_to_page(driver, product_url)
                    ean = retry_extraction(get_product_ean, driver, wait)
                    
                    if ean:
                        df.at[idx, COL_EAN] = ean
                        updated_count += 1
                    
                except Exception:
                    pass
        
        finally:
            try:
                driver.quit()
            except Exception:
                pass
        
        if updated_count > 0:
            df.to_excel(excel_file, index=False, engine='openpyxl')
            
    except FileNotFoundError:
        pass
    except Exception:
        pass
