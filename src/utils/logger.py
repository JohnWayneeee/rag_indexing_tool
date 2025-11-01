"""
Module for detailed logging configuration
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

# Base path for logs
BASE_DIR = Path(__file__).parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log files
GENERAL_LOG = LOG_DIR / "app.log"
INDEXING_LOG = LOG_DIR / "indexing.log"
SEARCH_LOG = LOG_DIR / "search.log"
ERROR_LOG = LOG_DIR / "errors.log"


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True
):
    """
    Configure logging system
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Log to files
        log_to_console: Log to console
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Log format
    detailed_format = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    simple_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Handlers
    handlers = []
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(simple_format))
        handlers.append(console_handler)
    
    # File handlers
    if log_to_file:
        # General log
        general_handler = RotatingFileHandler(
            GENERAL_LOG,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        general_handler.setLevel(logging.DEBUG)
        general_handler.setFormatter(logging.Formatter(detailed_format))
        handlers.append(general_handler)
        
        # Indexing log
        indexing_handler = RotatingFileHandler(
            INDEXING_LOG,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        indexing_handler.setLevel(logging.INFO)
        indexing_handler.setFormatter(logging.Formatter(detailed_format))
        indexing_handler.addFilter(lambda record: 'indexing' in record.name.lower() or 'index' in record.name.lower())
        handlers.append(indexing_handler)
        
        # Search log
        search_handler = RotatingFileHandler(
            SEARCH_LOG,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        search_handler.setLevel(logging.INFO)
        search_handler.setFormatter(logging.Formatter(detailed_format))
        search_handler.addFilter(lambda record: 'search' in record.name.lower())
        handlers.append(search_handler)
        
        # Error log
        error_handler = RotatingFileHandler(
            ERROR_LOG,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(detailed_format))
        handlers.append(error_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Configure logging level for external libraries
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logging.info(f"Logging configured. Level: {level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get logger with specified name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger
    """
    return logging.getLogger(name)


# Initialize logging on module import
# Can be disabled if manual configuration is needed
_initialized = False

def initialize_logging():
    """Initialize logging (called on application startup)"""
    global _initialized
    if not _initialized:
        import sys
        from pathlib import Path
        
        # Add project root to PYTHONPATH if needed
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from src.config.settings import LOGGING_CONFIG
        setup_logging(
            level=LOGGING_CONFIG.get("level", "INFO"),
            log_to_file=True,
            log_to_console=True
        )
        _initialized = True

