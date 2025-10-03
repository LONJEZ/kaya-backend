from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any
import csv
import io
import uuid
from datetime import datetime
import logging

from app.auth import verify_token
from app.utils.bigquery_client import bq_client
from app.models.schemas import IngestionStatus, DataSourceConfig
from app.services.data_processor import DataProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

data_processor = DataProcessor()


@router.post("/upload/csv", response_model=IngestionStatus)
async def upload_csv(
    file: UploadFile = File(...),
    source_type: str = "sheets",
    background_tasks: BackgroundTasks = None,
    token: dict = Depends(verify_token)
):
    """
    Upload CSV file for ingestion
    Supports: Google Sheets exports, M-Pesa statements, POS exports
    """
    user_id = token.get("sub")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        # Read CSV content
        content = await file.read()
        csv_text = content.decode('utf-8')
        
        # Parse and validate
        rows = data_processor.parse_csv(csv_text, source_type)
        
        if not rows:
            raise HTTPException(status_code=400, detail="No valid data found in CSV")
        
        # Generate ingestion ID
        ingestion_id = str(uuid.uuid4())
        
        # Process in background
        background_tasks.add_task(
            data_processor.process_and_ingest,
            ingestion_id=ingestion_id,
            user_id=user_id,
            rows=rows,
            source_type=source_type
        )
        
        return IngestionStatus(
            ingestion_id=ingestion_id,
            status="processing",
            rows_uploaded=len(rows),
            message=f"Processing {len(rows)} rows"
        )
        
    except Exception as e:
        logger.error(f"CSV upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{ingestion_id}", response_model=IngestionStatus)
async def get_ingestion_status(
    ingestion_id: str,
    token: dict = Depends(verify_token)
):
    """Check status of data ingestion"""
    status = data_processor.get_status(ingestion_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Ingestion not found")
    
    return status


@router.post("/sync/sheets")
async def sync_google_sheets(
    config: DataSourceConfig,
    token: dict = Depends(verify_token)
):
    """
    Sync data from Google Sheets
    Uses Fivetran-style incremental sync
    """
    user_id = token.get("sub")
    
    try:
        # TODO: Implement Google Sheets API integration
        # For now, direct CSV upload
        return {
            "status": "success",
            "message": "Use CSV upload endpoint for now"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/mpesa")
async def sync_mpesa(
    config: DataSourceConfig,
    token: dict = Depends(verify_token)
):
    """Sync M-Pesa transactions"""
    user_id = token.get("sub")
    
    # Mock M-Pesa integration
    return {
        "status": "success",
        "message": "M-Pesa sync configured. Upload M-Pesa CSV statements."
    }

