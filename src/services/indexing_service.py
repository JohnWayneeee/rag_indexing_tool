"""
Document indexing service
"""
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.core.document_processor import DocumentProcessor
from src.core.text_splitter import TextSplitter
from src.core.embeddings import EmbeddingModel
from src.database.chroma_manager import ChromaManager
from src.config.settings import (
    CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_SIZE,
    EMBEDDING_MODEL, EMBEDDING_DEVICE
)

logger = logging.getLogger(__name__)


class IndexingService:
    """Service for indexing documents into vector database"""
    
    def __init__(
        self,
        chroma_manager: ChromaManager,
        embedding_model: Optional[EmbeddingModel] = None
    ):
        """
        Args:
            chroma_manager: ChromaDB manager
            embedding_model: Model for creating embeddings (optional, will be created automatically)
        """
        self.chroma_manager = chroma_manager
        self.document_processor = DocumentProcessor()
        self.text_splitter = TextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            min_chunk_size=MIN_CHUNK_SIZE
        )
        
        # Initialize embedding model
        if embedding_model is None:
            logger.info(f"Initializing embedding model: {EMBEDDING_MODEL}")
            self.embedding_model = EmbeddingModel(
                model_name=EMBEDDING_MODEL,
                device=EMBEDDING_DEVICE
            )
        else:
            self.embedding_model = embedding_model
    
    def index_document(self, file_path: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Index a single document
        
        Args:
            file_path: Path to file
            overwrite: Overwrite existing document
            
        Returns:
            Dictionary with indexing results
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Starting document indexing: {file_path}")
        
        try:
            # 1. Document parsing to Markdown
            document = self.document_processor.process_document(file_path)
            if not document:
                raise ValueError(f"Failed to process document: {file_path}")
            
            # 2. Splitting into chunks
            chunks = self.text_splitter.split_document(document)
            if not chunks:
                raise ValueError(f"Failed to split document into chunks: {file_path}")
            
            logger.info(f"Document split into {len(chunks)} chunks")
            
            # 3. Create embeddings
            chunks_with_embeddings = self.embedding_model.encode_chunks(chunks)
            
            # 4. Prepare data for ChromaDB
            documents = [chunk['text'] for chunk in chunks_with_embeddings]
            embeddings = [chunk['embedding'] for chunk in chunks_with_embeddings]
            metadatas = []
            ids = []
            
            # Create unique ID for document
            import uuid
            document_id = str(uuid.uuid4())
            
            for i, chunk in enumerate(chunks_with_embeddings):
                # Metadata for ChromaDB
                metadata = {
                    'document_id': document_id,
                    'file_path': document['file_path'],
                    'file_name': document['file_name'],
                    'file_type': document['file_type'],
                    'chunk_index': chunk['chunk_index'],
                    'start_char': chunk['start_char'],
                    'end_char': chunk['end_char'],
                    'char_count': chunk['char_count']
                }
                
                # Add additional metadata from document
                if chunk.get('metadata'):
                    doc_meta = chunk['metadata']
                    if 'has_tables' in doc_meta:
                        metadata['has_tables'] = doc_meta['has_tables']
                    if 'tables_count' in doc_meta:
                        metadata['tables_count'] = doc_meta['tables_count']
                    if 'has_images' in doc_meta:
                        metadata['has_images'] = doc_meta['has_images']
                    if 'images_count' in doc_meta:
                        metadata['images_count'] = doc_meta['images_count']
                
                metadatas.append(metadata)
                
                # Create unique ID for chunk
                chunk_id = f"{document_id}_chunk_{i}"
                ids.append(chunk_id)
            
            # 5. If overwrite, delete old data
            if overwrite:
                logger.info(f"Deleting old data for document: {file_path}")
                self.chroma_manager.delete(where={'file_path': file_path})
            
            # 6. Add to ChromaDB
            self.chroma_manager.add_documents(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
            logger.info(f"Document successfully indexed: {file_path} (ID: {document_id}, chunks: {len(chunks)})")
            
            return {
                'success': True,
                'document_id': document_id,
                'chunks_count': len(chunks),
                'file_path': file_path,
                'file_name': document['file_name'],
                'message': f"Document successfully indexed: {len(chunks)} chunks"
            }
            
        except Exception as e:
            logger.error(f"Error indexing document {file_path}: {e}", exc_info=True)
            raise
    
    def index_directory(self, directory_path: str, overwrite: bool = False) -> List[Dict[str, Any]]:
        """
        Index all documents in directory
        
        Args:
            directory_path: Path to directory
            overwrite: Overwrite existing documents
            
        Returns:
            List of indexing results
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        logger.info(f"Starting directory indexing: {directory_path}")
        
        # Get list of files to process
        processed_docs = self.document_processor.process_directory(directory_path)
        
        if not processed_docs:
            logger.warning(f"No documents found for processing in: {directory_path}")
            return []
        
        results = []
        for doc in processed_docs:
            try:
                result = self.index_document(doc['file_path'], overwrite=overwrite)
                results.append(result)
            except Exception as e:
                logger.error(f"Error indexing {doc.get('file_path', 'unknown')}: {e}")
                results.append({
                    'success': False,
                    'file_path': doc.get('file_path', 'unknown'),
                    'message': str(e)
                })
        
        success_count = sum(1 for r in results if r.get('success', False))
        logger.info(f"Indexing completed: {success_count}/{len(results)} successful")
        
        return results
    
    def delete_document(self, document_id: Optional[str] = None, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete document from index
        
        Args:
            document_id: Document ID
            file_path: Path to file
            
        Returns:
            Deletion result
        """
        if not document_id and not file_path:
            raise ValueError("Must specify document_id or file_path")
        
        try:
            # Get document count BEFORE deletion
            count_before = self.chroma_manager.count()
            
            # Check document existence before deletion via query with where filter
            if document_id:
                # Check if document with such document_id exists
                try:
                    # Use query to check existence
                    results = self.chroma_manager.collection.query(
                        query_texts=[""],
                        n_results=1,
                        where={'document_id': document_id},
                        include=['metadatas']
                    )
                    
                    if not results.get('ids') or len(results['ids']) == 0 or len(results['ids'][0]) == 0:
                        raise ValueError(f"Document with ID {document_id} not found in index")
                    
                    # Delete document
                    self.chroma_manager.delete(where={'document_id': document_id})
                    logger.info(f"Deleted document with ID: {document_id}")
                except ValueError:
                    raise
                except Exception as e:
                    # If error occurred during check, still try to delete
                    # and check result by count change
                    logger.warning(f"Failed to check document existence before deletion: {e}")
                    self.chroma_manager.delete(where={'document_id': document_id})
                    count_check = self.chroma_manager.count()
                    if count_check == count_before:
                        raise ValueError(f"Document with ID {document_id} not found in index")
                    logger.info(f"Deleted document with ID: {document_id}")
            else:
                # Check if document with such file_path exists
                try:
                    results = self.chroma_manager.collection.query(
                        query_texts=[""],
                        n_results=1,
                        where={'file_path': file_path},
                        include=['metadatas']
                    )
                    
                    if not results.get('ids') or len(results['ids']) == 0 or len(results['ids'][0]) == 0:
                        raise ValueError(f"Document at path {file_path} not found in index")
                    
                    # Delete document
                    self.chroma_manager.delete(where={'file_path': file_path})
                    logger.info(f"Deleted document: {file_path}")
                except ValueError:
                    raise
                except Exception as e:
                    logger.warning(f"Failed to check document existence before deletion: {e}")
                    self.chroma_manager.delete(where={'file_path': file_path})
                    count_check = self.chroma_manager.count()
                    if count_check == count_before:
                        raise ValueError(f"Document at path {file_path} not found in index")
                    logger.info(f"Deleted document: {file_path}")
            
            # Get document count AFTER deletion
            count_after = self.chroma_manager.count()
            deleted_count = count_before - count_after
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'message': f"Document deleted from index"
            }
        except ValueError as e:
            # Re-raise ValueError as HTTP 404
            raise
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

