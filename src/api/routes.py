"""
FastAPI routes for REST API
"""
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import shutil
from pathlib import Path
import sys

# Add project root to PYTHONPATH
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.database.models import (
    SearchQuery, SearchResponse,
    IndexRequest, IndexResponse,
    DeleteRequest, DeleteResponse,
    StatusResponse
)
from src.database.chroma_manager import ChromaManager
from src.core.embeddings import EmbeddingModel
from src.services.indexing_service import IndexingService
from src.services.search_service import SearchService
from src.config.settings import (
    CHROMA_DB_PATH, COLLECTION_NAME,
    EMBEDDING_MODEL, EMBEDDING_DEVICE,
    UPLOADS_DIR
)
from src.core.document_processor import SUPPORTED_EXTENSIONS
from src.utils.logger import initialize_logging

# Initialize logging
initialize_logging()

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="RAG Indexing Tool API",
    version="1.0.0",
    description="API for document indexing and search"
)

# CORS middleware for Tauri integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production restrict domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global objects (initialized on startup)
chroma_manager: Optional[ChromaManager] = None
embedding_model: Optional[EmbeddingModel] = None
indexing_service: Optional[IndexingService] = None
search_service: Optional[SearchService] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global chroma_manager, embedding_model, indexing_service, search_service
    
    try:
        logger.info("Initializing services...")
        
        # Initializing embedding model
        logger.info(f"Loading model: {EMBEDDING_MODEL}")
        embedding_model = EmbeddingModel(
            model_name=EMBEDDING_MODEL,
            device=EMBEDDING_DEVICE
        )
        
        # Initialize ChromaDB
        logger.info(f"Initializing ChromaDB: {CHROMA_DB_PATH}")
        chroma_manager = ChromaManager(
            persist_directory=CHROMA_DB_PATH,
            collection_name=COLLECTION_NAME
        )
        
        # Initialize services
        indexing_service = IndexingService(
            chroma_manager=chroma_manager,
            embedding_model=embedding_model
        )
        
        search_service = SearchService(
            chroma_manager=chroma_manager,
            embedding_model=embedding_model
        )
        
        logger.info("All services successfully initialized")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}", exc_info=True)
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Indexing Tool API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check"""
    try:
        if chroma_manager is None:
            return {"status": "error", "message": "ChromaDB not initialized"}
        
        count = chroma_manager.count()
        return {
            "status": "healthy",
            "database": {
                "connected": True,
                "documents_count": count
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status"""
    try:
        if chroma_manager is None or embedding_model is None:
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        count = chroma_manager.count()
        embedding_dim = embedding_model.get_embedding_dim()
        
        return StatusResponse(
            status="running",
            total_documents=count,
            total_chunks=count,  # ChromaDB counts chunks as documents
            database_path=CHROMA_DB_PATH,
            collection_name=COLLECTION_NAME,
            embedding_model=EMBEDDING_MODEL,
            embedding_dim=embedding_dim
        )
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery):
    """Semantic search"""
    try:
        if search_service is None:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        return search_service.search(query)
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/simple")
async def search_simple(
    query_text: str,
    top_k: int = 10,
    min_score: Optional[float] = None
):
    """Simplified search (GET parameters)"""
    try:
        if search_service is None:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        return search_service.search_simple(
            query_text=query_text,
            top_k=top_k,
            min_score=min_score
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index", response_model=IndexResponse)
async def index_document(request: IndexRequest):
    """Index document by path"""
    try:
        if indexing_service is None:
            raise HTTPException(status_code=503, detail="Indexing service not initialized")
        
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        result = indexing_service.index_document(
            file_path=request.file_path,
            overwrite=request.overwrite
        )
        
        return IndexResponse(
            success=result['success'],
            document_id=result['document_id'],
            chunks_count=result['chunks_count'],
            file_path=result['file_path'],
            message=result['message']
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Indexing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/formats")
async def get_supported_formats():
    """Get list of supported document formats"""
    return {
        "supported_extensions": sorted(list(SUPPORTED_EXTENSIONS)),
        "formats": {
            "PDF": [".pdf"],
            "Word": [".docx", ".doc"],
            "PowerPoint": [".pptx", ".ppt"],
            "Excel": [".xlsx", ".xls"],
            "Text": [".txt"],
            "Markdown": [".md"],
            "HTML": [".html", ".htm"],
            "EPUB": [".epub"],
            "Jupyter Notebooks": [".ipynb"],
            "Images": [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"]
        }
    }


@app.post("/index/upload")
async def index_uploaded_file(
    file: UploadFile = File(...),
    overwrite: bool = False
):
    """
    Index uploaded file.
    Supports all formats processed by Docling.
    """
    try:
        if indexing_service is None:
            raise HTTPException(status_code=503, detail="Indexing service not initialized")
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        if file_ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file format: {file_ext}. "
                    f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
                )
            )
        
        # Save file to temporary directory
        file_path = UPLOADS_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Index
        result = indexing_service.index_document(
            file_path=str(file_path),
            overwrite=overwrite
        )
        
        # Remove temporary file
        try:
            os.remove(file_path)
        except Exception:
            pass
        
        if not result.get('success'):
            raise HTTPException(
                status_code=422,
                detail=result.get('message', 'Failed to process document')
            )
        
        return IndexResponse(
            success=result['success'],
            document_id=result['document_id'],
            chunks_count=result['chunks_count'],
            file_path=result['file_path'],
            message=result['message']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error indexing uploaded file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index/directory")
async def index_directory(
    directory_path: str,
    overwrite: bool = False
):
    """Index all documents in directory"""
    try:
        if indexing_service is None:
            raise HTTPException(status_code=503, detail="Indexing service not initialized")
        
        if not os.path.exists(directory_path):
            raise HTTPException(status_code=404, detail=f"Directory not found: {directory_path}")
        
        results = indexing_service.index_directory(
            directory_path=directory_path,
            overwrite=overwrite
        )
        
        success_count = sum(1 for r in results if r.get('success', False))
        
        return {
            "success": True,
            "total_files": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error indexing directory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete", response_model=DeleteResponse)
async def delete_document(request: DeleteRequest):
    """Delete document from index"""
    try:
        if indexing_service is None:
            raise HTTPException(status_code=503, detail="Indexing service not initialized")
        
        result = indexing_service.delete_document(
            document_id=request.document_id,
            file_path=request.file_path
        )
        
        return DeleteResponse(
            success=result['success'],
            deleted_count=result['deleted_count'],
            message=result['message']
        )
        
    except ValueError as e:
        # Document not found
        logger.warning(f"Document not found when deleting: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Delete error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/cache/clear")
async def clear_cache():
    """Clear cache"""
    try:
        if search_service is None:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        search_service.clear_cache()
        
        return {
            "success": True,
            "message": "Cache cleared"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/db/documents")
async def get_all_documents(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    document_id: Optional[str] = None
):
    """
    Get list of all documents (chunks) from DB with metadata
    
    Args:
        limit: Maximum number of documents
        offset: Offset for pagination
        document_id: Filter by specific document_id (optional)
    """
    try:
        if chroma_manager is None:
            raise HTTPException(status_code=503, detail="ChromaDB not initialized")
        
        where_filter = None
        if document_id:
            where_filter = {'document_id': document_id}
        
        if document_id:
            # Get specific document with all chunks
            results = chroma_manager.get_documents_by_document_id(document_id)
        else:
            # Get all documents
            results = chroma_manager.get_all_documents(limit=limit, offset=offset, where=where_filter)
        
        # Format results
        documents = []
        if results.get('ids'):
            for i, chunk_id in enumerate(results['ids']):
                metadata = results['metadatas'][i] if results.get('metadatas') else {}
                text = results['documents'][i] if results.get('documents') else ''
                
                documents.append({
                    'chunk_id': chunk_id,
                    'document_id': metadata.get('document_id', ''),
                    'file_path': metadata.get('file_path', ''),
                    'file_name': metadata.get('file_name', ''),
                    'file_type': metadata.get('file_type', ''),
                    'chunk_index': metadata.get('chunk_index', 0),
                    'text_preview': text[:500] if text else '',  # First 500 characters
                    'text_length': len(text),
                    'metadata': metadata
                })
        
        return {
            "total": len(results.get('ids', [])),
            "documents": documents,
            "collection_info": chroma_manager.get_collection_info()
        }
        
    except Exception as e:
        logger.error(f"Error getting documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/db/documents/unique")
async def get_unique_documents():
    """
    Get list of unique documents (by document_id) with chunk count
    
    Returns information about each indexed document
    """
    try:
        if chroma_manager is None:
            raise HTTPException(status_code=503, detail="ChromaDB not initialized")
        
        unique_docs = chroma_manager.get_unique_documents()
        
        return {
            "total_documents": len(unique_docs),
            "documents": unique_docs
        }
        
    except Exception as e:
        logger.error(f"Error getting unique documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse")
async def parse_document_test(
    file_path: Optional[str] = None,
    file_content: Optional[UploadFile] = File(None)
):
    """
    Test document parsing WITHOUT indexing
    
    Allows to see how file will be parsed before indexing.
    Can pass either file_path or upload file via file_content.
    """
    try:
        if indexing_service is None:
            raise HTTPException(status_code=503, detail="Indexing service not initialized")
        
        from src.core.document_processor import DocumentProcessor
        from src.core.text_splitter import TextSplitter
        from src.config.settings import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_SIZE
        import tempfile
        import os
        
        processor = DocumentProcessor()
        splitter = TextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            min_chunk_size=MIN_CHUNK_SIZE
        )
        
        # Determine file path
        actual_file_path = None
        temp_file = None
        
        if file_path:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            actual_file_path = file_path
        elif file_content:
            # Save uploaded file to temporary file
            file_ext = os.path.splitext(file_content.filename)[1].lower() if file_content.filename else ""
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                shutil.copyfileobj(file_content.file, tmp)
                actual_file_path = tmp.name
                temp_file = tmp.name
        else:
            raise HTTPException(status_code=400, detail="Must specify file_path or upload file")
        
        try:
            # 1. Document parsing
            document = processor.process_document(actual_file_path)
            if not document:
                raise ValueError(f"Failed to process document: {actual_file_path}")
            
            # 2. Splitting into chunks
            chunks = splitter.split_document(document)
            
            result = {
                "success": True,
                "file_path": actual_file_path,
                "file_name": document.get('file_name', ''),
                "file_type": document.get('file_type', ''),
                "original_text_length": len(document.get('content', '')),
                "chunks_count": len(chunks),
                "chunks": [],
                "parsing_info": {
                    "has_tables": document.get('metadata', {}).get('has_tables', False),
                    "tables_count": document.get('metadata', {}).get('tables_count', 0),
                    "has_images": document.get('metadata', {}).get('has_images', False),
                    "images_count": document.get('metadata', {}).get('images_count', 0)
                }
            }
            
            # Add chunk information
            for i, chunk in enumerate(chunks):
                result["chunks"].append({
                    "chunk_index": chunk.get('chunk_index', i),
                    "text_preview": chunk.get('text', '')[:500],  # First 500 characters
                    "text_length": len(chunk.get('text', '')),
                    "start_char": chunk.get('start_char', 0),
                    "end_char": chunk.get('end_char', 0),
                    "char_count": chunk.get('char_count', 0),
                    "text_full": chunk.get('text', '')  # Full text for analysis
                })
            
            # Add original text preview
            result["original_text_preview"] = document.get('content', '')[:2000]
            result["original_text_full"] = document.get('content', '')  # Full text for analysis
            
            return result
            
        finally:
            # Remove temporary file if created
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during test parsing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

