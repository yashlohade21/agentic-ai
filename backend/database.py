import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Load environment variables
load_dotenv()

# Use SQLite for local development
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }  # Required for SQLite
)

# Verify connection on startup
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Successfully connected to SQLite database")
except Exception as e:
    print(f"Failed to connect to SQLite: {e}")
    raise

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

