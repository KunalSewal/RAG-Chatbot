import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Settings configuration using environment variables."""

    def __init__(self):
        # OpenRouter API Configuration
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
        # Model Configuration
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.llm_model = os.getenv("LLM_MODEL", "amazon/nova-2-lite")
        self.llm_fallback_model = os.getenv("LLM_FALLBACK_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
        
        # Text Processing
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./database/chatbot.db")
        self.chroma_persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./database/chroma_db")
        
        # Redis Configuration
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        
        # API Configuration
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.api_workers = int(os.getenv("API_WORKERS", "4"))
        
        # Feature Flags
        self.enable_hybrid_search = os.getenv("ENABLE_HYBRID_SEARCH", "true").lower() == "true"
        self.enable_reranking = os.getenv("ENABLE_RERANKING", "false").lower() == "true"
        self.enable_streaming = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
        self.enable_analytics = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "./logs/app.log")
        
        # Paths
        self.data_directory = Path("./data")
        self.logs_directory = Path("./logs")
        self.database_directory = Path("./database")
        self.cache_directory = Path("./cache")
        
        # Ensure directories exist
        self.logs_directory.mkdir(exist_ok=True)
        self.database_directory.mkdir(exist_ok=True)
        self.data_directory.mkdir(exist_ok=True)
        self.cache_directory.mkdir(exist_ok=True)

# Global settings instance
settings = Settings()
