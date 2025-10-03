#!/bin/bash
# ============================================================================
# FILE: update_phase2.sh
# ============================================================================
# Update existing backend to Phase 2

echo "🔄 Updating Kaya AI Backend to Phase 2"
echo "========================================"

# Create new directories
mkdir -p app/connectors
mkdir -p app/services
mkdir -p sample_data

# Install new dependencies
echo "📦 Installing new dependencies..."
pip install gspread==5.12.0 google-auth==2.25.2

# Create sample CSV files
echo "📝 Creating sample data files..."

# Sample 1: Generic transactions
cat > sample_data/transactions_sample.csv << 'EOF'
Date,Item,Amount,Category,Payment Method
2025-10-01,iPhone 15 Pro,120000,Electronics,M-Pesa
2025-10-01,Samsung Galaxy A54,45000,Electronics,Card
2025-10-02,Phone Case,1200,Accessories,Cash
2025-10-02,Bluetooth Speaker,4500,Electronics,M-Pesa
2025-10-03,USB-C Cable,800,Accessories,Cash
2025-10-03,Laptop HP,65000,Electronics,Bank Transfer
2025-10-04,Headphones Sony,8500,Electronics,M-Pesa
2025-10-04,Screen Protector,500,Accessories,Cash
2025-10-05,Power Bank,3500,Accessories,M-Pesa
2025-10-05,Wireless Mouse,1500,Accessories,Card
EOF

# Sample 2: M-Pesa statement
cat > sample_data/mpesa_sample.csv << 'EOF'
Receipt No.,Completion Time,Details,Transaction Status,Paid In,Withdrawn,Balance
SLK1ABC123,01/10/2025 14:30:00,Received from JOHN DOE 0712345678,Completed,5000,0,25000
SLK2DEF456,01/10/2025 15:45:00,Sent to JANE SMITH 0723456789 for goods,Completed,0,2000,23000
SLK3GHI789,02/10/2025 09:15:00,Withdraw from Agent 12345,Completed,0,3000,20000
SLK4JKL012,02/10/2025 11:30:00,Received from PETER MWANGI 0734567890,Completed,15000,0,35000
SLK5MNO345,03/10/2025 08:20:00,Paid to SAFARICOM for airtime,Completed,0,500,34500
SLK6PQR678,03/10/2025 14:10:00,Received from MARY WANJIKU 0745678901,Completed,8000,0,42500
SLK7STU901,04/10/2025 10:05:00,Sent to JAMES KAMAU 0756789012 for rent,Completed,0,25000,17500
SLK8VWX234,04/10/2025 16:45:00,Received from LUCY AKINYI 0767890123,Completed,12000,0,29500
SLK9YZA567,05/10/2025 09:30:00,Paid to KPLC for electricity,Completed,0,3500,26000
SLK0BCD890,05/10/2025 13:15:00,Received from DAVID OMONDI 0778901234,Completed,20000,0,46000
EOF

# Sample 3: POS export
cat > sample_data/pos_sample.csv << 'EOF'
Date,Item,Quantity,Price,Total,Payment Method
2025-10-01,iPhone 15 Pro,1,120000,120000,M-Pesa
2025-10-01,Phone Case,2,1200,2400,Cash
2025-10-02,Bluetooth Speaker,1,4500,4500,Card
2025-10-02,USB-C Cable,3,800,2400,Cash
2025-10-03,Samsung Galaxy A54,1,45000,45000,M-Pesa
2025-10-03,Screen Protector,5,500,2500,Cash
2025-10-04,Laptop HP,1,65000,65000,Bank Transfer
2025-10-04,Wireless Mouse,2,1500,3000,Cash
2025-10-05,Headphones Sony,1,8500,8500,M-Pesa
2025-10-05,Power Bank,2,3500,7000,Card
EOF

echo "✅ Sample data files created in sample_data/"

# Update main.py to include new routers
echo "🔧 Updating main.py..."

# Create backup
cp app/main.py app/main.py.backup

# Add new imports and routers (you'll need to do this manually or use sed)
echo "⚠️  Manual step required:"
echo "   Add these imports to app/main.py:"
echo "   from app.api import ingestion, connectors"
echo ""
echo "   Add these routers:"
echo "   app.include_router(ingestion.router, prefix='/api/ingestion', tags=['Data Ingestion'])"
echo "   app.include_router(connectors.router, prefix='/api/connectors', tags=['Connectors'])"

# Test the setup
echo ""
echo "🧪 Testing Phase 2 setup..."
python3 -c "
try:
    from app.services.data_processor import DataProcessor
    from app.connectors.base import BaseConnector
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
"

echo ""
echo "✅ Phase 2 Update Complete!"
echo "=========================="
echo ""
echo "Next steps:"
echo "1. Update app/main.py with new router imports"
echo "2. Test CSV upload: python3 scripts/test_connectors.py"
echo "3. Upload sample data via API"
echo ""
echo "Sample data available in: sample_data/"
echo "  - transactions_sample.csv (generic format)"
echo "  - mpesa_sample.csv (M-Pesa statement)"
echo "  - pos_sample.csv (POS export)"
