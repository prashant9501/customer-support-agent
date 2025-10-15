"""
Application configuration and settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.0
    embedding_model: str = "text-embedding-3-small"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # ChromaDB Configuration
    chromadb_path: str = "./knowledge_base"
    chromadb_collection: str = "knowledge_base"
    
    # RAG Configuration
    rag_top_k: int = 3
    rag_score_threshold: float = 0.2
    
    # Application Settings
    max_query_length: int = 500
    rate_limit_per_minute: int = 10
    session_timeout_hours: int = 24
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "agent.log"
    
    # Security
    allowed_origins: str = "http://localhost:8000,http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Helper function to get settings
def get_settings() -> Settings:
    """Get application settings"""
    return settings
