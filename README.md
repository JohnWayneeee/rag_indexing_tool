# RAG Indexing Tool

Universal utility for indexing documents of various formats into a vector database with semantic search support. Converts documents to RAG-compatible format for use with LLMs.

## 🎯 Key Features

- **Document Parsing**: Converts documents to Markdown via Docling
  - Supports 10+ formats: PDF, Word, PowerPoint, Excel, HTML, EPUB, Jupyter Notebooks, images, and more
  - Automatic document type detection
  - Consistent Markdown output for all formats
- **Smart Chunking**: Splits text into logical blocks of 500-1000 characters
- **Vectorization**: all-MiniLM-L6-v2 model for creating embeddings (384-dimensional vectors)
- **Storage**: ChromaDB in persistent mode
- **Semantic Search**: Vector-based search (50-200 ms per query)
- **REST API**: FastAPI endpoints for integration with Tauri/Rust

## 📦 Installation

1. Clone the repository or navigate to the project directory

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install the package in development mode:
```bash
pip install -e .
```

4. Configure settings in `config.yaml` (optional)

## ⚙️ Configuration

Main settings in `config.yaml`:

```yaml
document_processing:
  chunk_size: 1000        # Chunk size
  chunk_overlap: 200      # Overlap between chunks

embeddings:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"           # or "cuda"

database:
  path: "./data/vector_db"
  collection_name: "documents"
```

Alternatively, configure via environment variables:
- `CHROMA_DB_PATH` - path to vector database
- `EMBEDDING_MODEL` - embedding model
- `EMBEDDING_DEVICE` - device (cpu/cuda)
- `CHUNK_SIZE` - chunk size
- `API_HOST` - API host (default: 127.0.0.1)
- `API_PORT` - API port (default: 8000)

## 🚀 Usage

### Starting the API Server

**Recommended method:**
```bash
python -m src.api.main
```

**Alternative method via uvicorn:**
```bash
# From project root
uvicorn src.api.routes:app --host 127.0.0.1 --port 8000 --reload
```

**Note:** All modules use absolute imports with `src.` prefix, so when running from project root, Python automatically finds modules.

### Using CLI (legacy method)

```bash
python src/main.py
```

## 📡 API Endpoints

**📚 Swagger UI available at:** `http://127.0.0.1:8000/docs`  
**📖 ReDoc available at:** `http://127.0.0.1:8000/redoc`

FastAPI automatically generates interactive API documentation with all endpoints, data models, and request examples.

### GET `/`
Service information

### GET `/health`
Health check

### GET `/status`
Get system status

### POST `/search`
Semantic search:
```json
{
  "query": "search query",
  "top_k": 10,
  "min_score": 0.7
}
```

### POST `/index`
Index document by path:
```json
{
  "file_path": "./data/raw/document.xlsx",
  "overwrite": false
}
```

### GET `/formats`
Get list of supported document formats

### POST `/index/upload`
Upload and index file (multipart/form-data)

**Supported formats:**
- **PDF** (.pdf)
- **Word** (.docx, .doc)
- **PowerPoint** (.pptx, .ppt)
- **Excel** (.xlsx, .xls)
- **Text** (.txt)
- **Markdown** (.md)
- **HTML** (.html, .htm)
- **EPUB** (.epub)
- **Jupyter Notebooks** (.ipynb)
- **Images** (.png, .jpg, .jpeg, .bmp, .tiff, .gif, .webp)

### POST `/index/directory`
Index all documents in a directory:
```
POST /index/directory?directory_path=./data/raw&overwrite=false
```

### DELETE `/delete`
Delete document from index:
```json
{
  "document_id": "uuid",
  "file_path": "./path/to/file"
}
```

## 🔌 Tauri Integration

Use functions from `src/api/tauri_commands.py`:

```python
from src.api.tauri_commands import (
    tauri_index_document,
    tauri_search,
    tauri_delete_document,
    tauri_get_status
)

# Indexing
result = tauri_index_document("path/to/file.xlsx")

# Search
results = tauri_search("semantic search query", top_k=10)

# Status
status = tauri_get_status()
```

In Rust Tauri code, register commands:
```rust
tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![
        index_document,
        search,
        delete_document,
        get_status
    ])
```

## 📁 Project Structure

```
rag_indexing_tool/
├── src/
│   ├── api/              # FastAPI routes and Tauri commands
│   ├── core/             # Parsing, chunking, embeddings
│   ├── database/         # ChromaDB manager and models
│   ├── services/         # Business logic (indexing, search)
│   ├── config/          # Settings
│   └── utils/           # Utilities (cache, logging)
├── data/
│   ├── vector_db/       # ChromaDB storage
│   ├── raw/            # Source documents
│   └── processed/      # Processed data
├── docs/                # Documentation
└── config.yaml          # Configuration
```

## 🧪 Performance

- **Indexing**: Peak load only when adding files
- **Search**: 50-200 ms per query (with caching)
- **Memory**: ~300-500 MB in operation mode
- **Storage**: ~10-100 MB per 1000 documents

## 📝 Logging

Logs are saved in `logs/`:
- `app.log` - general log
- `indexing.log` - indexing operations
- `search.log` - search operations
- `errors.log` - errors

## 🔧 Development

To run in development mode:
```bash
export API_RELOAD=true  # Linux/Mac
# or
set API_RELOAD=true     # Windows CMD
# or
$env:API_RELOAD="true"  # PowerShell
python -m src.api.main
```

## 🧪 Testing

The project includes comprehensive test coverage using pytest:

- **Unit tests**: `tests/unit/` - Test individual components
- **Integration tests**: `tests/integration/` - Test API endpoints
- **E2E tests**: `tests/e2e/` - Test complete workflows

Run tests with:
```bash
pytest
```

## 📚 Documentation

For detailed documentation, see the [docs/](./docs/) directory:
- [Architecture](./docs/ARCHITECTURE.md) - Project structure
- [API Reference](./docs/API.md) - Complete API documentation
- [Supported Formats](./docs/SUPPORTED_FORMATS.md) - Document formats
- [Development Guide](./docs/DEVELOPMENT.md) - Development setup
- [Contributing](./docs/CONTRIBUTING.md) - Contribution guidelines

## 📄 License

MIT
