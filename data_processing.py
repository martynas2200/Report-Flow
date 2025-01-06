from io import StringIO
import os
import pandas as pd
from prefix_mapping import get_supplier_by_prefix
from b1_api import get_supplier_by_barcode

def convert_decimal(x):
    """Converts a string to a float, replacing commas with dots."""
    try:
        return float(x.replace(',', '.'))
    except:
        return 0


def read_csv_windows1257(file_path: str, sep=';', decimal=',', thousands='\xa0') -> pd.DataFrame:
    """Reads a CSV file with Windows-1257 encoding."""
    ##### Inconsistencies that decimal operator cannot pick up 
    ##### 1 ,000 might be used instead of 1,000
    # Preprocess the file and replace non-breaking spaces
    with open(file_path, 'r', encoding='Windows-1257') as f:
        content = f.read().replace('\xa0', '')

    return pd.read_csv(StringIO(content), sep=sep, decimal=decimal, thousands=thousands)

def filter_discounted_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Filters the DataFrame for active checks with a discount."""
    # Example conditions from your code:
    filtered_df = df[
        (df['Ar aktyvus?'] == 1) &
        (df['Ar čekis atmestas?'] == 0) &
        (df['Nuol. suma 1'] > 0)
    ]
    return filtered_df

def map_suppliers(df: pd.DataFrame, mapping_csv: str) -> pd.DataFrame:
    """Adds a 'Tiekėjas' column by merging on Prekės kodas and does fallback prefix logic."""
    # Load mapping CSV
    mapping_df = pd.read_csv(mapping_csv, encoding='utf-8')
    mapping_df['Prekės kodas'] = mapping_df['Prekės kodas'].astype(int)

    df = df.merge(mapping_df, on='Prekės kodas', how='left')

    # prefix-based && B1 API fallback
    df['Tiekėjas'] = df.apply(
        lambda row: row['Tiekėjas'] 
        if pd.notnull(row['Tiekėjas']) 
        else (
            get_supplier_by_prefix(str(row['Prekės kodas'])) 
            if get_supplier_by_prefix(str(row['Prekės kodas'])) is not None 
            else get_supplier_by_barcode(str(row['Prekės kodas']))
        ),
        axis=1
    )
    # Fill in the remaining missing values
    df['Tiekėjas'] = df['Tiekėjas'].fillna('Nežinomas')
    return df

def summarize_discounts_by_supplier(df: pd.DataFrame) -> pd.DataFrame:
    """Group by 'Tiekėjas' and sum 'Nuolaida'."""
    grouped_df = df.groupby('Tiekėjas')['Nuolaida'].sum().reset_index()
    return grouped_df.sort_values(by='Nuolaida', ascending=False)

def save_excel(df: pd.DataFrame, grouped_df: pd.DataFrame, output_path: str) -> None:
    """Saves two sheets in one Excel file."""
    with pd.ExcelWriter(output_path) as writer:
        df.to_excel(writer, sheet_name='Pardavimai', index=False)
        grouped_df.to_excel(writer, sheet_name='Sumiškai pagal tiekėją', index=False)