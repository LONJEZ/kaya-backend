"""Base connector following Fivetran SDK patterns"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Base class for data source connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state = {}  # For incremental sync
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection to data source is valid"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return schema definition for this connector"""
        pass
    
    @abstractmethod
    def read(self, state: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Read data from source with incremental sync support
        
        Args:
            state: Last sync state (cursor values, timestamps, etc.)
        
        Returns:
            List of records to insert/update
        """
        pass
    
    def update_state(self, new_state: Dict[str, Any]):
        """Update connector state for next sync"""
        self.state.update(new_state)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current connector state"""
        return self.state

