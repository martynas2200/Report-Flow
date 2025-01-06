from config import PREFIX_SUPPLIER_MAP

def get_supplier_by_prefix(product_code_str: str) -> str:
    """Get the supplier name by product code prefix."""
    for prefix, supplier_name in PREFIX_SUPPLIER_MAP.items():
        if product_code_str.startswith(prefix):
            return supplier_name
    return None