"""M-Pesa connector (CSV-based for now)"""

from typing import Dict, Any, List, Optional
import csv
import io

from app.connectors.base import BaseConnector


class MPesaConnector(BaseConnector):
    """
    M-Pesa connector
    Supports CSV statement uploads with idempotency via receipt numbers
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.csv_data = config.get('csv_data')
        self.processed_receipts = set(config.get('processed_receipts', []))
    
    def test_connection(self) -> bool:
        """Validate M-Pesa CSV format"""
        try:
            reader = csv.DictReader(io.StringIO(self.csv_data))
            headers = reader.fieldnames
            required = ['Receipt No.', 'Completion Time', 'Paid In', 'Withdrawn']
            return all(h in headers for h in required)
        except:
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            'table': 'transactions',
            'primary_key': ['receipt_no']
        }
    
    def read(self, state: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Read M-Pesa transactions with deduplication
        Uses receipt numbers for idempotency
        """
        if state:
            self.processed_receipts.update(state.get('processed_receipts', []))
        
        reader = csv.DictReader(io.StringIO(self.csv_data))
        records = []
        new_receipts = []
        
        for row in reader:
            receipt_no = row.get('Receipt No.', '')
            
            # Skip if already processed (idempotency)
            if receipt_no in self.processed_receipts:
                continue
            
            records.append(row)
            new_receipts.append(receipt_no)
        
        # Update state
        if new_receipts:
            self.update_state({
                'processed_receipts': list(self.processed_receipts) + new_receipts
            })
        
        logger.info(f"Read {len(records)} new M-Pesa transactions")
        return records

