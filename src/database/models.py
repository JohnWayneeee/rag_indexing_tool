"""
Pydantic models for documents and requests
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentMetadata(BaseModel):
    """Document metadata"""
    file_path: str
    file_name: str
    file_type: str
    file_size: Optional[int] = None
    creation_time: Optional[float] = None
    modification_time: Optional[float] = None
    chunk_index: Optional[int] = None
    document_id: Optional[str] = None
    has_tables: Optional[bool] = None
    tables_count: Optional[int] = None
    has_images: Optional[bool] = None
    images_count: Optional[int] = None


class Chunk(BaseModel):
    """Document chunk model"""
    text: str
    chunk_index: int
    start_char: int
    end_char: int
    char_count: int
    metadata: Optional[DocumentMetadata] = None
    embedding: Optional[List[float]] = None


class Document(BaseModel):
    """Document model"""
    file_path: str
    file_name: str
    file_type: str
    full_text: str
    chunks: List[Chunk] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    indexed_at: Optional[datetime] = None
    document_id: Optional[str] = None


class SearchQuery(BaseModel):
    """Search query model"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results")
    min_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum score")
    filter_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filter")


class SearchResult(BaseModel):
    """Search result model"""
    text: str
    score: float
    chunk_index: int
    metadata: DocumentMetadata
    document_id: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response model"""
    results: List[SearchResult]
    query: str
    total_results: int
    search_time_ms: float


class IndexRequest(BaseModel):
    """Indexing request model"""
    file_path: str = Field(..., description="Path to file for indexing")
    overwrite: bool = Field(default=False, description="Overwrite existing document")


class IndexResponse(BaseModel):
    """Indexing response model"""
    success: bool
    document_id: str
    chunks_count: int
    file_path: str
    message: str


class DeleteRequest(BaseModel):
    """Deletion request model"""
    document_id: Optional[str] = None
    file_path: Optional[str] = None


class DeleteResponse(BaseModel):
    """Deletion response model"""
    success: bool
    deleted_count: int
    message: str


class StatusResponse(BaseModel):
    """System status response model"""
    status: str
    total_documents: int
    total_chunks: int
    database_path: str
    collection_name: str
    embedding_model: str
    embedding_dim: int

