import requests
from bs4 import BeautifulSoup
from config import LOGIN_URL, FILTER_URL, EXPORT_URL, DOWNLOAD_URL, LOGOUT_URL, USERNAME, PASSWORD

class POSClient:
    def __init__(self, grid: str):
        """
        :param grid: e.g. 'Transactions', 'ZReports', 'DiscountsApplied', etc. (refering to RASO RETAIL or depending on the POS system)
        """
        self.grid = grid
        self.session = requests.Session()

    @staticmethod # since it does not use self
    def get_error_message(response):
        """Parse a known error message from HTML response."""
        soup = BeautifulSoup(response.text, "html.parser")
        error_div = soup.find("div", {"class": "dxpc-content"})
        return error_div.text if error_div else "Unknown error"

    def login(self):
        """
        Logs in to the POS system and sets up session cookies.
        Raises an exception if login fails.
        """
        response = self.session.get(LOGIN_URL.format(GRID=self.grid), verify=False)
        soup = BeautifulSoup(response.text, "html.parser")

        token_input = soup.find("input", {"name": "__RequestVerificationToken"})
        if not token_input:
            raise RuntimeError("Could not find RequestVerificationToken on login page.")

        token = token_input["value"]

        payload = {
            "__RequestVerificationToken": token,
            "UserName": USERNAME,
            "Password": PASSWORD,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        login_response = self.session.post(
            LOGIN_URL.format(GRID=self.grid),
            data=payload, headers=headers, verify=False
        )

        if login_response.status_code != 200 or "Invalid login" in login_response.text:
            raise RuntimeError("Login failed. Check credentials or request structure.")

        print("Login successful!")

    def filter_data(self, date_from: str, date_to: str):
        """
        Sends a POST request to filter data for the specified date range.
        """
        body = {"dateFrom": date_from, "dateTo": date_to}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.session.post(
            FILTER_URL.format(GRID=self.grid), data=body, headers=headers, verify=False
        )

        if response.status_code != 200:
            raise RuntimeError(f"Filter request failed: {response.status_code}")
        print("Filter request successful!")

    def export_data(self, output_format="CSV", grid_name_prefix="GridView"):
        """
        Triggers the export request (OutputFormat can be CSV, Excel, etc.).
        """
        export_params = {
            "OutputFormat": output_format,
            "GridName": f"{grid_name_prefix}{self.grid}",
            "VID": "undefined",
        }
        body = {}  # In many cases, you might reuse the same body from filter_data
        response = self.session.post(EXPORT_URL, params=export_params, data=body, verify=False)

        if response.status_code != 200:
            raise RuntimeError(f"Export request failed: {response.status_code}")
        print("ExportTo request successful!")

    def download_file(self, file_path: str) -> None:
        """
        Downloads the exported file and writes it to file_path.
        """
        response = self.session.post(DOWNLOAD_URL, verify=False, stream=True)
        if response.status_code == 200:
            print("Download request successful!")
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            # .replace('\xa0', '') to clean up the file
            print(f"File downloaded successfully to: {file_path}")
        else:
            error_msg = self.get_error_message(response)
            raise RuntimeError(f"Download request failed with status {response.status_code}: {error_msg}")

    def logout(self):
        """
        Logs out of the POS system.
        """
        log_out_response = self.session.get(LOGOUT_URL, verify=False)
        if log_out_response.status_code in [200, 302]:
            print("Log out successful!")