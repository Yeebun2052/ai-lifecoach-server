import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Life Coach API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Use SQLite URL for development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    if DATABASE_URL.startswith("sqlite"):
        DATABASE_URL = DATABASE_URL.replace("sqlite:", "sqlite+pysqlite:", 1)

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # JWT token configuration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"

settings = Settings()