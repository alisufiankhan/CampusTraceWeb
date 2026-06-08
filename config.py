import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    SECRET_KEY = "campustrace-secret-key-2024"
    # For production (Vercel), we'll read DATABASE_URL or POSTGRES_URL
    database_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or os.environ.get("TEST_DATABASE_URL") or "sqlite:///campustrace.db"
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
