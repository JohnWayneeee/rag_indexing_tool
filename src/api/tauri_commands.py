"""
Tauri commands for native calls from Rust
These functions can be called directly from Tauri application
"""
import logging
from typing import Optional, Dict, Any, List
import os

import sys
from pathlib import Path

# Add project root to PYTHONPATH
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.database.chroma_manager import ChromaManager
from src.core.embeddings import EmbeddingModel
from src.services.indexing_service import IndexingService
from src.services.search_service import SearchService
from src.database.models import SearchQuery
from src.config.settings import (
    CHROMA_DB_PATH, COLLECTION_NAME,
    EMBEDDING_MODEL, EMBEDDING_DEVICE
)

logger = logging.getLogger(__name__)

# Global objects (lazy initialization)
_chroma_manager: Optional[ChromaManager] = None
_embedding_model: Optional[EmbeddingModel] = None
_indexing_service: Optional[IndexingService] = None
_search_service: Optional[SearchService] = None


def _get_services():
    """Lazy service initialization"""
    global _chroma_manager, _embedding_model, _indexing_service, _search_service
    
    if _chroma_manager is None:
        logger.info("Initializing services for Tauri commands")
        
        # Initialize model
        _embedding_model = EmbeddingModel(
            model_name=EMBEDDING_MODEL,
            device=EMBEDDING_DEVICE
        )
        
        # Initialize ChromaDB
        _chroma_manager = ChromaManager(
            persist_directory=CHROMA_DB_PATH,
            collection_name=COLLECTION_NAME
        )
        
        # Initialize services
        _indexing_service = IndexingService(
            chroma_manager=_chroma_manager,
            embedding_model=_embedding_model
        )
        
        _search_service = SearchService(
            chroma_manager=_chroma_manager,
            embedding_model=_embedding_model
        )
        
        logger.info("Services initialized")
    
    return _indexing_service, _search_service, _chroma_manager


def tauri_index_document(file_path: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Index document (Tauri command)
    
    Args:
        file_path: Path to file
        overwrite: Overwrite existing
        
    Returns:
        Indexing result
    """
    try:
        indexing_service, _, _ = _get_services()
        result = indexing_service.index_document(file_path, overwrite=overwrite)
        return result
    except Exception as e:
        logger.error(f"Error in tauri_index_document: {e}", exc_info=True)
        return {
            'success': False,
            'message': str(e)
        }


def tauri_search(
    query: str,
    top_k: int = 10,
    min_score: Optional[float] = None,
    filter_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Perform search (Tauri command)
    
    Args:
        query: Query text
        top_k: Number of results
        min_score: Minimum score
        filter_metadata: Metadata filter
        
    Returns:
        Search results
    """
    try:
        _, search_service, _ = _get_services()
        
        search_query = SearchQuery(
            query=query,
            top_k=top_k,
            min_score=min_score,
            filter_metadata=filter_metadata
        )
        
        response = search_service.search(search_query)
        
        # Convert Pydantic models to dictionaries for JSON
        return {
            'results': [
                {
                    'text': r.text,
                    'score': r.score,
                    'chunk_index': r.chunk_index,
                    'metadata': r.metadata.dict() if hasattr(r.metadata, 'dict') else r.metadata,
                    'document_id': r.document_id
                }
                for r in response.results
            ],
            'query': response.query,
            'total_results': response.total_results,
            'search_time_ms': response.search_time_ms
        }
    except Exception as e:
        logger.error(f"Error in tauri_search: {e}", exc_info=True)
        return {
            'results': [],
            'query': query,
            'total_results': 0,
            'search_time_ms': 0.0,
            'error': str(e)
        }


def tauri_delete_document(
    document_id: Optional[str] = None,
    file_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete document (Tauri command)
    
    Args:
        document_id: Document ID
        file_path: Path to file
        
    Returns:
        Deletion result
    """
    try:
        indexing_service, _, _ = _get_services()
        result = indexing_service.delete_document(document_id, file_path)
        return result
    except Exception as e:
        logger.error(f"Error in tauri_delete_document: {e}", exc_info=True)
        return {
            'success': False,
            'message': str(e)
        }


def tauri_get_status() -> Dict[str, Any]:
    """
    Get system status (Tauri command)
    
    Returns:
        System status
    """
    try:
        _, _, chroma_manager = _get_services()
        embedding_dim = _embedding_model.get_embedding_dim() if _embedding_model else 384
        
        return {
            'status': 'running',
            'total_documents': chroma_manager.count(),
            'database_path': CHROMA_DB_PATH,
            'collection_name': COLLECTION_NAME,
            'embedding_model': EMBEDDING_MODEL,
            'embedding_dim': embedding_dim
        }
    except Exception as e:
        logger.error(f"Error in tauri_get_status: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e)
        }


def tauri_index_directory(directory_path: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Index directory (Tauri command)
    
    Args:
        directory_path: Path to directory
        overwrite: Overwrite existing
        
    Returns:
        Indexing results
    """
    try:
        indexing_service, _, _ = _get_services()
        
        if not os.path.exists(directory_path):
            return {
                'success': False,
                'message': f"Directory not found: {directory_path}"
            }
        
        results = indexing_service.index_directory(directory_path, overwrite=overwrite)
        success_count = sum(1 for r in results if r.get('success', False))
        
        return {
            'success': True,
            'total_files': len(results),
            'successful': success_count,
            'failed': len(results) - success_count,
            'results': results
        }
    except Exception as e:
        logger.error(f"Error in tauri_index_directory: {e}", exc_info=True)
        return {
            'success': False,
            'message': str(e)
        }

