"""
Excel file operations for saving and updating product data.
"""

import pandas as pd
from browser import create_driver, navigate_to_page, retry_extraction
from extractors import get_product_ean


def save_result_to_excel(products_data, output_file='bol_products.xlsx'):
    """Save products data to Excel file.
    
    Args:
        products_data: List of dictionaries with keys 'Product URL', 'EAN', 'Price'
        output_file: Name of the Excel file to save results
    """
    df = pd.DataFrame(products_data)
    df.to_excel(output_file, index=False)
    print(f"Results saved to: {output_file}")
    print(f"Total products: {len(products_data)}")


def update_missing_ean_codes(excel_file='bol_products.xlsx'):
    """Read Excel file, find URLs with missing EAN codes, test them, and update the file.
    
    Args:
        excel_file: Path to the Excel file to update
    """
    try:
        # Read existing Excel file
        df = pd.read_excel(excel_file)
        print(f"Loaded {len(df)} products from {excel_file}")
        
        # Ensure EAN column is string type to avoid dtype warnings
        df['EAN'] = df['EAN'].astype(str).replace('nan', '').replace('None', '')
        
        # Find rows with missing EAN codes (empty string or NaN)
        missing_ean_mask = (df['EAN'].isna()) | (df['EAN'] == '') | (df['EAN'].astype(str).str.strip() == '')
        missing_ean_df = df[missing_ean_mask].copy()
        
        if len(missing_ean_df) == 0:
            print("No missing EAN codes found. All products have EAN codes.")
            return
        
        print(f"\nFound {len(missing_ean_df)} products with missing EAN codes")
        print("=" * 60)
        
        # Initialize browser
        driver, wait = create_driver()
        
        updated_count = 0
        
        try:
            for idx, row in missing_ean_df.iterrows():
                product_url = row['Product URL']
                print(f"\n[{updated_count + 1}/{len(missing_ean_df)}] Testing: {product_url}")
                
                try:
                    navigate_to_page(driver, product_url)
                    
                    # Extract EAN with retry
                    ean = retry_extraction(get_product_ean, driver, wait)
                    
                    if ean:
                        # Update the DataFrame
                        df.at[idx, 'EAN'] = ean
                        updated_count += 1
                        print(f"  [SUCCESS] EAN: {ean}")
                    else:
                        print(f"  [FAILED] Could not extract EAN")
                    
                except Exception as e:
                    print(f"  [ERROR] {e}")
        
        finally:
            try:
                driver.quit()
            except Exception:
                pass
        
        # Save updated DataFrame back to Excel
        if updated_count > 0:
            df.to_excel(excel_file, index=False)
            print(f"\n{'=' * 60}")
            print(f"Updated {updated_count} EAN codes in {excel_file}")
            print(f"{'=' * 60}")
        else:
            print("\nNo EAN codes were updated.")
            
    except FileNotFoundError:
        print(f"Error: Excel file '{excel_file}' not found.")
    except Exception as e:
        print(f"Error updating EAN codes: {e}")
