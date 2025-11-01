# API Reference

Complete REST API documentation for RAG Indexing Tool.

**Base URL**: `http://localhost:8000`  
**Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)  
**Alternative Documentation**: `http://localhost:8000/redoc` (ReDoc)

## Endpoints Overview

### Health & Status

- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - System status

### Indexing

- `POST /index` - Index document by file path
- `POST /index/upload` - Upload and index file
- `POST /index/directory` - Index all documents in directory

### Search

- `POST /search` - Semantic search
- `POST /search/simple` - Simplified search endpoint

### Management

- `GET /formats` - Get supported document formats
- `GET /db/documents` - List all documents in database
- `GET /db/documents/unique` - Get unique documents
- `DELETE /delete` - Delete document from index
- `DELETE /cache/clear` - Clear search cache

### Utilities

- `POST /parse` - Parse document without indexing

---

## Health & Status Endpoints

### GET `/`

Get API information.

**Response:**
```json
{
  "message": "RAG Indexing Tool API",
  "version": "1.0.0",
  "status": "running"
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "documents_count": 42
  }
}
```

### GET `/status`

Get detailed system status.

**Response:**
```json
{
  "status": "running",
  "total_documents": 42,
  "total_chunks": 156,
  "database_path": "./data/vector_db",
  "collection_name": "documents",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "embedding_dim": 384
}
```

---

## Indexing Endpoints

### POST `/index`

Index a document by file path.

**Request Body:**
```json
{
  "file_path": "./data/raw/document.pdf",
  "overwrite": false
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "uuid-here",
  "chunks_count": 15,
  "file_path": "./data/raw/document.pdf",
  "message": "Document indexed successfully"
}
```

### POST `/index/upload`

Upload and index a file.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (file, required): Document file to upload
- `overwrite` (boolean, query param, default: false): Overwrite if exists

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/index/upload?overwrite=false" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "success": true,
  "document_id": "uuid-here",
  "chunks_count": 15,
  "file_path": "document.pdf",
  "message": "Document indexed successfully"
}
```

### POST `/index/directory`

Index all supported documents in a directory.

**Parameters:**
- `directory_path` (string, query param, required): Path to directory
- `overwrite` (boolean, query param, default: false): Overwrite existing documents

**Example:**
```bash
curl -X POST "http://localhost:8000/index/directory?directory_path=./data/raw&overwrite=false"
```

**Response:**
```json
{
  "success": true,
  "indexed_count": 5,
  "failed_count": 0,
  "total_files": 5,
  "results": [
    {
      "file_path": "./data/raw/doc1.pdf",
      "success": true,
      "chunks_count": 10
    }
  ]
}
```

---

## Search Endpoints

### POST `/search`

Semantic search with full control.

**Request Body:**
```json
{
  "query": "your search query",
  "top_k": 10,
  "min_score": 0.7
}
```

**Response:**
```json
{
  "query": "your search query",
  "results": [
    {
      "id": "chunk-id",
      "text": "Relevant document chunk text...",
      "score": 0.85,
      "metadata": {
        "document_id": "doc-uuid",
        "file_path": "./data/raw/document.pdf",
        "chunk_index": 0
      }
    }
  ],
  "total_results": 10,
  "search_time_ms": 45
}
```

### POST `/search/simple`

Simplified search endpoint.

**Parameters:**
- `query_text` (string, query param, required): Search query
- `top_k` (integer, query param, default: 10): Number of results
- `min_score` (float, query param, optional): Minimum similarity score

**Example:**
```bash
curl -X POST "http://localhost:8000/search/simple?query_text=example&top_k=5"
```

---

## Management Endpoints

### GET `/formats`

Get list of supported document formats.

**Response:**
```json
{
  "supported_extensions": [".pdf", ".docx", ".doc", ...],
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
```

### GET `/db/documents`

List all documents in the database.

**Response:**
```json
{
  "total_documents": 42,
  "documents": [
    {
      "document_id": "uuid",
      "file_path": "./data/raw/document.pdf",
      "chunks_count": 15,
      "metadata": {}
    }
  ]
}
```

### GET `/db/documents/unique`

Get unique documents (one entry per file).

**Response:**
```json
{
  "total_unique": 10,
  "documents": [
    {
      "file_path": "./data/raw/document.pdf",
      "chunks_count": 15,
      "document_ids": ["uuid1", "uuid2"]
    }
  ]
}
```

### DELETE `/delete`

Delete a document from the index.

**Request Body:**
```json
{
  "document_id": "uuid-here"
}
```

or

```json
{
  "file_path": "./data/raw/document.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully",
  "deleted_count": 15
}
```

### DELETE `/cache/clear`

Clear the search cache.

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared successfully"
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service not initialized

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

---

## Authentication

Currently, the API does not require authentication. For production use, implement:
- API key authentication
- OAuth2
- JWT tokens

---

## Rate Limiting

No rate limiting is currently implemented. For production, consider:
- Request throttling per IP
- Per-user rate limits
- Endpoint-specific limits

---

## CORS

CORS is enabled for all origins (`*`). In production, restrict to specific domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

---

For interactive testing, use the Swagger UI at `/docs` or ReDoc at `/redoc`.

## Testing

The project includes comprehensive test coverage using pytest:

- **Unit tests**: `tests/unit/` - Test individual components
- **Integration tests**: `tests/integration/` - Test API endpoints
- **E2E tests**: `tests/e2e/` - Test complete workflows

Run tests with:
```bash
pytest
```

See [DEVELOPMENT.md](./DEVELOPMENT.md) for more testing details.

