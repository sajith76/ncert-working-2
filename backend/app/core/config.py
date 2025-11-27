"""
Configuration module for NCERT AI Learning Backend.
Loads environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Info
    APP_NAME: str = "NCERT AI Learning Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # MongoDB Atlas
    MONGO_URI: str
    
    # Google Gemini AI
    GEMINI_API_KEY: str
    
    # Pinecone Vector Database
    PINECONE_API_KEY: str
    PINECONE_INDEX: str
    PINECONE_HOST: str
    
    # CORS Settings
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Optional fields (for compatibility)
    OPENAI_API_KEY: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env


# Create global settings instance
settings = Settings()
