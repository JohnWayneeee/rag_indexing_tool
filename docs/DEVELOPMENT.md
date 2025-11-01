# Development Guide

This guide covers setup, development workflow, and testing procedures for the RAG Indexing Tool.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for development)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag_indexing_tool
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

For development, install additional tools:

```bash
pip install pytest pytest-cov pytest-xdist
```

### 3. Install in Development Mode

```bash
pip install -e .
```

### 4. Configure Environment

Copy environment variables or create `config.yaml`:

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

Or use environment variables:

```bash
export CHROMA_DB_PATH="./data/vector_db"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export EMBEDDING_DEVICE="cpu"
```

## Development Workflow

### Running the API Server

**Development mode (with auto-reload):**
```bash
python -m src.api.main
```

**Production mode:**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Running Tests

**All tests:**
```bash
pytest
```

**With coverage:**
```bash
pytest --cov=src --cov-report=html
```

Open `htmlcov/index.html` to view coverage report.

**Specific test types:**
```bash
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/           # End-to-end tests only
```

**With markers:**
```bash
pytest -m unit              # Tests marked with @pytest.mark.unit
pytest -m "not slow"        # Exclude slow tests
```

### Code Quality

**Linting** (if configured):
```bash
ruff check src/
```

**Formatting** (if configured):
```bash
black src/
```

## Project Structure

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed structure.

Key directories:
- `src/` - Source code
- `tests/` - Test suite
- `docs/` - Documentation
- `data/` - Application data (not in git)

## Adding New Features

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Write Code

Follow existing patterns:
- Use type hints
- Add docstrings
- Follow PEP 8 style guide

### 3. Write Tests

Add tests in appropriate test directory:
- `tests/unit/` - Unit tests for modules
- `tests/integration/` - API integration tests
- `tests/e2e/` - End-to-end workflow tests

### 4. Update Documentation

- Update relevant `.md` files
- Add docstrings to new functions/classes
- Update API docs if adding endpoints

### 5. Run Tests

```bash
pytest
```

Ensure all tests pass before committing.

### 6. Commit and Push

```bash
git add .
git commit -m "Add feature: description"
git push origin feature/your-feature-name
```

## Testing Guidelines

### Unit Tests

Test individual functions and classes in isolation:

```python
def test_text_splitter():
    splitter = TextSplitter(chunk_size=100, chunk_overlap=20)
    chunks = splitter.split("long text here...")
    assert len(chunks) > 0
```

### Integration Tests

Test API endpoints with test client:

```python
def test_search_endpoint(client):
    response = client.post("/search", json={
        "query": "test",
        "top_k": 10
    })
    assert response.status_code == 200
```

### E2E Tests

Test complete workflows:

```python
def test_index_and_search_workflow():
    # Index document
    result = index_document("test.pdf")
    assert result["success"]
    
    # Search
    results = search("test query")
    assert len(results) > 0
```

Tests are organized in `tests/` directory with unit, integration, and e2e test suites. Run `pytest` to execute all tests.

## Debugging

### Enable Debug Logging

Set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

Or modify `src/utils/logger.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Using Debugger

Add breakpoints in code:
```python
import pdb; pdb.set_trace()
```

Or use IDE debugger with FastAPI:
```bash
python -m debugpy --listen 5678 -m uvicorn src.api.main:app --reload
```

## Performance Profiling

### Profile API Endpoints

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10
```

### Memory Profiling

```bash
pip install memory-profiler
python -m memory_profiler your_script.py
```

## Common Issues

### Import Errors

If you get import errors, ensure you're running from project root:
```bash
python -m src.api.main  # ✅ Correct
python src/api/main.py   # ❌ May fail
```

### ChromaDB Lock Errors

If ChromaDB is locked, ensure only one instance is running:
```bash
# Kill existing processes
pkill -f "python.*api.main"
```

### Model Loading Issues

If embedding model fails to load:
- Check internet connection (first download)
- Verify model name in config
- Check disk space

## Documentation

### Generating API Docs

API documentation is auto-generated by FastAPI:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Updating Docs

1. Update relevant `.md` files in `docs/`
2. Ensure code examples are correct
3. Test all examples in documentation

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.

## Getting Help

- Check existing documentation
- Review test examples
- Check FastAPI docs: https://fastapi.tiangolo.com
- Check ChromaDB docs: https://docs.trychroma.com
- Check Docling docs: https://docling-project.github.io/docling/

---

Happy coding! 🚀

