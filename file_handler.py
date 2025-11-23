from typing import List, Dict, Any
import pandas as pd

from config import DEFAULT_OUTPUT_FILE


def save_result_to_excel(products_data: List[Dict[str, Any]], output_file: str = DEFAULT_OUTPUT_FILE) -> None:
    """Saves products data to Excel file."""
    import os
    
    if not products_data:
        return
    
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    df = pd.DataFrame(products_data)
    df.to_excel(output_file, index=False, engine='openpyxl')
