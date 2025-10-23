"""Enhanced data processor with flexible CSV parsing"""

import csv
import io
from datetime import datetime
from typing import Dict, List, Any
import hashlib
import logging
import re

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and normalize data from various sources"""
    
    # Column name mappings for flexible parsing
    COLUMN_MAPPINGS = {
        'date': ['date', 'Date', 'DATE', 'timestamp', 'Timestamp', 'time', 'Time', 
                 'completion_time', 'Completion Time', 'transaction_date', 'Transaction Date'],
        'amount': ['amount', 'Amount', 'AMOUNT', 'price', 'Price', 'total', 'Total', 
                   'paid_in', 'Paid In', 'withdrawn', 'Withdrawn', 'value', 'Value'],
        'item': ['item', 'Item', 'ITEM', 'product', 'Product', 'description', 'Description',
                 'details', 'Details', 'name', 'Name', 'transaction_details', 'Transaction Details'],
        'category': ['category', 'Category', 'CATEGORY', 'type', 'Type', 'class', 'Class'],
        'payment_method': ['payment_method', 'Payment Method', 'method', 'Method', 
                          'payment_type', 'Payment Type', 'mode', 'Mode'],
        'receipt_no': ['receipt_no', 'Receipt No', 'receipt', 'Receipt', 'transaction_id', 
                       'Transaction ID', 'id', 'ID']
    }
    
    @staticmethod
    def find_column(headers: List[str], field: str) -> str | None:
        """Find actual column name from headers using mappings"""
        possible_names = DataProcessor.COLUMN_MAPPINGS.get(field, [])
        
        # Exact match first
        for header in headers:
            if header in possible_names:
                return header
        
        # Case-insensitive partial match
        for header in headers:
            header_lower = header.lower().strip()
            for possible in possible_names:
                if possible.lower() in header_lower:
                    return header
        
        return None
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """Parse date from various formats"""
        if not date_str or date_str.strip() == '':
            return datetime.now()
        
        date_str = date_str.strip()
        
        # Common date formats to try
        formats = [
            '%Y-%m-%d',           # 2024-01-15
            '%m/%d/%Y',           # 01/15/2024
            '%d/%m/%Y',           # 15/01/2024
            '%Y/%m/%d',           # 2024/01/15
            '%d-%m-%Y',           # 15-01-2024
            '%d-%b-%Y',           # 15-Jan-2024
            '%d %b %Y',           # 15 Jan 2024
            '%d/%m/%Y %H:%M',     # 15/01/2024 14:30
            '%Y-%m-%d %H:%M:%S',  # 2024-01-15 14:30:00
            '%d/%m/%Y %H:%M:%S',  # 15/01/2024 14:30:00
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all else fails, return current date
        logger.warning(f"Could not parse date: {date_str}, using current date")
        return datetime.now()
    
    @staticmethod
    def parse_amount(amount_str: str) -> float:
        """Parse amount from various formats"""
        if not amount_str:
            return 0.0
        
        # Remove currency symbols, commas, and whitespace
        amount_str = str(amount_str).strip()
        amount_str = re.sub(r'[KES$€£,\s]', '', amount_str)
        
        try:
            return float(amount_str)
        except ValueError:
            logger.warning(f"Could not parse amount: {amount_str}")
            return 0.0
    
    @staticmethod
    def categorize_transaction(item: str, details: str = '') -> str:
        """Auto-categorize transaction based on item description"""
        text = f"{item} {details}".lower()
        
        # Electronics keywords
        if any(word in text for word in ['phone', 'laptop', 'computer', 'tablet', 'tv', 
                                          'electronics', 'camera', 'iphone', 'samsung']):
            return 'Electronics'
        
        # Accessories keywords
        if any(word in text for word in ['case', 'charger', 'cable', 'headphone', 'earphone',
                                          'adapter', 'cover', 'screen protector']):
            return 'Accessories'
        
        # Food keywords
        if any(word in text for word in ['food', 'meal', 'lunch', 'dinner', 'breakfast',
                                          'restaurant', 'cafe', 'snack']):
            return 'Food & Beverage'
        
        # Services keywords
        if any(word in text for word in ['service', 'repair', 'maintenance', 'consultation',
                                          'delivery', 'shipping']):
            return 'Services'
        
        # Default
        return 'Other'
    
    @staticmethod
    def parse_csv(content: bytes, source_type: str = 'csv') -> List[Dict[str, Any]]:
        """Parse CSV content with flexible column mapping"""
        try:
            # Decode content
            text = content.decode('utf-8-sig')  # Handles BOM
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO(text))
            headers = reader.fieldnames or []
            
            if not headers:
                raise ValueError("CSV has no headers")
            
            logger.info(f"CSV headers: {headers}")
            
            # Find column mappings
            date_col = DataProcessor.find_column(headers, 'date')
            amount_col = DataProcessor.find_column(headers, 'amount')
            item_col = DataProcessor.find_column(headers, 'item')
            category_col = DataProcessor.find_column(headers, 'category')
            method_col = DataProcessor.find_column(headers, 'payment_method')
            receipt_col = DataProcessor.find_column(headers, 'receipt_no')
            
            # Validate required columns
            if not date_col and not receipt_col:
                raise ValueError(
                    f"CSV must contain a date/time column. Found columns: {', '.join(headers)}"
                )
            
            if not amount_col:
                raise ValueError(
                    f"CSV must contain an amount column. Found columns: {', '.join(headers)}"
                )
            
            logger.info(f"Column mapping - date: {date_col}, amount: {amount_col}, item: {item_col}")
            
            # Parse rows
            transactions = []
            skipped = 0
            
            for idx, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    # Extract date
                    date_str = row.get(date_col, '') if date_col else ''
                    date = DataProcessor.parse_date(date_str)
                    
                    # Extract amount
                    amount_str = row.get(amount_col, '0')
                    amount = DataProcessor.parse_amount(amount_str)
                    
                    if amount <= 0:
                        logger.warning(f"Row {idx}: Invalid amount {amount_str}, skipping")
                        skipped += 1
                        continue
                    
                    # Extract item/description
                    item = row.get(item_col, 'Unknown Item') if item_col else 'Unknown Item'
                    if not item or item.strip() == '':
                        item = 'Unknown Item'
                    
                    # Extract or infer category
                    category = row.get(category_col, '') if category_col else ''
                    if not category:
                        category = DataProcessor.categorize_transaction(item)
                    
                    # Extract payment method
                    method = row.get(method_col, 'Cash') if method_col else 'Cash'
                    
                    # Generate unique ID
                    receipt_no = row.get(receipt_col, '') if receipt_col else ''
                    unique_id = DataProcessor.generate_transaction_id(
                        date, amount, item, receipt_no
                    )
                    
                    transaction = {
                        'id': unique_id,
                        'date': date.strftime('%Y-%m-%d'),
                        'timestamp': date.isoformat(),
                        'item': item.strip(),
                        'amount': amount,
                        'category': category,
                        'payment_method': method,
                        'source_type': source_type,
                        'receipt_no': receipt_no
                    }
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    logger.warning(f"Row {idx}: Error parsing - {str(e)}, skipping")
                    skipped += 1
                    continue
            
            if not transactions:
                raise ValueError(
                    f"No valid transactions found in CSV. "
                    f"Processed {idx - 1} rows, skipped {skipped}. "
                    f"Please check your data format."
                )
            
            logger.info(f"Successfully parsed {len(transactions)} transactions, skipped {skipped}")
            return transactions
            
        except UnicodeDecodeError:
            raise ValueError("Unable to read CSV file. Please ensure it's saved as UTF-8")
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")
        except Exception as e:
            logger.error(f"CSV parsing error: {str(e)}")
            raise ValueError(f"Failed to parse CSV: {str(e)}")
    
    @staticmethod
    def process_and_ingest(ingestion_id: str, user_id: str, 
                          rows: List[Dict[str, Any]], source_type: str):
        """Process and ingest data into BigQuery (background task)"""
        try:
            logger.info(f"[INGEST] Starting ingestion {ingestion_id} for user {user_id}")
            
            # Normalize for BigQuery
            normalized_rows = DataProcessor.normalize_for_bigquery(rows, user_id)
            
            # Insert into BigQuery
            from app.utils.bigquery_client import bq_client
            bq_client.insert_rows('transactions', normalized_rows)
            
            logger.info(
                f"[INGEST] Completed ingestion {ingestion_id}: "
                f"{len(normalized_rows)} rows inserted"
            )
            
        except Exception as e:
            logger.error(f"[INGEST] Failed ingestion {ingestion_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def generate_transaction_id(date: datetime, amount: float, 
                                item: str, receipt_no: str = '') -> str:
        """Generate unique transaction ID"""
        if receipt_no:
            return hashlib.md5(receipt_no.encode()).hexdigest()[:16]
        
        unique_str = f"{date.isoformat()}{amount}{item}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]
    
    @staticmethod
    def normalize_for_bigquery(transactions: List[Dict[str, Any]], 
                               user_id: str) -> List[Dict[str, Any]]:
        """Normalize transactions for BigQuery insertion"""
        normalized = []
        
        for txn in transactions:
            normalized.append({
                'id': txn['id'],
                'user_id': user_id,
                'date': txn['date'],
                'timestamp': txn['timestamp'],
                'item': txn['item'],
                'amount': txn['amount'],
                'category': txn['category'],
                'payment_method': txn['payment_method'],
                'source': txn['source_type'],
                'metadata': {
                    'receipt_no': txn.get('receipt_no', ''),
                    'processed_at': datetime.now().isoformat()
                }
            })
        
        return normalized