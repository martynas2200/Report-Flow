import requests
from config import B1_API_KEY, DATA_FOLDER
import os
import datetime

SUPPLIER_CACHE = {}

def fetch_b1_data(url: str, body: dict) -> dict:
    """Fetches data from the B1 API."""
    url = f"https://www.b1.lt/api/{url}"
    headers = {
        'B1-Api-Key': B1_API_KEY,
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json(), response.status_code


def get_supplier_by_barcode(barcode: str) -> str:
    """Get the supplier name by barcode."""
    if barcode.isdigit():
        body = {
            "rows": 100,
            "page": 1,
            "filters": {
                "groupOp": "AND",
                "rules": [
                    {
                        "field": "barcode",
                        "op": "eq",
                        "data": barcode
                    }
                ]
            }
        }
        if barcode in SUPPLIER_CACHE:
            return SUPPLIER_CACHE[barcode]

        try:
            response, status = fetch_b1_data("reference-book/items/list", body)
            if status != 200 or not response.get('data'):
                return None
            # temp: add a line to the csv file
            with open(os.path.join(DATA_FOLDER, "mapping.csv"), "a") as f:
                f.seek(0, os.SEEK_END) # check if there ia a newline at the end of the file
                if f.tell() > 0:
                    f.seek(-1, os.SEEK_END)
                    if f.read(1) != "\n":
                        f.write("\n")
                f.write(f"{barcode},{response['data'][0]['manufacturerName']}\n")
            SUPPLIER_CACHE[barcode] = response['data'][0]['manufacturerName']
            return response['data'][0]['manufacturerName']
        except:
            return None
    return None

def create_cash_receipt(sum, full_date, number, try_count=1):
    """Create a cash receipt in the B1 system."""
    if try_count > 2:
        print("Error: Maximum number of retries reached.")
        return 0
    date = full_date.split(" ")[0]
    number = str(number).zfill(5)
    body = {
        "clientAccountId": 195,
        "clientId": 2,
        "currencyId": 2,
        "currencyCode": "EUR",
        "date": date,
        "debitAccountId": 510,
        "series": "PPK",
        "number": number,
        "total": sum,
        "attachment": "Inkasuota suma " + date.replace("-", " "),
        "documentStatusId": 5,
        "employeeId": 39
    }
    path = "cash-flow/cash-receipts/create"
    response, status = fetch_b1_data(path, body)
    if status == 400:
        return create_cash_receipt(sum, full_date, number + 1, try_count + 1)
    elif status == 200:
        return try_count
    else:
        print(f"Unexpected error: {response}")
        return 0


def read_document_number():
    """Read the current document number from the file."""
    try:
        with open(os.path.join(DATA_FOLDER, "cash_receipt_num.txt"), 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        # return the today's date without spaces and symbols
        return int("".join(str(datetime.datetime.now().date()).split("-")))

def save_document_number(number):
    """Save the document number to the file."""
    with open(os.path.join(DATA_FOLDER, "cash_receipt_num.txt"), 'w') as f:
        f.write(str(number))

def process_new_cash_receipt(sum, full_date):
    """Process a new cash receipt, track the document number"""
    doc_number = read_document_number()
    tries = create_cash_receipt(sum, full_date, doc_number)
    if tries and doc_number < 20250000:
        save_document_number(doc_number + tries)
        return True
    return False
