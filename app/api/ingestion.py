from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any
import uuid
import logging

from app.auth import verify_token
from app.utils.bigquery_client import bq_client
from app.models.schemas import IngestionStatus, DataSourceConfig
from app.services.data_processor import DataProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory status tracking (for demo - use Redis in production)
ingestion_status_cache = {}


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
        # Read CSV content as bytes
        content = await file.read()
        logger.info(f"[UPLOAD] Processing CSV: {file.filename}, size: {len(content)} bytes")

        # Parse and validate
        data_processor = DataProcessor()
        rows = data_processor.parse_csv(content, source_type)

        if not rows:
            raise HTTPException(status_code=400, detail="No valid data found in CSV")

        # Generate ingestion ID
        ingestion_id = str(uuid.uuid4())

        # Initialize status
        ingestion_status_cache[ingestion_id] = {
            "ingestion_id": ingestion_id,
            "status": "processing",
            "rows_uploaded": len(rows),
            "rows_processed": 0,
            "message": f"Processing {len(rows)} rows"
        }

        # Log ingestion start
        logger.info(
            f"[UPLOAD] User={user_id} uploading {len(rows)} rows "
            f"for source={source_type}, ingestion_id={ingestion_id}"
        )

        # Process in background
        if background_tasks:
            background_tasks.add_task(
                process_and_ingest_task,
                ingestion_id=ingestion_id,
                user_id=user_id,
                rows=rows,
                source_type=source_type
            )
        else:
            # Fallback: process synchronously
            process_and_ingest_task(ingestion_id, user_id, rows, source_type)

        return IngestionStatus(
            ingestion_id=ingestion_id,
            status="processing",
            rows_uploaded=len(rows),
            message=f"Processing {len(rows)} rows in background"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[UPLOAD] CSV upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to parse CSV: {str(e)}")


def process_and_ingest_task(ingestion_id: str, user_id: str, rows: List[Dict[str, Any]], source_type: str):
    """Background task to process and ingest data into BigQuery"""
    try:
        logger.info(f"[INGEST] Starting ingestion {ingestion_id} for user {user_id}")
        
        # Normalize for BigQuery
        data_processor = DataProcessor()
        normalized_rows = data_processor.normalize_for_bigquery(rows, user_id)
        
        logger.info(f"[INGEST] Normalized {len(normalized_rows)} rows, inserting into BigQuery...")
        
        # Insert into BigQuery
        bq_client.insert_rows('transactions', normalized_rows)
        
        # Update status - SUCCESS
        ingestion_status_cache[ingestion_id] = {
            "ingestion_id": ingestion_id,
            "status": "completed",
            "rows_uploaded": len(rows),
            "rows_processed": len(normalized_rows),
            "message": f"Successfully processed {len(normalized_rows)} rows"
        }
        
        logger.info(f"[INGEST] ✅ Completed ingestion {ingestion_id}: {len(normalized_rows)} rows inserted")
        
    except Exception as e:
        logger.error(f"[INGEST] ❌ Failed ingestion {ingestion_id}: {str(e)}", exc_info=True)
        
        # Update status - FAILED
        ingestion_status_cache[ingestion_id] = {
            "ingestion_id": ingestion_id,
            "status": "failed",
            "rows_uploaded": len(rows),
            "rows_processed": 0,
            "message": f"Error: {str(e)}"
        }


@router.get("/status/{ingestion_id}", response_model=IngestionStatus)
async def get_ingestion_status(
    ingestion_id: str,
    token: dict = Depends(verify_token),
):
    """Check status of data ingestion"""
    # Use the cache directly instead of data_processor.get_status()
    status = ingestion_status_cache.get(ingestion_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Ingestion not found")
    
    logger.info(f"[STATUS] Ingestion {ingestion_id} -> {status['status']}")
    return IngestionStatus(**status)


@router.post("/sync/sheets")
async def sync_google_sheets(
    config: DataSourceConfig,
    token: dict = Depends(verify_token),
):
    """
    Sync data from Google Sheets
    Uses Fivetran-style incremental sync
    """
    user_id = token.get("sub")

    try:
        # TODO: Implement Google Sheets API integration
        return {
            "status": "success",
            "message": "Use /upload/csv endpoint for now",
        }
    except Exception as e:
        logger.error(f"[SYNC] Google Sheets sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/mpesa")
async def sync_mpesa(
    config: DataSourceConfig,
    token: dict = Depends(verify_token),
):
    """Sync M-Pesa transactions (currently CSV only)"""
    user_id = token.get("sub")

    logger.info(f"[SYNC] User={user_id} configured M-Pesa sync")

    return {
        "status": "success",
        "message": "M-Pesa sync configured. Upload M-Pesa CSV statements.",
    }