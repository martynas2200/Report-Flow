# Report Flow

## Overview
Report Flow is a tiny case-specific Python application designed to interact with a Point of Sale (POS) system. It provides functionalities for data processing, reporting, and email notifications, making it easier to manage and analyze sales data.

## Features
- **Data Processing**: Process sales data to generate reports.
- **Reporting**: Generate weekly and daily reports for printing or emailing.
- **Integrates with Raso Retail POS System & B1 accounting program API**: Fetch sales data from the POS system and push data to the accounting program.

## Usage Guidelines
- Configure your environment variables in the `.env` file.
- Use `weekly_script.py` for tasks that need to run weekly.
- Use `daily_script.py` for tasks that need to run daily.
- Refer to the individual module files for specific functionalities and usage instructions.