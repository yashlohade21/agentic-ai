# Mock Firebase configuration for testing
import logging

logger = logging.getLogger(__name__)

class MockFirestore:
    """Mock Firestore database for testing"""
    
    def __init__(self):
        self.data = {}
        logger.info("Using mock Firestore database")
    
    def collection(self, collection_name):
        return MockCollection(collection_name, self.data)

class MockCollection:
    """Mock Firestore collection"""
    
    def __init__(self, name, data):
        self.name = name
        self.data = data
        if name not in self.data:
            self.data[name] = {}
    
    def document(self, doc_id):
        return MockDocument(self.name, doc_id, self.data)
    
    def add(self, data):
        import uuid
        doc_id = str(uuid.uuid4())
        self.data[self.name][doc_id] = data
        return MockDocumentReference(self.name, doc_id, self.data), None

class MockDocument:
    """Mock Firestore document"""
    
    def __init__(self, collection_name, doc_id, data):
        self.collection_name = collection_name
        self.doc_id = doc_id
        self.data = data
    
    def get(self):
        doc_data = self.data.get(self.collection_name, {}).get(self.doc_id)
        return MockDocumentSnapshot(doc_data, self.doc_id)
    
    def set(self, data):
        if self.collection_name not in self.data:
            self.data[self.collection_name] = {}
        self.data[self.collection_name][self.doc_id] = data
    
    def update(self, data):
        if self.collection_name not in self.data:
            self.data[self.collection_name] = {}
        if self.doc_id not in self.data[self.collection_name]:
            self.data[self.collection_name][self.doc_id] = {}
        self.data[self.collection_name][self.doc_id].update(data)

class MockDocumentSnapshot:
    """Mock Firestore document snapshot"""
    
    def __init__(self, data, doc_id):
        self._data = data
        self.id = doc_id
    
    def exists(self):
        return self._data is not None
    
    def to_dict(self):
        return self._data or {}

class MockDocumentReference:
    """Mock Firestore document reference"""
    
    def __init__(self, collection_name, doc_id, data):
        self.collection_name = collection_name
        self.id = doc_id
        self.data = data

# Create mock database instance
db = MockFirestore()

logger.info("Firebase mock configuration loaded successfully")

