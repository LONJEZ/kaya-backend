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
        # Read CSV content as bytes (data_processor.parse_csv expects bytes)
        content = await file.read()
        
        logger.info(f"[UPLOAD] Processing CSV: {file.filename}, size: {len(content)} bytes")

        # Parse and validate
        rows = data_processor.parse_csv(content, source_type)

        if not rows:
            raise HTTPException(status_code=400, detail="No valid data found in CSV")

        # Generate ingestion ID
        ingestion_id = str(uuid.uuid4())

        # Log ingestion start
        logger.info(
            f"[UPLOAD] User={user_id} uploading {len(rows)} rows "
            f"for source={source_type}, ingestion_id={ingestion_id}"
        )

        # Process in background
        background_tasks.add_task(
            data_processor.process_and_ingest,
            ingestion_id=ingestion_id,
            user_id=user_id,
            rows=rows,
            source_type=source_type,
        )

        return IngestionStatus(
            ingestion_id=ingestion_id,
            status="processing",
            rows_uploaded=len(rows),
            message=f"Processing {len(rows)} rows in background",
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"[UPLOAD] CSV upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to parse CSV: {str(e)}")


@router.get("/status/{ingestion_id}", response_model=IngestionStatus)
async def get_ingestion_status(
    ingestion_id: str,
    token: dict = Depends(verify_token),
):
    """Check status of data ingestion"""
    status = data_processor.get_status(ingestion_id)

    if not status:
        raise HTTPException(status_code=404, detail="Ingestion not found")

    logger.info(f"[STATUS] Ingestion {ingestion_id} -> {status}")
    return status


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
