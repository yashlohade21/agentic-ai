import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
import json
from functools import lru_cache

logger = logging.getLogger(__name__)

# Connection pool for Firebase clients
_firebase_client = None
_firebase_initialized = False

@lru_cache(maxsize=1)
def get_firebase_credentials():
    """Get Firebase credentials with caching"""
    try:
        # Try environment variable first (for Render deployment)
        firebase_secret = os.environ.get('FIREBASE_SECRET_JSON')
        if firebase_secret:
            logger.info("Using Firebase credentials from environment variable")
            return json.loads(firebase_secret)
        
        # Try multiple paths for the service account file
        possible_paths = [
            './google-service.json',  # Current directory
            'google-service.json',    # Relative path
            os.path.join(os.path.dirname(__file__), 'google-service.json'),  # Same directory as this file
            os.environ.get('FIREBASE_SECRET_PATH', ''),  # From env variable path
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                logger.info(f"Found Firebase credentials file at: {path}")
                with open(path, 'r') as f:
                    return json.load(f)
        
        logger.error("Firebase credentials not found in any expected location")
        logger.error(f"Searched paths: {possible_paths}")
        return None
        
    except Exception as e:
        logger.error(f"Error loading Firebase credentials: {e}")
        return None

def initialize_firebase():
    """Initialize Firebase with optimized connection pooling"""
    global _firebase_client, _firebase_initialized
    
    try:
        # Return existing client if already initialized
        if _firebase_initialized and _firebase_client:
            return _firebase_client
            
        # Check if already initialized by another process
        if firebase_admin._apps:
            logger.info("Firebase already initialized by another process")
            _firebase_client = firestore.client()
            _firebase_initialized = True
            return _firebase_client
        
        # Get credentials
        cred_data = get_firebase_credentials()
        if not cred_data:
            raise FileNotFoundError("Firebase credentials not found")
        
        # Initialize Firebase Admin SDK with optimized settings
        cred = credentials.Certificate(cred_data)
        firebase_admin.initialize_app(cred, {
            'projectId': cred_data.get('project_id'),
        })
        
        # Get Firestore client with settings for better performance
        _firebase_client = firestore.client()
        _firebase_initialized = True
        
        logger.info("Firebase initialized successfully with optimized configuration")
        return _firebase_client
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        # Fall back to mock if in development or if credentials missing
        if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('USE_MOCK_FIREBASE', 'false').lower() == 'true':
            logger.warning("Falling back to mock Firebase")
            from firebase_config_mock import MockFirestore
            _firebase_client = MockFirestore()
            _firebase_initialized = True
            return _firebase_client
        raise

# Initialize on module import with better error handling
try:
    db = initialize_firebase()
except Exception as e:
    logger.warning(f"Firebase initialization failed on import: {e}")
    # Use mock in development or when credentials are missing
    if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('USE_MOCK_FIREBASE', 'false').lower() == 'true':
        from firebase_config_mock import MockFirestore
        db = MockFirestore()
    else:
        db = None

def get_firestore_client():
    """Get Firestore client with connection pooling, initializing if necessary"""
    global db, _firebase_client, _firebase_initialized
    
    # Return cached client if available
    if _firebase_initialized and _firebase_client:
        return _firebase_client
    
    # Initialize if needed
    if db is None:
        db = initialize_firebase()
    
    return db

# User data cache to reduce database hits
_user_cache = {}
_cache_ttl = {}
import time

def get_cached_user(user_id, ttl_seconds=300):  # 5 minute cache
    """Get user from cache or database with TTL"""
    current_time = time.time()
    
    # Check if user is cached and not expired
    if (user_id in _user_cache and 
        user_id in _cache_ttl and 
        current_time - _cache_ttl[user_id] < ttl_seconds):
        return _user_cache[user_id]
    
    try:
        # Fetch from database
        db_client = get_firestore_client()
        user_doc = db_client.collection('users').document(user_id).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            # Cache the result
            _user_cache[user_id] = {
                'id': user_doc.id,
                'data': user_data,
                'exists': True
            }
            _cache_ttl[user_id] = current_time
            return _user_cache[user_id]
        else:
            # Cache negative result too
            _user_cache[user_id] = {'exists': False}
            _cache_ttl[user_id] = current_time
            return _user_cache[user_id]
            
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return {'exists': False}

def invalidate_user_cache(user_id=None):
    """Invalidate user cache for specific user or all users"""
    global _user_cache, _cache_ttl
    
    if user_id:
        _user_cache.pop(user_id, None)
        _cache_ttl.pop(user_id, None)
    else:
        _user_cache.clear()
        _cache_ttl.clear()