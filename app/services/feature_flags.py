"""Feature flags for gradual rollout"""

from typing import Dict
from enum import Enum


class Feature(Enum):
    """Available features"""
    AI_CHAT = "ai_chat"
    ADVANCED_ANALYTICS = "advanced_analytics"
    WEBSOCKET = "websocket"
    CSV_UPLOAD = "csv_upload"
    SHEETS_CONNECTOR = "sheets_connector"
    MPESA_CONNECTOR = "mpesa_connector"


class FeatureFlags:
    """Manage feature flags"""
    
    def __init__(self):
        # Default: all features enabled
        self.flags = {
            Feature.AI_CHAT: True,
            Feature.ADVANCED_ANALYTICS: True,
            Feature.WEBSOCKET: True,
            Feature.CSV_UPLOAD: True,
            Feature.SHEETS_CONNECTOR: True,
            Feature.MPESA_CONNECTOR: True,
        }
        
        # User-specific overrides
        self.user_overrides: Dict[str, Dict[Feature, bool]] = {}
    
    def is_enabled(self, feature: Feature, user_id: str = None) -> bool:
        """Check if feature is enabled"""
        
        # Check user override first
        if user_id and user_id in self.user_overrides:
            if feature in self.user_overrides[user_id]:
                return self.user_overrides[user_id][feature]
        
        # Check global flag
        return self.flags.get(feature, False)
    
    def enable(self, feature: Feature, user_id: str = None):
        """Enable feature globally or for specific user"""
        if user_id:
            if user_id not in self.user_overrides:
                self.user_overrides[user_id] = {}
            self.user_overrides[user_id][feature] = True
        else:
            self.flags[feature] = True
    
    def disable(self, feature: Feature, user_id: str = None):
        """Disable feature"""
        if user_id:
            if user_id not in self.user_overrides:
                self.user_overrides[user_id] = {}
            self.user_overrides[user_id][feature] = False
        else:
            self.flags[feature] = False


feature_flags = FeatureFlags()
