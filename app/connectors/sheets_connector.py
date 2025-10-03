"""Google Sheets connector with incremental sync"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

from app.connectors.base import BaseConnector


class SheetsConnector(BaseConnector):
    """
    Google Sheets connector
    Supports incremental sync by tracking last row processed
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.spreadsheet_id = config.get('spreadsheet_id')
        self.sheet_name = config.get('sheet_name', 'Sheet1')
        self.credentials_path = config.get('credentials_path')
        self.client = None
    
    def _get_client(self):
        """Initialize Google Sheets client"""
        if not self.client:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scope
            )
            self.client = gspread.authorize(creds)
        return self.client
    
    def test_connection(self) -> bool:
        """Test Google Sheets access"""
        try:
            client = self._get_client()
            sheet = client.open_by_key(self.spreadsheet_id)
            return True
        except Exception as e:
            logger.error(f"Sheets connection test failed: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Get schema from sheet headers"""
        client = self._get_client()
        sheet = client.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)
        headers = sheet.row_values(1)
        
        return {
            'table': 'transactions',
            'columns': headers,
            'primary_key': ['id']
        }
    
    def read(self, state: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Read data from Google Sheets with incremental sync
        
        State format: {'last_row': 100}
        Only reads rows after last_row
        """
        client = self._get_client()
        sheet = client.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)
        
        # Get headers
        headers = sheet.row_values(1)
        
        # Determine start row for incremental sync
        last_row = state.get('last_row', 1) if state else 1
        start_row = last_row + 1
        
        # Get all rows from start_row onwards
        all_values = sheet.get_all_values()
        
        if len(all_values) <= start_row:
            logger.info("No new rows to sync")
            return []
        
        new_rows = all_values[start_row:]
        
        # Convert to dicts
        records = []
        for idx, row in enumerate(new_rows):
            if len(row) < len(headers):
                row.extend([''] * (len(headers) - len(row)))
            
            record = dict(zip(headers, row))
            record['_row_number'] = start_row + idx
            records.append(record)
        
        # Update state
        if records:
            self.update_state({'last_row': start_row + len(records) - 1})
        
        logger.info(f"Read {len(records)} new rows from sheet")
        return records
