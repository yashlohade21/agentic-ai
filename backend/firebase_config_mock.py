import logging
import json
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class MockDocument:
    """Mock Firestore document"""
    
    def __init__(self, doc_id: str, data: Dict[str, Any] = None, exists: bool = False):
        self.id = doc_id
        self._data = data or {}
        self._exists = exists
    
    def exists(self):
        return self._exists
    
    def to_dict(self):
        return self._data.copy() if self._data else {}
    
    def get(self):
        return self

class MockCollection:
    """Mock Firestore collection"""
    
    def __init__(self, name: str):
        self.name = name
        self._documents = {}  # Store mock documents
    
    def document(self, doc_id: str = None):
        if doc_id is None:
            # Generate a mock document ID
            doc_id = f"mock_doc_{int(time.time() * 1000)}"
        
        class MockDocumentRef:
            def __init__(self, collection, doc_id):
                self.collection = collection
                self.id = doc_id
            
            def get(self):
                # Return mock document data for common users
                if self.collection.name == 'users':
                    if doc_id in self.collection._documents:
                        return MockDocument(doc_id, self.collection._documents[doc_id], True)
                    else:
                        # Return a default test user for auth testing
                        mock_user_data = {
                            'username': 'testuser',
                            'email': 'test@example.com',
                            'hashed_password': 'scrypt:32768:8:1$H8q7Z8oM$a1b2c3d4e5f6'
                        }
                        return MockDocument(doc_id, mock_user_data, True)
                return MockDocument(doc_id, {}, False)
            
            def set(self, data):
                self.collection._documents[doc_id] = data
                logger.info(f"Mock: Set document {doc_id} in collection {self.collection.name}")
            
            def update(self, data):
                if doc_id in self.collection._documents:
                    self.collection._documents[doc_id].update(data)
                else:
                    self.collection._documents[doc_id] = data
                logger.info(f"Mock: Updated document {doc_id} in collection {self.collection.name}")
            
            def delete(self):
                if doc_id in self.collection._documents:
                    del self.collection._documents[doc_id]
                logger.info(f"Mock: Deleted document {doc_id} from collection {self.collection.name}")
        
        return MockDocumentRef(self, doc_id)
    
    def where(self, field: str, op: str, value: Any):
        """Mock where query"""
        class MockQuery:
            def __init__(self, collection, field, op, value):
                self.collection = collection
                self.field = field
                self.op = op
                self.value = value
            
            def limit(self, count):
                return self
            
            def stream(self):
                # Return mock results for common queries
                results = []
                if self.field == 'username' and self.value == 'testuser':
                    results.append(MockDocument('test_user_id', {
                        'username': 'testuser',
                        'email': 'test@example.com',
                        'hashed_password': 'scrypt:32768:8:1$H8q7Z8oM$a1b2c3d4e5f6'
                    }, True))
                return results
        
        return MockQuery(self, field, op, value)

class MockFirestore:
    """Mock Firestore client"""
    
    def __init__(self):
        self._collections = {}
        logger.info("Initialized mock Firestore client")
    
    def collection(self, name: str):
        if name not in self._collections:
            self._collections[name] = MockCollection(name)
        return self._collections[name]

# Create mock database instance
db = MockFirestore()

# Mock functions for compatibility
def get_cached_user(user_id, ttl_seconds=300):
    """Mock cached user function"""
    # Return a test user for auth testing
    if user_id == 'test_user_id':
        return {
            'id': user_id,
            'data': {
                'username': 'testuser',
                'email': 'test@example.com',
                'hashed_password': 'scrypt:32768:8:1$H8q7Z8oM$a1b2c3d4e5f6'
            },
            'exists': True
        }
    return {'exists': False}

def invalidate_user_cache(user_id=None):
    """Mock cache invalidation"""
    pass

def get_firestore_client():
    """Mock get firestore client"""
    return db
