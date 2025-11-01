"""
Module for loading configuration from config.yaml and environment variables
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = BASE_DIR / "config.yaml"
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
BACKUPS_DIR = DATA_DIR / "backups"
UPLOADS_DIR = DATA_DIR / "uploads"

# Create directories if they don't exist
for directory in [VECTOR_DB_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, BACKUPS_DIR, UPLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    import logging
    _logger = logging.getLogger(__name__)
    
    if not CONFIG_FILE.exists():
        _logger.warning(f"Config file {CONFIG_FILE} not found, using default values")
        return get_default_config()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        # Override values from environment variables
        config = override_with_env(config)
        return config
    except Exception as e:
        _logger.error(f"Error loading configuration: {e}")
        return get_default_config()


def override_with_env(config: Dict[str, Any]) -> Dict[str, Any]:
    """Override configuration values from environment variables"""
    # Vector database path
    if os.getenv("CHROMA_DB_PATH"):
        config.setdefault("database", {})["path"] = os.getenv("CHROMA_DB_PATH")
    
    # Embedding model
    if os.getenv("EMBEDDING_MODEL"):
        config.setdefault("embeddings", {})["model"] = os.getenv("EMBEDDING_MODEL")
    
    # Computing device
    if os.getenv("EMBEDDING_DEVICE"):
        config.setdefault("embeddings", {})["device"] = os.getenv("EMBEDDING_DEVICE")
    
    # Chunk size
    if os.getenv("CHUNK_SIZE"):
        try:
            config.setdefault("document_processing", {})["chunk_size"] = int(os.getenv("CHUNK_SIZE"))
        except ValueError:
            pass
    
    # Chunk overlap
    if os.getenv("CHUNK_OVERLAP"):
        try:
            config.setdefault("document_processing", {})["chunk_overlap"] = int(os.getenv("CHUNK_OVERLAP"))
        except ValueError:
            pass
    
    return config


def get_default_config() -> Dict[str, Any]:
    """Return default configuration"""
    return {
        "app": {
            "name": "RAG Indexing Tool",
            "version": "1.0.0"
        },
        "document_processing": {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "supported_formats": [".pdf", ".docx", ".txt", ".pptx", ".html", ".xlsx"]
        },
        "embeddings": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "device": "cpu"
        },
        "database": {
            "type": "chromadb",
            "path": str(VECTOR_DB_DIR),
            "collection_name": "documents"
        },
        "paths": {
            "raw_data": str(RAW_DATA_DIR),
            "processed_data": str(PROCESSED_DATA_DIR),
            "backups": str(BACKUPS_DIR)
        }
    }


# Load configuration
_config = load_config()

# Application settings
APP_NAME = _config.get("app", {}).get("name", "RAG Indexing Tool")
APP_VERSION = _config.get("app", {}).get("version", "1.0.0")

# Document processing settings
DOCUMENT_SETTINGS = _config.get("document_processing", {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "supported_formats": [".pdf", ".docx", ".txt", ".pptx", ".html", ".xlsx"]
})

CHUNK_SIZE = DOCUMENT_SETTINGS.get("chunk_size", 1000)
CHUNK_OVERLAP = DOCUMENT_SETTINGS.get("chunk_overlap", 200)
MIN_CHUNK_SIZE = 500  # Minimum chunk size
SUPPORTED_FORMATS = DOCUMENT_SETTINGS.get("supported_formats", [])

# Embedding settings
EMBEDDING_SETTINGS = _config.get("embeddings", {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "device": "cpu"
})

EMBEDDING_MODEL = EMBEDDING_SETTINGS.get("model", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DEVICE = EMBEDDING_SETTINGS.get("device", "cpu")

# Database settings
DATABASE_SETTINGS = _config.get("database", {
    "type": "chromadb",
    "path": str(VECTOR_DB_DIR),
    "collection_name": "documents"
})

CHROMA_DB_PATH = DATABASE_SETTINGS.get("path", str(VECTOR_DB_DIR))
COLLECTION_NAME = DATABASE_SETTINGS.get("collection_name", "documents")

# Path settings
PATH_SETTINGS = _config.get("paths", {
    "raw_data": str(RAW_DATA_DIR),
    "processed_data": str(PROCESSED_DATA_DIR),
    "backups": str(BACKUPS_DIR)
})

# Logging settings
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S"
}

# API settings
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "false").lower() == "true"
