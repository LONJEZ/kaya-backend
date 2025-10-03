"""Verify data was loaded into BigQuery"""

from app.utils.bigquery_client import bq_client
from app.config import settings


def verify_data():
    print("="*60)
    print("🔍 Verifying BigQuery Data")
    print("="*60)
    print()
    
    # Check transactions count
    query = f"""
    SELECT 
        source,
        COUNT(*) as count,
        SUM(amount) as total_amount,
        MIN(date) as earliest_date,
        MAX(date) as latest_date
    FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
    GROUP BY source
    ORDER BY source
    """
    
    print("📊 Transactions by Source:")
    print("-" * 60)
    
    try:
        results = bq_client.query(query)
        
        if not results:
            print("⚠️  No data found in transactions table")
            return
        
        total_count = 0
        total_amount = 0
        
        for row in results:
            print(f"\nSource: {row['source']}")
            print(f"  Count: {row['count']}")
            print(f"  Total Amount: KES {row['total_amount']:,.2f}")
            print(f"  Date Range: {row['earliest_date']} to {row['latest_date']}")
            
            total_count += row['count']
            total_amount += row['total_amount']
        
        print("\n" + "="*60)
        print(f"Total Transactions: {total_count}")
        print(f"Total Amount: KES {total_amount:,.2f}")
        print("="*60)
        
        # Check for duplicates
        dup_query = f"""
        SELECT 
            item_name,
            date,
            amount,
            COUNT(*) as count
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        GROUP BY item_name, date, amount
        HAVING COUNT(*) > 1
        LIMIT 10
        """
        
        dup_results = bq_client.query(dup_query)
        
        if dup_results:
            print("\n⚠️  Potential Duplicates Found:")
            for row in dup_results:
                print(f"  {row['item_name']} ({row['date']}): {row['count']} copies")
        else:
            print("\n✅ No duplicates detected")
    
    except Exception as e:
        print(f"❌ Error querying BigQuery: {e}")


if __name__ == "__main__":
    verify_data()

