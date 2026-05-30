import os

class Config:
    SECRET_KEY = "campustrace-secret-key-2024"
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite:///campustrace.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
