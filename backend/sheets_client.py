from loguru import logger
from typing import List, Dict, Any, Optional
import os
import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# Configure logging to DEV_MAN/backend.log
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DEV_MAN', 'backend.log'))
logger.add(LOG_PATH, level="INFO", format="{time} | {level} | {message}")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]
CREDENTIALS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'client_secret.json'))
TOKEN_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'token.pickle'))
WORKSPACE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DEV_MAN', 'google_workspace.json'))

class SheetsClient:
    """
    Backend client for Google Sheets API access.
    """
    def __init__(self, sheet_id: Optional[str] = None):
        self.sheet_id = sheet_id
        self.gc = None
        self._authenticate()
        logger.info(f"SheetsClient initialized. Sheet ID: {self.sheet_id}")

    def _authenticate(self):
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            else:
                creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
            self.gc = gspread.authorize(creds)
            logger.success("Authenticated with Google Sheets API.")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self.gc = None

    def set_sheet_id(self, sheet_id: str) -> None:
        self.sheet_id = sheet_id
        logger.info(f"Sheet ID set to: {sheet_id}")

    def _get_spreadsheet(self):
        if not self.gc or not self.sheet_id:
            logger.error("Google Sheets client not authenticated or sheet_id not set.")
            return None
        try:
            ss = self.gc.open_by_key(self.sheet_id)
            logger.success(f"Opened spreadsheet: {ss.title}")
            return ss
        except Exception as e:
            logger.error(f"Error opening spreadsheet: {e}")
            return None

    def get_sheet_names(self) -> List[str]:
        logger.info("Fetching sheet names...")
        ss = self._get_spreadsheet()
        if not ss:
            return []
        try:
            sheet_names = [ws.title for ws in ss.worksheets()]
            logger.success(f"Fetched sheet names: {sheet_names}")
            return sheet_names
        except Exception as e:
            logger.error(f"Error fetching sheet names: {e}")
            return []

    def get_headers(self, sheet_name: str) -> List[str]:
        logger.info(f"Fetching headers for sheet: {sheet_name}")
        ss = self._get_spreadsheet()
        if not ss:
            return []
        try:
            ws = ss.worksheet(sheet_name)
            headers = ws.row_values(1)
            logger.success(f"Fetched headers for {sheet_name}: {headers}")
            return headers
        except Exception as e:
            logger.error(f"Error fetching headers for {sheet_name}: {e}")
            return []

    def get_data(self, sheet_name: str) -> List[Dict[str, Any]]:
        logger.info(f"Fetching data for sheet: {sheet_name}")
        ss = self._get_spreadsheet()
        if not ss:
            return []
        try:
            ws = ss.worksheet(sheet_name)
            records = ws.get_all_records()
            logger.success(f"Fetched {len(records)} records for {sheet_name}")
            return records
        except Exception as e:
            logger.error(f"Error fetching data for {sheet_name}: {e}")
            return []

    def save_template_headers_as_json(self, sheet_name: str, output_json_path: str) -> bool:
        """
        Fetch headers from the specified sheet/tab and save as JSON for use as the Pete template.
        """
        headers = self.get_headers(sheet_name)
        if not headers:
            logger.error(f"No headers found for sheet: {sheet_name}")
            return False
        try:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(headers, f, indent=2)
            logger.success(f"Saved template headers to {output_json_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving headers to JSON: {e}")
            return False

    @staticmethod
    def load_workspace() -> Dict[str, Any]:
        if os.path.exists(WORKSPACE_FILE):
            with open(WORKSPACE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"sheets": []}

    @staticmethod
    def save_workspace(workspace: Dict[str, Any]):
        with open(WORKSPACE_FILE, 'w', encoding='utf-8') as f:
            json.dump(workspace, f, indent=2)

    def log_sheet_to_workspace(self):
        ss = self._get_spreadsheet()
        if not ss:
            return
        workspace = self.load_workspace()
        sheet_entry = {
            "sheet_id": self.sheet_id,
            "spreadsheet_name": ss.title,
            "tabs": [ws.title for ws in ss.worksheets()],
            "last_used": datetime.now().isoformat()
        }
        # Remove any existing entry for this sheet_id
        workspace["sheets"] = [s for s in workspace["sheets"] if s["sheet_id"] != self.sheet_id]
        workspace["sheets"].append(sheet_entry)
        self.save_workspace(workspace)
        logger.success(f"Logged sheet to workspace: {ss.title} ({self.sheet_id})")

    @staticmethod
    def print_workspace():
        workspace = SheetsClient.load_workspace()
        print("\n=== Google Workspace ===")
        for i, sheet in enumerate(workspace["sheets"]):
            print(f"[{i+1}] {sheet['spreadsheet_name']} (ID: {sheet['sheet_id']}) Tabs: {', '.join(sheet['tabs'])} Last used: {sheet['last_used']}")
        print("========================\n")

    @staticmethod
    def select_sheet_from_workspace() -> Optional[str]:
        workspace = SheetsClient.load_workspace()
        if not workspace["sheets"]:
            return None
        SheetsClient.print_workspace()
        while True:
            resp = input("Select a sheet by number, or press Enter to enter a new Sheet ID: ").strip()
            if not resp:
                return None
            try:
                idx = int(resp) - 1
                if 0 <= idx < len(workspace["sheets"]):
                    return workspace["sheets"][idx]["sheet_id"]
            except Exception:
                pass
            print("Invalid selection. Try again.")

# Example usage (for testing)
if __name__ == "__main__":
    print("Welcome to Pete Google Sheets Workspace!")
    SheetsClient.print_workspace()
    SHEET_ID = SheetsClient.select_sheet_from_workspace()
    if not SHEET_ID:
        SHEET_ID = input("Enter Google Sheet ID: ").strip()
    client = SheetsClient()
    client.set_sheet_id(SHEET_ID)
    client.log_sheet_to_workspace()
    names = client.get_sheet_names()
    print(f"Sheet names: {names}")
    for name in names:
        headers = client.get_headers(name)
        print(f"Headers for {name}: {headers}")
        data = client.get_data(name)
        print(f"First 2 rows for {name}: {data[:2]}") 