from database import Base, engine
from routes import models  # Import all your SQLAlchemy models here

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")

if __name__ == "__main__":
    init_db()