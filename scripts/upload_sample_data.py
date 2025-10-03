"""Upload all sample data to test ingestion"""

import requests
from pathlib import Path
import time
import json

BASE_URL = "http://localhost:8000"


def get_demo_token():
    from app.auth import create_access_token
    return create_access_token({"sub": "demo-user-001", "business_name": "Demo Electronics"})


def upload_csv_file(file_path: Path, source_type: str, token: str):
    """Upload a CSV file"""
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'text/csv')}
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(
            f"{BASE_URL}/api/ingestion/upload/csv?source_type={source_type}",
            files=files,
            headers=headers
        )
    
    return response


def main():
    print("="*60)
    print("📤 Uploading Sample Data to Kaya AI")
    print("="*60)
    print()
    
    token = get_demo_token()
    
    sample_files = [
        ('sample_data/transactions_sample.csv', 'sheets'),
        ('sample_data/mpesa_sample.csv', 'mpesa'),
        ('sample_data/pos_sample.csv', 'pos'),
    ]
    
    results = []
    
    for file_path, source_type in sample_files:
        path = Path(file_path)
        
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        print(f"📤 Uploading {path.name} ({source_type})...")
        
        try:
            response = upload_csv_file(path, source_type, token)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('rows_uploaded')} rows uploaded")
                print(f"   Ingestion ID: {result.get('ingestion_id')}")
                results.append((path.name, result))
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   {response.text}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        time.sleep(1)  # Brief pause between uploads
    
    # Wait for processing
    print("⏳ Waiting for background processing...")
    time.sleep(3)
    
    # Check status of uploads
    print("\n" + "="*60)
    print("📊 Upload Results Summary")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for filename, result in results:
        ingestion_id = result.get('ingestion_id')
        
        if ingestion_id:
            status_response = requests.get(
                f"{BASE_URL}/api/ingestion/status/{ingestion_id}",
                headers=headers
            )
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"\n{filename}:")
                print(f"  Status: {status.get('status')}")
                print(f"  Rows uploaded: {status.get('rows_uploaded')}")
                print(f"  Rows processed: {status.get('rows_processed')}")
                print(f"  Rows skipped: {status.get('rows_skipped', 0)}")
    
    print("\n" + "="*60)
    print("✅ Sample data upload complete!")
    print("="*60)


if __name__ == "__main__":
    main()