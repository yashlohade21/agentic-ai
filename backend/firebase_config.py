import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase Admin SDK
FIREBASE_SECRET_PATH = os.getenv("FIREBASE_SECRET_PATH")

if FIREBASE_SECRET_PATH:
    cred = credentials.Certificate(FIREBASE_SECRET_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    raise Exception("FIREBASE_SECRET_PATH environment variable not set.")