import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import logging
from collections import defaultdict

from app.utils.bigquery_client import bq_client

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data parsing, normalization, and ingestion with idempotency"""
    
    def __init__(self):
        self.ingestion_status = {}
        self.processed_hashes = set()  # For idempotency
    
    def parse_csv(self, csv_text: str, source_type: str) -> List[Dict[str, Any]]:
        """Parse CSV based on source type"""
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        
        if source_type == "mpesa":
            return self._parse_mpesa_csv(rows)
        elif source_type == "pos":
            return self._parse_pos_csv(rows)
        else:  # sheets or generic
            return self._parse_generic_csv(rows)
    
    def _parse_mpesa_csv(self, rows: List[Dict]) -> List[Dict[str, Any]]:
        """Parse M-Pesa statement format"""
        parsed = []
        
        for row in rows:
            try:
                # M-Pesa CSV columns: Receipt No., Completion Time, Details, Transaction Status, Paid In, Withdrawn, Balance
                parsed.append({
                    'receipt_no': row.get('Receipt No.', ''),
                    'completion_time': row.get('Completion Time', ''),
                    'details': row.get('Details', ''),
                    'status': row.get('Transaction Status', ''),
                    'paid_in': float(row.get('Paid In', 0) or 0),
                    'withdrawn': float(row.get('Withdrawn', 0) or 0),
                    'balance': float(row.get('Balance', 0) or 0),
                })
            except Exception as e:
                logger.warning(f"Skipping invalid M-Pesa row: {e}")
                continue
        
        return parsed
    
    def _parse_pos_csv(self, rows: List[Dict]) -> List[Dict[str, Any]]:
        """Parse POS system export"""
        parsed = []
        
        for row in rows:
            try:
                # Common POS columns: Date, Item, Quantity, Price, Total, Payment Method
                parsed.append({
                    'date': row.get('Date', ''),
                    'item': row.get('Item', ''),
                    'quantity': int(row.get('Quantity', 1)),
                    'price': float(row.get('Price', 0)),
                    'total': float(row.get('Total', 0)),
                    'payment_method': row.get('Payment Method', 'Cash'),
                })
            except Exception as e:
                logger.warning(f"Skipping invalid POS row: {e}")
                continue
        
        return parsed
    
    def _parse_generic_csv(self, rows: List[Dict]) -> List[Dict[str, Any]]:
        """Parse generic/Google Sheets format"""
        # Flexible parser - detect common column names
        parsed = []
        
        for row in rows:
            try:
                # Try to extract standard fields
                parsed_row = {}
                
                # Date field
                for date_col in ['date', 'Date', 'transaction_date', 'Date of Transaction']:
                    if date_col in row:
                        parsed_row['date'] = row[date_col]
                        break
                
                # Amount field
                for amt_col in ['amount', 'Amount', 'total', 'Total', 'price', 'Price']:
                    if amt_col in row:
                        parsed_row['amount'] = float(row[amt_col] or 0)
                        break
                
                # Item/Description
                for item_col in ['item', 'Item', 'description', 'Description', 'product', 'Product']:
                    if item_col in row:
                        parsed_row['item'] = row[item_col]
                        break
                
                # Category
                for cat_col in ['category', 'Category', 'type', 'Type']:
                    if cat_col in row:
                        parsed_row['category'] = row[cat_col]
                        break
                
                # Payment method
                for pay_col in ['payment_method', 'Payment Method', 'method', 'Method']:
                    if pay_col in row:
                        parsed_row['payment_method'] = row[pay_col]
                        break
                
                if parsed_row:
                    parsed.append(parsed_row)
                    
            except Exception as e:
                logger.warning(f"Skipping invalid row: {e}")
                continue
        
        return parsed
    
    def normalize_transactions(
        self,
        rows: List[Dict[str, Any]],
        user_id: str,
        source_type: str
    ) -> List[Dict[str, Any]]:
        """Normalize to BigQuery transactions schema"""
        normalized = []
        
        for row in rows:
            try:
                # Generate row hash for idempotency
                row_hash = self._generate_hash(row)
                
                if row_hash in self.processed_hashes:
                    continue  # Skip duplicate
                
                # Normalize based on source
                if source_type == "mpesa":
                    normalized_row = self._normalize_mpesa(row, user_id)
                elif source_type == "pos":
                    normalized_row = self._normalize_pos(row, user_id)
                else:
                    normalized_row = self._normalize_generic(row, user_id, source_type)
                
                if normalized_row:
                    normalized.append(normalized_row)
                    self.processed_hashes.add(row_hash)
                    
            except Exception as e:
                logger.error(f"Normalization error: {e}")
                continue
        
        return normalized
    
    def _normalize_mpesa(self, row: Dict, user_id: str) -> Dict[str, Any]:
        """Normalize M-Pesa transaction"""
        amount = row['paid_in'] if row['paid_in'] > 0 else row['withdrawn']
        
        return {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'source': 'mpesa',
            'amount': float(amount),
            'currency': 'KES',
            'date': self._parse_date(row['completion_time']),
            'timestamp': self._parse_timestamp(row['completion_time']),
            'category': self._categorize_mpesa(row['details']),
            'item_name': row['details'],
            'payment_method': 'M-Pesa',
            'status': row['status'],
            'metadata': {'receipt_no': row['receipt_no']},
            'created_at': datetime.utcnow().isoformat(),
        }
    
    def _normalize_pos(self, row: Dict, user_id: str) -> Dict[str, Any]:
        """Normalize POS transaction"""
        return {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'source': 'pos',
            'amount': float(row['total']),
            'currency': 'KES',
            'date': self._parse_date(row['date']),
            'timestamp': self._parse_timestamp(row['date']),
            'category': 'Retail',
            'item_name': row['item'],
            'payment_method': row['payment_method'],
            'status': 'completed',
            'metadata': {'quantity': row['quantity'], 'unit_price': row['price']},
            'created_at': datetime.utcnow().isoformat(),
        }
    
    def _normalize_generic(self, row: Dict, user_id: str, source: str) -> Dict[str, Any]:
        """Normalize generic/sheets transaction"""
        return {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'source': source,
            'amount': float(row.get('amount', 0)),
            'currency': 'KES',
            'date': self._parse_date(row.get('date', '')),
            'timestamp': self._parse_timestamp(row.get('date', '')),
            'category': row.get('category', 'Other'),
            'item_name': row.get('item', 'N/A'),
            'payment_method': row.get('payment_method', 'Unknown'),
            'status': 'completed',
            'metadata': {},
            'created_at': datetime.utcnow().isoformat(),
        }
    
    def _generate_hash(self, row: Dict) -> str:
        """Generate hash for idempotency check"""
        row_str = str(sorted(row.items()))
        return hashlib.md5(row_str.encode()).hexdigest()
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        if not date_str:
            return datetime.utcnow().date().isoformat()
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%Y/%m/%d',
            '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%d %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date().isoformat()
            except:
                continue
        
        return datetime.utcnow().date().isoformat()
    
    def _parse_timestamp(self, date_str: str) -> str:
        """Parse timestamp string to ISO format"""
        if not date_str:
            return datetime.utcnow().isoformat()
        
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).isoformat()
            except:
                continue
        
        return datetime.utcnow().isoformat()
    
    def _categorize_mpesa(self, details: str) -> str:
        """Categorize M-Pesa transaction from details"""
        details_lower = details.lower()
        
        if any(word in details_lower for word in ['sent', 'transfer', 'paid']):
            return 'Payment'
        elif any(word in details_lower for word in ['received', 'deposit']):
            return 'Income'
        elif 'withdraw' in details_lower:
            return 'Withdrawal'
        else:
            return 'Other'
    
    def process_and_ingest(
        self,
        ingestion_id: str,
        user_id: str,
        rows: List[Dict],
        source_type: str
    ):
        """Process and ingest data to BigQuery (background task)"""
        try:
            self.ingestion_status[ingestion_id] = {
                'status': 'processing',
                'rows_uploaded': len(rows),
                'rows_processed': 0
            }
            
            # Normalize
            normalized = self.normalize_transactions(rows, user_id, source_type)
            
            # Batch insert to BigQuery
            batch_size = 500
            for i in range(0, len(normalized), batch_size):
                batch = normalized[i:i + batch_size]
                bq_client.insert_rows('transactions', batch)
            
            self.ingestion_status[ingestion_id] = {
                'status': 'completed',
                'rows_uploaded': len(rows),
                'rows_processed': len(normalized),
                'rows_skipped': len(rows) - len(normalized)
            }
            
            logger.info(f"Ingestion {ingestion_id} completed: {len(normalized)} rows")
            
        except Exception as e:
            logger.error(f"Ingestion {ingestion_id} failed: {e}")
            self.ingestion_status[ingestion_id] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def get_status(self, ingestion_id: str) -> Optional[Dict]:
        """Get ingestion status"""
        return self.ingestion_status.get(ingestion_id)

