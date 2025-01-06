import os
import pandas as pd
from datetime import datetime
from config import SHOP_NAME

def generate_html_report(
    products_df: pd.DataFrame,
    grouped_df: pd.DataFrame,
    missing_values_df: pd.DataFrame,
    file_downloaded: str,
    start_date,
    end_date,
    week_number: int,
    year: int
) -> str:
    """
    Generates an HTML report string that you can save to a file.
    """
    html_str = []
    html_str.append("<html><head><title>Nukainavimai {}</title>".format(week_number))
    html_str.append('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">')
    html_str.append("</head><body>")

    # Some styling
    html_str.append("<style>.table thead th {padding: 6px 4px;} .table tbody td { padding: 2px 4px;}</style>")

    # Header
    html_str.append(f"""
    <div class="columns">
      <div class="column"><h1 class="is-3 title">Nukainojimai {week_number} savaitė</h1></div>
      <div class="column"><div class="has-text-right">{SHOP_NAME} <br> Periodas: {start_date} - {end_date}</div></div>
    </div>
    """)

    # Main table
    html_str.append(products_df.to_html(index=False, classes='main-table table is-striped is-hoverable'))

    # Grouped sums
    html_str.append("<div class='columns'>")
    html_str.append("<div class='column'>")
    html_str.append("<h1>Suvestinė pagal tiekėją</h1>")
    # add  page-break-inside: avoid; to the style attribute of the table tag
    html_str.append(grouped_df.to_html(index=False, classes='table avoid-page-break-inside is-striped is-hoverable'))

    html_str.append("</div>")

    # Missing values, file info, etc.
    html_str.append("<div class='column has-text-info'>")
    if not missing_values_df.empty:
        missing_values_str = ", ".join(missing_values_df['Prekės kodas'].astype(str).unique())
        html_str.append(f"<p>Nepavyko surasti tiekėjų šiems kodams: {missing_values_str}</p>")

    file_time = datetime.fromtimestamp(os.path.getmtime(file_downloaded)).strftime('%Y-%m-%d %H:%M:%S')
    html_str.append(f"<p>Ataskaita sugeruota: {file_time}</p>")
    html_str.append("</div></div>")

    html_str.append("</body></html>")

    return "\n".join(html_str)