"""API endpoints for data source connectors"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
import logging

from app.auth import verify_token
from app.models.schemas import ConnectorConfig, ConnectorStatus, SyncRequest
from app.services.connector_manager import ConnectorManager
from app.services.data_processor import DataProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

connector_manager = ConnectorManager()
data_processor = DataProcessor()


@router.post("/register", response_model=ConnectorStatus)
async def register_connector(
    config: ConnectorConfig,
    token: dict = Depends(verify_token)
):
    """
    Register a new data source connector
    
    Example config for Google Sheets:
    {
        "source_id": "my-sales-sheet",
        "type": "sheets",
        "spreadsheet_id": "1abc...",
        "sheet_name": "Sales",
        "credentials_path": "/path/to/creds.json"
    }
    """
    user_id = token.get("sub")
    
    try:
        connector = connector_manager.register_connector(
            user_id=user_id,
            source_id=config.source_id,
            config=config.dict()
        )
        
        return ConnectorStatus(
            source_id=config.source_id,
            status="connected",
            message="Connector registered successfully"
        )
        
    except ConnectionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Connector registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=Dict[str, Any])
async def trigger_sync(
    sync_request: SyncRequest,
    background_tasks: BackgroundTasks,
    token: dict = Depends(verify_token)
):
    """
    Trigger incremental sync for a data source
    Runs in background and returns immediately
    """
    user_id = token.get("sub")
    
    try:
        # Run sync in background
        background_tasks.add_task(
            _perform_sync,
            user_id=user_id,
            source_id=sync_request.source_id
        )
        
        return {
            "status": "syncing",
            "source_id": sync_request.source_id,
            "message": "Sync started in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _perform_sync(user_id: str, source_id: str):
    """Background task to perform sync"""
    try:
        result = connector_manager.sync(user_id, source_id)
        logger.info(f"Sync completed for {user_id}:{source_id} - {result}")
    except Exception as e:
        logger.error(f"Sync failed for {user_id}:{source_id}: {e}")


@router.get("/status/{source_id}", response_model=ConnectorStatus)
async def get_connector_status(
    source_id: str,
    token: dict = Depends(verify_token)
):
    """Get connector sync status"""
    user_id = token.get("sub")
    
    status = connector_manager.get_connector_status(user_id, source_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    return ConnectorStatus(
        source_id=source_id,
        status="synced",
        last_sync=status.get('last_sync'),
        state=status.get('state')
    )


@router.delete("/{source_id}")
async def delete_connector(
    source_id: str,
    token: dict = Depends(verify_token)
):
    """Disconnect and remove a data source"""
    user_id = token.get("sub")
    key = f"{user_id}:{source_id}"
    
    if key in connector_manager.connectors:
        del connector_manager.connectors[key]
        del connector_manager.sync_states[key]
        
        return {"status": "deleted", "source_id": source_id}
    
    raise HTTPException(status_code=404, detail="Connector not found")
