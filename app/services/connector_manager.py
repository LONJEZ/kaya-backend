"""Manage data source connectors"""

from typing import Dict, Any, Optional
import logging

from app.connectors.sheets_connector import SheetsConnector
from app.connectors.mpesa_connector import MPesaConnector
from app.utils.bigquery_client import bq_client

logger = logging.getLogger(__name__)


class ConnectorManager:
    """Manages connector lifecycle and sync operations"""
    
    def __init__(self):
        self.connectors = {}
        self.sync_states = {}  # Store in-memory, migrate to BigQuery later
    
    def register_connector(self, user_id: str, source_id: str, config: Dict[str, Any]):
        """Register a new data source connector"""
        connector_type = config.get('type')
        
        if connector_type == 'sheets':
            connector = SheetsConnector(config)
        elif connector_type == 'mpesa':
            connector = MPesaConnector(config)
        else:
            raise ValueError(f"Unsupported connector type: {connector_type}")
        
        # Test connection
        if not connector.test_connection():
            raise ConnectionError("Failed to connect to data source")
        
        key = f"{user_id}:{source_id}"
        self.connectors[key] = connector
        
        logger.info(f"Registered {connector_type} connector for {user_id}")
        return connector
    
    def sync(self, user_id: str, source_id: str) -> Dict[str, Any]:
        """
        Perform incremental sync for a connector
        
        Returns sync results with row counts
        """
        key = f"{user_id}:{source_id}"
        connector = self.connectors.get(key)
        
        if not connector:
            raise ValueError(f"Connector not found: {key}")
        
        # Get last state
        state = self.sync_states.get(key)
        
        # Read new data
        records = connector.read(state=state)
        
        if not records:
            return {
                'status': 'completed',
                'rows_synced': 0,
                'message': 'No new data'
            }
        
        # TODO: Transform and load to BigQuery
        # For now, just update state
        self.sync_states[key] = connector.get_state()
        
        return {
            'status': 'completed',
            'rows_synced': len(records),
            'last_sync': datetime.utcnow().isoformat(),
            'state': connector.get_state()
        }
    
    def get_connector_status(self, user_id: str, source_id: str) -> Optional[Dict]:
        """Get connector sync status"""
        key = f"{user_id}:{source_id}"
        state = self.sync_states.get(key)
        
        if not state:
            return None
        
        return {
            'source_id': source_id,
            'state': state,
            'last_sync': state.get('last_sync')
        }

