import csv
import io
from typing import List, Dict, Any
from datetime import datetime
import hashlib
import uuid
import logging

from app.utils.bigquery_client import bq_client

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data parsing, normalization, and ingestion with idempotency"""

    def __init__(self):
        # Store ingestion status in memory
        self.ingestion_status: Dict[str, Dict[str, Any]] = {}
        self.processed_hashes = set()  # For idempotency

    # -------------------------------
    # CSV Parsing
    # -------------------------------
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
        parsed = []
        for row in rows:
            try:
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
        return parsed

    def _parse_pos_csv(self, rows: List[Dict]) -> List[Dict[str, Any]]:
        parsed = []
        for row in rows:
            try:
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
        return parsed

    def _parse_generic_csv(self, rows: List[Dict]) -> List[Dict[str, Any]]:
        parsed = []
        for row in rows:
            try:
                parsed_row = {}

                for date_col in ['date', 'Date', 'transaction_date', 'Date of Transaction']:
                    if date_col in row:
                        parsed_row['date'] = row[date_col]
                        break

                for amt_col in ['amount', 'Amount', 'total', 'Total', 'price', 'Price']:
                    if amt_col in row:
                        parsed_row['amount'] = float(row[amt_col] or 0)
                        break

                for item_col in ['item', 'Item', 'description', 'Description', 'product', 'Product']:
                    if item_col in row:
                        parsed_row['item'] = row[item_col]
                        break

                for cat_col in ['category', 'Category', 'type', 'Type']:
                    if cat_col in row:
                        parsed_row['category'] = row[cat_col]
                        break

                for pay_col in ['payment_method', 'Payment Method', 'method', 'Method']:
                    if pay_col in row:
                        parsed_row['payment_method'] = row[pay_col]
                        break

                if parsed_row:
                    parsed.append(parsed_row)
            except Exception as e:
                logger.warning(f"Skipping invalid row: {e}")
        return parsed

    # -------------------------------
    # Normalization
    # -------------------------------
    def normalize_transactions(
        self,
        rows: List[Dict[str, Any]],
        user_id: str,
        source_type: str
    ) -> List[Dict[str, Any]]:
        normalized = []
        for row in rows:
            try:
                row_hash = self._generate_hash(row)
                if row_hash in self.processed_hashes:
                    continue  # Skip duplicates

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
        return normalized

    def _normalize_mpesa(self, row: Dict, user_id: str) -> Dict[str, Any]:
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

    # -------------------------------
    # Helpers
    # -------------------------------
    def _generate_hash(self, row: Dict) -> str:
        row_str = str(sorted(row.items()))
        return hashlib.md5(row_str.encode()).hexdigest()

    def _parse_date(self, date_str: str) -> str:
        if not date_str:
            return datetime.utcnow().date().isoformat()
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
        details_lower = details.lower()
        if any(word in details_lower for word in ['sent', 'transfer', 'paid']):
            return 'Payment'
        elif any(word in details_lower for word in ['received', 'deposit']):
            return 'Income'
        elif 'withdraw' in details_lower:
            return 'Withdrawal'
        else:
            return 'Other'

    # -------------------------------
    # Ingestion
    # -------------------------------
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
                'rows_processed': 0,
                'rows_skipped': 0,
                'error': None
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
                'rows_skipped': len(rows) - len(normalized),
                'error': None
            }

            logger.info(f"Ingestion {ingestion_id} completed: {len(normalized)} rows")

        except Exception as e:
            logger.error(f"Ingestion {ingestion_id} failed: {e}")
            self.ingestion_status[ingestion_id] = {
                'status': 'failed',
                'rows_uploaded': len(rows),
                'rows_processed': 0,
                'rows_skipped': 0,
                'error': str(e)
            }

    def get_status(self, ingestion_id: str):
        """Retrieve ingestion status by ID"""
        status = self.ingestion_status.get(ingestion_id)
        if not status:
            return None
        return {"ingestion_id": ingestion_id, **status}
