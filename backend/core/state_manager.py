from typing import Dict, Any, Optional, List
import json
import asyncio
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, storage_type: str = "memory", **kwargs):
        self.storage_type = storage_type
        self.memory_store = {}
        
        if storage_type == "file":
            self.file_path = Path(kwargs.get('file_path', 'agent_state.json'))
            self.load_from_file()
    
    async def set_state(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set state value"""
        serialized_value = json.dumps({
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "ttl": ttl
        })
        
        self.memory_store[key] = serialized_value
        
        if self.storage_type == "file":
            self.save_to_file()
    
    async def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        try:
            serialized_value = self.memory_store.get(key)
            
            if serialized_value:
                data = json.loads(serialized_value)
                return data["value"]
            
            return default
            
        except Exception as e:
            logger.error(f"Error getting state for key {key}: {e}")
            return default
    
    async def delete_state(self, key: str):
        """Delete state value"""
        self.memory_store.pop(key, None)
        
        if self.storage_type == "file":
            self.save_to_file()
    
    async def get_all_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern"""
        return list(self.memory_store.keys())
    
    def save_to_file(self):
        """Save memory store to file"""
        if self.storage_type == "file":
            try:
                with open(self.file_path, 'w') as f:
                    json.dump(self.memory_store, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving state to file: {e}")
    
    def load_from_file(self):
        """Load state from file"""
        if self.storage_type == "file" and self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    self.memory_store = json.load(f)
            except Exception as e:
                logger.error(f"Error loading state from file: {e}")
                self.memory_store = {}
