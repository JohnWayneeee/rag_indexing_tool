# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-2

### Added
- Initial release of RAG Indexing Tool
- Support for multiple document formats (PDF, Word, PowerPoint, Excel, HTML, EPUB, Jupyter Notebooks, images)
- Document parsing via Docling library
- Smart text chunking with configurable overlap
- Vector embeddings using sentence-transformers (all-MiniLM-L6-v2)
- ChromaDB integration for vector storage
- FastAPI REST API with Swagger/ReDoc documentation
- Semantic search functionality
- File upload and directory indexing endpoints
- Tauri integration support
- Comprehensive test suite (unit, integration, E2E)
- Configuration via YAML and environment variables
- Logging system with multiple log files

### Features
- **Document Processing**: Converts documents to Markdown via Docling
- **Smart Chunking**: Splits text into logical blocks (500-1000 characters)
- **Vectorization**: Creates 384-dimensional embeddings
- **Storage**: ChromaDB in persistent mode
- **Semantic Search**: Vector-based search (50-200 ms per query)
- **REST API**: FastAPI endpoints for easy integration

### Technical Details
- Python 3.10+ support
- FastAPI 0.104+ for API layer
- Pydantic 2.0+ for data validation
- ChromaDB 0.4.0+ for vector storage
- Sentence-transformers for embeddings

[1.0.0]: https://github.com/JohnWayneeee/rag-indexing-tool/releases/tag/v1.0.0
