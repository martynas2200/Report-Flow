import os
import pandas as pd
from datetime import datetime, timedelta

from pos_client import POSClient
from config import DATA_FOLDER, DAILY_EMAIL
from data_processing import read_csv_windows1257
from email_service import send_email_html
from b1_api import process_new_cash_receipt

def main():
    GRID = "ZReports"
    today = datetime.today().strftime('%Y-%m-%d 00:00')
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d 00:00')
    today_date = datetime.today().strftime('%Y-%m-%d')
    file_path = os.path.join(DATA_FOLDER, f"z_{today_date}.csv")

    # Quick checks
    if os.path.exists(file_path) or datetime.now().hour < 15:
        print("Either file already exists or it's too early in the day; exiting.")
        return

    pos_client = POSClient(grid=GRID)
    pos_client.login()

    # Filter
    pos_client.filter_data(today, tomorrow)
    # Export
    pos_client.export_data()
    # Download
    pos_client.download_file(file_path)
    pos_client.logout()

    # Process the data
    try:
        df = read_csv_windows1257(file_path, sep=';')
    except:
        print("Could not parse CSV; removing file.")
        os.remove(file_path)
        return

    if df.empty:
        print("No data found. Removing file.")
        os.remove(file_path)
        return

    # Clean up data (drop first 5 columns, it is store info)
    df = df.iloc[:, 6:]
    # Remove unused columns
    if "GT" in df.columns:
        df.drop(columns=["GT"], inplace=True, errors='ignore')
    if "Fiskalo nr." in df.columns:
        df.drop(columns=["Fiskalo nr."], inplace=True, errors='ignore')

    first_row = df.iloc[0]

    # Save Cash Incollection to B1 API
    if "Išimta gryn. 1" not in first_row or "Išimta gryn. 2" not in first_row:
        print("No cash data found.")
    else:
        process_new_cash_receipt(first_row["Išimta gryn. 1"] + first_row["Išimta gryn. 2"], first_row["Data"])

    # Check the first row
    if first_row["Darb. vardas"] == "Reda":
        print("Reda closed the day. No need to send a receipt.")
        return

    # Build receipt text
    header = df.columns
    receipt_text = ""
    for header_name, value in zip(header, first_row):
        if pd.notnull(value) and value != 0:
            receipt_text += f"{header_name:<22} {value:>20}\n"

    # HTML-ify
    receipt_text_html = (
        "<div style='font-family: Courier New;'><pre>" +
        receipt_text +
        "</pre></div><div style='color: grey;'>Tai automatinė žinutė. This is an automated email.</div>"
    )

    # Send email
    subject = f"Z ataskaita {today_date}"
    send_email_html(subject=subject, to_email=DAILY_EMAIL, html_content=receipt_text_html)


if __name__ == "__main__":
    main()