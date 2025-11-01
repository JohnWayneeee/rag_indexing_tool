# RAG Indexing Tool - Developer Documentation

Welcome to the RAG Indexing Tool documentation. This project provides a universal document indexing solution that converts various document formats into RAG-compatible vector embeddings for use with LLMs.

## 📚 Documentation Index

- **[Architecture](./ARCHITECTURE.md)** - Project structure and component overview
- **[API Reference](./API.md)** - REST API endpoints and usage
- **[Supported Formats](./SUPPORTED_FORMATS.md)** - Document formats and processing details
- **[Development Guide](./DEVELOPMENT.md)** - Setup, testing, and contribution guidelines

## 🎯 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create a `config.yaml` file or use environment variables:

```yaml
document_processing:
  chunk_size: 1000
  chunk_overlap: 200

embeddings:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"

database:
  path: "./data/vector_db"
  collection_name: "documents"
```

### Running the API Server

```bash
python -m src.api.main
```

The API will be available at `http://127.0.0.1:8000` with interactive documentation at `/docs`.

## 🏗️ Project Overview

This tool processes documents through the following pipeline:

1. **Document Parsing** - Uses Docling to convert various formats to Markdown
2. **Text Chunking** - Splits documents into semantic chunks (500-1000 characters)
3. **Embedding Generation** - Creates vector embeddings using sentence-transformers
4. **Vector Storage** - Stores embeddings in ChromaDB for fast retrieval
5. **Semantic Search** - Enables similarity-based document search

## 🔧 Core Components

- **Document Processor** - Handles parsing via Docling library
- **Text Splitter** - Intelligent chunking with overlap preservation
- **Embedding Model** - Sentence transformers for vector generation
- **Chroma Manager** - Vector database operations
- **REST API** - FastAPI endpoints for integration

## 📖 Key Features

- ✅ Supports 10+ document formats (PDF, Word, Excel, PowerPoint, images, etc.)
- ✅ Automatic format detection and conversion
- ✅ Semantic search with configurable similarity thresholds
- ✅ REST API for easy integration
- ✅ Persistent vector storage with ChromaDB
- ✅ Production-ready with logging and error handling

## 🚀 Use Cases

- Document knowledge bases for LLM applications
- Semantic search over document collections
- RAG pipeline preprocessing
- Document similarity analysis
- Multi-format document processing

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on contributing to this project.

## 🔗 Useful Links

- **API Documentation**: `http://localhost:8000/docs` (when server is running)
- **ReDoc**: `http://localhost:8000/redoc`

---

For detailed information about specific aspects of the project, please refer to the documentation files listed above.

