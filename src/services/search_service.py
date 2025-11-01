"""
Semantic search service
"""
import logging
import time
from typing import List, Dict, Any, Optional

from src.database.chroma_manager import ChromaManager
from src.database.models import SearchQuery, SearchResult, SearchResponse
from src.core.embeddings import EmbeddingModel
from src.utils.cache import cached_query, get_query_cache
from src.config.settings import EMBEDDING_MODEL, EMBEDDING_DEVICE

logger = logging.getLogger(__name__)


class SearchService:
    """Service for semantic search in vector database"""
    
    def __init__(
        self,
        chroma_manager: ChromaManager,
        embedding_model: Optional[EmbeddingModel] = None
    ):
        """
        Args:
            chroma_manager: ChromaDB manager
            embedding_model: Model for creating embeddings (optional)
        """
        self.chroma_manager = chroma_manager
        
        # Initialize embedding model
        if embedding_model is None:
            logger.info(f"Initializing embedding model for search: {EMBEDDING_MODEL}")
            self.embedding_model = EmbeddingModel(
                model_name=EMBEDDING_MODEL,
                device=EMBEDDING_DEVICE
            )
        else:
            self.embedding_model = embedding_model
    
    def search(self, query: SearchQuery, use_cache: bool = True) -> SearchResponse:
        """
        Perform semantic search
        
        Args:
            query: SearchQuery object with search parameters
            use_cache: Use cache for results
            
        Returns:
            SearchResponse with results
        """
        start_time = time.time()
        
        logger.info(f"Executing search: '{query.query[:50]}...' (top_k={query.top_k})")
        
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode_single(query.query, normalize=True)
            query_embeddings = [query_embedding.tolist()]
            
            # Prepare filter
            where_filter = None
            if query.filter_metadata:
                where_filter = query.filter_metadata
            
            # Execute search in ChromaDB
            results = self.chroma_manager.search(
                query_texts=[query.query],
                query_embeddings=query_embeddings,
                n_results=query.top_k,
                where=where_filter,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Process results
            search_results = []
            
            if results.get('ids') and len(results['ids']) > 0:
                ids = results['ids'][0]
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                
                for i in range(len(ids)):
                    # ChromaDB returns distances (smaller = closer)
                    # Convert to score (larger = better)
                    # For cosine distance: score = 1 - distance
                    distance = distances[i]
                    score = max(0.0, 1.0 - distance)
                    
                    # Apply minimum score threshold
                    if query.min_score is not None and score < query.min_score:
                        continue
                    
                    metadata_dict = metadatas[i]
                    
                    # Create result object
                    from src.database.models import DocumentMetadata
                    
                    # Create metadata object
                    metadata_obj = DocumentMetadata(
                        file_path=metadata_dict.get('file_path', ''),
                        file_name=metadata_dict.get('file_name', ''),
                        file_type=metadata_dict.get('file_type', ''),
                        chunk_index=metadata_dict.get('chunk_index', 0),
                        document_id=metadata_dict.get('document_id', ''),
                        file_size=metadata_dict.get('file_size'),
                        creation_time=metadata_dict.get('creation_time'),
                        modification_time=metadata_dict.get('modification_time')
                    )
                    
                    search_result = SearchResult(
                        text=documents[i],
                        score=score,
                        chunk_index=metadata_dict.get('chunk_index', 0),
                        metadata=metadata_obj,
                        document_id=metadata_dict.get('document_id')
                    )
                    
                    search_results.append(search_result)
            
            search_time_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Search completed: found {len(search_results)} results in {search_time_ms:.2f}ms")
            
            return SearchResponse(
                results=search_results,
                query=query.query,
                total_results=len(search_results),
                search_time_ms=search_time_ms
            )
            
        except Exception as e:
            logger.error(f"Error executing search: {e}", exc_info=True)
            raise
    
    def search_simple(
        self,
        query_text: str,
        top_k: int = 10,
        min_score: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> SearchResponse:
        """
        Simplified search method
        
        Args:
            query_text: Query text
            top_k: Number of results
            min_score: Minimum score
            filter_metadata: Metadata filter
            
        Returns:
            SearchResponse with results
        """
        query = SearchQuery(
            query=query_text,
            top_k=top_k,
            min_score=min_score,
            filter_metadata=filter_metadata
        )
        return self.search(query)
    
    def clear_cache(self):
        """Clear search results cache"""
        cache = get_query_cache()
        cache.clear()
        logger.info("Search results cache cleared")

