import os
from datetime import datetime, timedelta
import pandas as pd

from pos_client import POSClient
from config import DATA_FOLDER, REPORTING_EMAIL
from data_processing import (
    read_csv_windows1257,
    filter_discounted_sales,
    map_suppliers,
    summarize_discounts_by_supplier,
    save_excel
)
from reporting import generate_html_report
from email_service import send_email_html


def get_week_interval(year, week_number):
    """Get the start and end date of a week by its number."""
    first_day = datetime(year, 1, 1)
    start_of_week = first_day + \
        timedelta(days=(week_number - 1) * 7 - first_day.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.date(), end_of_week.date()


def reduced_sales_report(year, week_number):
    """Generates a report for a given week number and year."""
    GRID = 'Transactions'
    pos_client = POSClient(grid=GRID)
    start_date, end_date = get_week_interval(year, week_number)
    last_report_path = os.path.join(DATA_FOLDER, "last_report.html")
    print(f"Week {week_number} of {year}: {start_date} to {end_date}")

    # File name
    file_name = f"sales_{year}_{week_number}.csv"
    file_path = os.path.join(DATA_FOLDER, file_name)

    if os.path.exists(file_path):
        print(f"File {file_name} already exists, skipping generation.")
        return
    else:
        if os.path.exists(last_report_path):
            os.remove(last_report_path)

    # 1. Login
    pos_client.login()

    # 2. Filter data
    begin = start_date.strftime('%Y-%m-%d 00:00')
    end = (end_date + timedelta(days=1)).strftime('%Y-%m-%d 00:00')
    pos_client.filter_data(begin, end)

    # 3. Export
    pos_client.export_data(output_format="CSV", grid_name_prefix="GridView")

    # 4. Download
    pos_client.download_file(file_path)

    # 5. Logout
    pos_client.logout()

    # 6. Data processing

    df = read_csv_windows1257(file_path, sep=';')
    df = filter_discounted_sales(df)

    df = df.rename(columns={'Nuol. suma 1': 'Nuolaida'})
    df['Prekės kodas'] = df['Prekės kodas'].astype(int)

    df = map_suppliers(df, mapping_csv=os.path.join(DATA_FOLDER, "mapping.csv"))

    keep_columns = [
        'Darb. vardas', 'Čekio nr.', 'Prekės kodas', 'Tiekėjas', 'Prekės pavadinimas',
        'Kiekis', 'Pagr. kaina', 'Pagr. suma', 'Suma', 'Mok. suma', 'Nuolaida', 'Įrašo data'
    ]
    df = df[keep_columns]

    # Summaries
    grouped_df = summarize_discounts_by_supplier(df)

    # Export to Excel
    final_name = f"Nukainavimai_{year}_{week_number}_savaite.xlsx"
    final_output_path = os.path.join(DATA_FOLDER, final_name)
    save_excel(df, grouped_df, final_output_path)
    print(f"Final data exported to {final_output_path}")

    # Generate HTML report
    # Additional formatting
    df['Prekė'] = df['Prekės pavadinimas'] + \
        ' (' + df['Prekės kodas'].astype(str) + ')'
    df['Įrašo data'] = pd.to_datetime(df['Įrašo data'])

    df = df.sort_values(by=['Tiekėjas', 'Suma'], ascending=[True, False])

    df['Tiekėjas'] = (
        df['Tiekėjas']
        .str.replace('UAB ', '', regex=False)
        .str.replace('AB ', '', regex=False)
        .str.replace('"', '', regex=False)
        .str.title()
    )

    df['Employee_Date'] = df['Darb. vardas'] + \
        ', ' + df['Įrašo data'].dt.strftime('%m-%d')
    df['Kvitai'] = df.groupby(['Employee_Date', 'Prekė'])['Čekio nr.'].transform(
        lambda x: ', '.join(x.astype(str).unique())
    )
    df['Kvitai'] = df['Kvitai'] + ' (' + df['Employee_Date'] + ')'

    products_df = (
        df.groupby(['Tiekėjas', 'Prekė'])
          .agg({
              'Pagr. kaina': 'mean',
              'Kiekis': 'sum',
              'Nuolaida': 'sum',
              'Kvitai': lambda x: '; '.join(x.unique())
          })
        .reset_index()
    )
    products_df = products_df.rename(
        columns={'Nuolaida': 'Nuol.', 'Pagr. kaina': 'Kaina'})
    missing_values = df[df['Tiekėjas'] == 'Nežinomas']

    html_report = generate_html_report(
        products_df=products_df,
        grouped_df=grouped_df,
        missing_values_df=missing_values,
        file_downloaded=file_path,
        start_date=start_date,
        end_date=end_date,
        week_number=week_number,
        year=year
    )
    html_output_path = os.path.join(
        DATA_FOLDER, f"report_{year}_{week_number}.html")
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html_report)
    print(f"HTML report exported")

    # Duplicate last report
    os.system(f"cp {html_output_path} {last_report_path}")

    # send email
    message = f"<div style='color: grey;'>Prisegamas {final_name} failas. Tai automatinė žinutė. (This is an automated email.)</div>"
    send_email_html(
        subject=f"Nukainavimų ataskaita, {week_number} savaitė",
        html_content= message + grouped_df.to_html(),
        attachments=[final_output_path],
        to_email= REPORTING_EMAIL
    )

if __name__ == "__main__":
    current_date = datetime.now()
    current_week_number = current_date.isocalendar()[1]
    current_year = current_date.year
    reduced_sales_report(year=current_year, week_number=current_week_number)
