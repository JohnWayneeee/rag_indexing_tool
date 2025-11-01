# Contributing to RAG Indexing Tool

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

1. Check if the bug already exists in issues
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create an issue describing:
   - Use case
   - Expected behavior
   - Potential implementation approach (if you have ideas)

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes**
4. **Write tests** for new functionality
5. **Run tests**: `pytest`
6. **Update documentation** if needed
7. **Commit changes**: Follow commit message guidelines
8. **Push to your fork**: `git push origin feature/your-feature`
9. **Create a Pull Request**

## Code Standards

### Python Style

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Maximum line length: 88 characters (Black default)
- Use meaningful variable and function names

### Code Example

```python
from typing import List, Optional

def process_document(
    file_path: str,
    chunk_size: int = 1000,
    overlap: Optional[int] = None
) -> List[str]:
    """
    Process a document and return chunks.
    
    Args:
        file_path: Path to the document file
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    # Implementation here
    pass
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update relevant `.md` files for user-facing changes
- Keep code examples in documentation up-to-date

### Testing

- Write tests for all new features
- Aim for >80% code coverage
- Include both positive and negative test cases
- Test edge cases and error conditions

## Commit Message Guidelines

Use clear, descriptive commit messages:

**Format:**
```
<type>: <subject>

<body>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add support for CSV file format

Add CSV parsing support using pandas. Includes validation
and error handling for malformed files.

Fixes #123
```

```
fix: Resolve memory leak in embedding cache

Clear cache entries after processing to prevent memory
accumulation during batch operations.
```

## Pull Request Process

### Before Submitting

1. **Run all tests**: `pytest`
2. **Check code coverage**: `pytest --cov=src --cov-report=term-missing`
3. **Test your changes**: Manually test new features
4. **Update documentation**: If API or behavior changes
5. **Check for linting errors**: `ruff check src/` (if configured)

### PR Description

Include:
- Description of changes
- Related issues (if any)
- Testing performed
- Screenshots (for UI changes)
- Breaking changes (if any)

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, PR will be merged

## Development Setup

See [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed setup instructions.

## Areas for Contribution

We welcome contributions in:

- **New document format support**: Add parsers for additional formats
- **Performance improvements**: Optimize indexing and search
- **API enhancements**: New endpoints or features
- **Documentation**: Improve docs, add examples
- **Testing**: Increase test coverage
- **Bug fixes**: Fix reported issues
- **Code quality**: Refactoring and improvements

## Questions?

- Open an issue for questions or discussions
- Check existing documentation first
- Review closed issues/PRs for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🙏

