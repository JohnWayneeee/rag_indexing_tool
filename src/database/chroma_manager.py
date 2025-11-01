"""
Module for managing ChromaDB collections
"""
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Tuple
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class ChromaManager:
    """Manager for working with ChromaDB"""
    
    def __init__(
        self,
        persist_directory: str,
        collection_name: str = "documents",
        embedding_function=None
    ):
        """
        Args:
            persist_directory: Path to directory for database storage
            collection_name: Collection name
            embedding_function: Function for creating embeddings (optional, can use external)
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_function = embedding_function
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        logger.info(f"ChromaDB initialized. Collection: {collection_name}, Path: {persist_directory}")
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Found existing collection: {self.collection_name}")
            return collection
        except Exception:
            # Create new collection
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "RAG indexing collection for documents"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
            return collection
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to collection
        
        Args:
            documents: List of document texts
            metadatas: List of metadata for each document
            embeddings: List of embeddings (optional, if None, ChromaDB will create them)
            ids: List of document IDs (optional, will be generated automatically)
            
        Returns:
            List of added document IDs
        """
        if not documents:
            logger.warning("Empty list of documents for adding")
            return []
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # Check size matching
        if len(documents) != len(metadatas) or len(documents) != len(ids):
            raise ValueError("List sizes must match")
        
        try:
            # If embeddings not provided, ChromaDB will create them automatically
            # But for performance it's better to pass ready ones
            if embeddings is not None:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings,
                    ids=ids
                )
            else:
                # Use embedding_function if provided
                if self.embedding_function:
                    embeddings = [self.embedding_function(doc) for doc in documents]
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        embeddings=embeddings,
                        ids=ids
                    )
                else:
                    # ChromaDB will create embeddings itself (default uses SentenceTransformer)
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
            
            logger.info(f"Added {len(documents)} documents to collection")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query_texts: List[str],
        n_results: int = 10,
        query_embeddings: Optional[List[List[float]]] = None,
        where: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform semantic search
        
        Args:
            query_texts: List of query texts
            n_results: Number of results for each query
            query_embeddings: Ready query embeddings (optional)
            where: Metadata filter
            include: What to include in result (default: ['metadatas', 'documents', 'distances'])
            
        Returns:
            Dictionary with search results
        """
        if include is None:
            include = ['metadatas', 'documents', 'distances']
        
        try:
            if query_embeddings is not None:
                # Use ready embeddings
                results = self.collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results,
                    where=where,
                    include=include
                )
            else:
                # ChromaDB will create embeddings itself
                results = self.collection.query(
                    query_texts=query_texts,
                    n_results=n_results,
                    where=where,
                    include=include
                )
            
            logger.debug(f"Found results: {len(results.get('ids', [{}])[0]) if results.get('ids') else 0}")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None):
        """
        Delete documents from collection
        
        Args:
            ids: List of document IDs to delete
            where: Metadata filter for deletion
        """
        try:
            self.collection.delete(ids=ids, where=where)
            
            deleted_count = len(ids) if ids else "by filter"
            logger.info(f"Deleted documents: {deleted_count}")
            
        except Exception as e:
            logger.error(f"Delete error: {e}")
            raise
    
    def update(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        Update documents in collection
        
        Args:
            ids: List of document IDs to update
            documents: New document texts
            metadatas: New metadata
            embeddings: New embeddings
        """
        try:
            self.collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            logger.info(f"Updated {len(ids)} documents")
            
        except Exception as e:
            logger.error(f"Update error: {e}")
            raise
    
    def get_by_id(self, ids: List[str], include: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get documents by ID
        
        Args:
            ids: List of document IDs
            include: What to include in result
            
        Returns:
            Dictionary with documents
        """
        if include is None:
            include = ['metadatas', 'documents', 'embeddings']
        
        try:
            results = self.collection.get(ids=ids, include=include)
            return results
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            raise
    
    def count(self) -> int:
        """Returns number of documents in collection"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
    
    def reset(self):
        """Delete entire collection and recreate"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self._get_or_create_collection()
            logger.warning(f"Collection {self.collection_name} has been reset")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Return collection information"""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "path": str(self.persist_directory)
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "name": self.collection_name,
                "count": 0,
                "path": str(self.persist_directory)
            }
    
    def get_all_documents(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get all documents from collection
        
        Args:
            limit: Maximum number of documents
            offset: Offset for pagination (ChromaDB doesn't support directly, so used via limit)
            where: Metadata filter
            
        Returns:
            Dictionary with documents in ChromaDB format
        """
        try:
            # ChromaDB get() doesn't support where directly in old versions
            # Use query() with empty query or get() without where
            if where:
                # For metadata filtering use query with empty query
                # This will return all documents matching the filter
                all_count = self.collection.count()
                fetch_limit = limit if limit else all_count
                if offset and limit:
                    fetch_limit = offset + limit
                
                # Use query with empty string to get all documents with filter
                results = self.collection.query(
                    query_texts=[""],
                    n_results=fetch_limit if fetch_limit else all_count,
                    where=where,
                    include=['metadatas', 'documents']
                )
                
                # Convert query format to get format
                ids_list = results.get('ids', [[]])
                documents_list = results.get('documents', [[]])
                metadatas_list = results.get('metadatas', [[]])
                
                ids = ids_list[0] if ids_list else []
                documents = documents_list[0] if documents_list else []
                metadatas = metadatas_list[0] if metadatas_list else []
                
                # Apply offset if needed
                if offset and offset > 0:
                    start = offset
                    end = offset + limit if limit else len(ids)
                    ids = ids[start:end]
                    documents = documents[start:end] if documents else []
                    metadatas = metadatas[start:end] if metadatas else []
                elif limit and len(ids) > limit:
                    ids = ids[:limit]
                    documents = documents[:limit] if documents else []
                    metadatas = metadatas[:limit] if metadatas else []
                
                return {
                    'ids': ids,
                    'documents': documents,
                    'metadatas': metadatas
                }
            else:
                # Without filter use get()
                if limit or offset:
                    fetch_limit = None
                    if offset and limit:
                        fetch_limit = offset + limit
                    elif limit:
                        fetch_limit = limit
                    
                    results = self.collection.get(
                        limit=fetch_limit,
                        include=['metadatas', 'documents']
                    )
                    
                    if offset and offset > 0:
                        ids = results.get('ids', [])
                        documents = results.get('documents', [])
                        metadatas = results.get('metadatas', [])
                        
                        start = offset
                        end = offset + limit if limit else len(ids)
                        
                        return {
                            'ids': ids[start:end],
                            'documents': documents[start:end] if documents else [],
                            'metadatas': metadatas[start:end] if metadatas else []
                        }
                    elif limit and results.get('ids'):
                        ids = results.get('ids', [])
                        return {
                            'ids': ids[:limit],
                            'documents': results.get('documents', [])[:limit] if results.get('documents') else [],
                            'metadatas': results.get('metadatas', [])[:limit] if results.get('metadatas') else []
                        }
                    return results
                else:
                    return self.collection.get(
                        include=['metadatas', 'documents']
                    )
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            raise
    
    def get_documents_by_document_id(self, document_id: str) -> Dict[str, Any]:
        """
        Get all document chunks by document_id
        
        Args:
            document_id: Document ID
            
        Returns:
            Dictionary with document chunks
        """
        try:
            # Use query to filter by metadata
            all_count = self.collection.count()
            results = self.collection.query(
                query_texts=[""],
                n_results=all_count,
                where={'document_id': document_id},
                include=['metadatas', 'documents']
            )
            
            # Convert query format to get format
            ids_list = results.get('ids', [[]])
            documents_list = results.get('documents', [[]])
            metadatas_list = results.get('metadatas', [[]])
            
            return {
                'ids': ids_list[0] if ids_list else [],
                'documents': documents_list[0] if documents_list else [],
                'metadatas': metadatas_list[0] if metadatas_list else []
            }
        except Exception as e:
            logger.error(f"Error getting documents by document_id: {e}")
            raise
    
    def get_unique_documents(self) -> List[Dict[str, Any]]:
        """
        Get list of unique documents (by document_id) with chunk count information
        
        Returns:
            List of dictionaries with information about each unique document
        """
        try:
            # Get all documents
            all_results = self.collection.get(
                include=['metadatas']
            )
            
            if not all_results.get('ids'):
                return []
            
            metadatas = all_results['metadatas']
            ids = all_results['ids']
            
            # Group by document_id
            documents_map = {}
            for i, metadata in enumerate(metadatas):
                doc_id = metadata.get('document_id', '')
                if not doc_id:
                    continue
                
                if doc_id not in documents_map:
                    documents_map[doc_id] = {
                        'document_id': doc_id,
                        'file_path': metadata.get('file_path', ''),
                        'file_name': metadata.get('file_name', ''),
                        'file_type': metadata.get('file_type', ''),
                        'chunks_count': 0,
                        'chunk_ids': []
                    }
                
                documents_map[doc_id]['chunks_count'] += 1
                documents_map[doc_id]['chunk_ids'].append(ids[i])
            
            return list(documents_map.values())
            
        except Exception as e:
            logger.error(f"Error getting unique documents: {e}")
            raise

