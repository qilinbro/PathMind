from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import os

# Create SQLite database directory if it doesn't exist
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
if DATABASE_URL.startswith('sqlite'):
    db_path = DATABASE_URL.replace('sqlite:///', '')
    if not os.path.dirname(db_path) == '':
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Create SQLAlchemy engine
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=True,  # Set to False in production
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}
    )
    print(f"Database engine created successfully with URL: {DATABASE_URL}")
except Exception as e:
    print(f"Failed to create database engine: {e}")
    raise e

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to initialize database
def init_db():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e