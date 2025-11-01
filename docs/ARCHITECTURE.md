# Architecture Overview

This document describes the architecture and structure of the RAG Indexing Tool.

## Project Structure

```
rag_indexing_tool/
├── src/
│   ├── api/              # FastAPI routes and Tauri commands
│   │   ├── main.py       # Application entry point
│   │   ├── routes.py     # REST API endpoints
│   │   └── tauri_commands.py  # Tauri integration commands
│   ├── core/             # Core processing modules
│   │   ├── document_processor.py  # Docling-based document parsing
│   │   ├── text_splitter.py       # Text chunking logic
│   │   └── embeddings.py          # Embedding model wrapper
│   ├── database/          # Vector database layer
│   │   ├── chroma_manager.py      # ChromaDB operations
│   │   └── models.py              # Pydantic data models
│   ├── services/         # Business logic layer
│   │   ├── indexing_service.py   # Document indexing workflow
│   │   └── search_service.py      # Semantic search operations
│   ├── config/            # Configuration management
│   │   └── settings.py    # Settings and environment variables
│   └── utils/             # Utility modules
│       ├── logger.py      # Logging configuration
│       ├── cache.py       # LRU cache implementation
│       └── file_utils.py  # File operations
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/               # End-to-end tests
├── data/                  # Application data
│   ├── vector_db/         # ChromaDB storage (auto-created)
│   ├── uploads/           # Temporary uploads
│   └── backups/           # Database backups
├── docs/                  # Documentation
├── config.yaml            # Configuration file
└── requirements.txt       # Python dependencies
```

## Architecture Layers

### 1. API Layer (`src/api/`)

Handles HTTP requests and exposes REST endpoints:

- **routes.py**: FastAPI route definitions
- **main.py**: Application initialization and server startup
- **tauri_commands.py**: Native commands for Tauri/Rust integration

**Responsibilities**:
- Request validation
- Response formatting
- Error handling
- API documentation generation

### 2. Service Layer (`src/services/`)

Implements business logic for core operations:

- **indexing_service.py**: 
  - Orchestrates document indexing workflow
  - Manages document metadata
  - Handles batch processing
  - Error recovery

- **search_service.py**:
  - Semantic search execution
  - Query preprocessing
  - Result ranking and filtering
  - Caching layer integration

### 3. Core Layer (`src/core/`)

Contains fundamental processing modules:

- **document_processor.py**:
  - Document format detection
  - Docling integration for parsing
  - Markdown conversion
  - Format-specific handling

- **text_splitter.py**:
  - Chunk size calculation
  - Overlap management
  - Metadata preservation
  - Boundary detection

- **embeddings.py**:
  - Sentence transformer model loading
  - Embedding generation
  - Batch processing
  - Device management (CPU/GPU)

### 4. Database Layer (`src/database/`)

Manages vector database operations:

- **chroma_manager.py**:
  - Collection management
  - Document CRUD operations
  - Query execution
  - Persistence handling

- **models.py**:
  - Pydantic schemas
  - Data validation
  - Request/response models

### 5. Configuration Layer (`src/config/`)

Centralized configuration management:

- **settings.py**:
  - Environment variable loading
  - YAML config parsing
  - Default value management
  - Configuration validation

## Data Flow

### Indexing Flow

```
Document File
    ↓
[Document Processor] → Markdown
    ↓
[Text Splitter] → Chunks
    ↓
[Embedding Model] → Vectors
    ↓
[Chroma Manager] → Database
```

### Search Flow

```
Query String
    ↓
[Embedding Model] → Query Vector
    ↓
[Chroma Manager] → Similarity Search
    ↓
[Search Service] → Ranked Results
    ↓
[API Layer] → JSON Response
```

## Key Design Decisions

### 1. Unified Markdown Format

All documents are converted to Markdown before processing, ensuring:
- Consistent processing pipeline
- Simplified text splitting
- Format-agnostic chunking logic

### 2. ChromaDB for Vector Storage

Chosen for:
- Local persistence
- Low memory footprint
- Fast similarity search
- Easy integration

### 3. Sentence Transformers

Uses `all-MiniLM-L6-v2` because:
- Fast inference
- Good semantic understanding
- 384-dimensional vectors (balanced size/quality)
- No API dependencies

### 4. REST API Design

FastAPI provides:
- Automatic OpenAPI documentation
- Type validation with Pydantic
- Async support
- Easy integration with frontend/other services

## Dependencies

### Core Libraries

- **FastAPI**: Web framework
- **Docling**: Document parsing
- **ChromaDB**: Vector database
- **sentence-transformers**: Embedding generation
- **Pydantic**: Data validation

### Processing Libraries

- **numpy**: Numerical operations
- **python-multipart**: File uploads

See `requirements.txt` for complete list.

## Performance Considerations

- **Chunking**: Configurable chunk size balances context vs. retrieval precision
- **Caching**: LRU cache for frequent queries
- **Batch Processing**: Embeddings generated in batches when possible
- **Lazy Loading**: Models loaded on first use
- **Persistent Storage**: ChromaDB persists to disk, avoiding re-indexing

## Extensibility

The architecture supports extension through:

1. **New Document Formats**: Add handlers in `document_processor.py`
2. **Custom Embedding Models**: Extend `embeddings.py`
3. **Alternative Vector DBs**: Implement new manager in `database/`
4. **Additional API Endpoints**: Add routes in `routes.py`

## Security Considerations

- File type validation before processing
- Path sanitization for file operations
- Environment variable for sensitive config
- Input validation via Pydantic models
- No execution of user-provided code

---

For implementation details, refer to the source code and inline documentation.

