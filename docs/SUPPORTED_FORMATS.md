# Supported Document Formats

The system uses the **Docling** library for document processing. Docling automatically detects document types and converts them to a unified Markdown format for subsequent indexing.

## 📄 Complete List of Supported Formats

### Office Documents

- **PDF** (.pdf)
  - Text content and tables
  - OCR support for scanned documents
  - Page structure preservation
  - ⚠️ **Limitation**: Password-protected PDFs are not supported

- **Microsoft Word** (.docx, .doc)
  - Text, tables, images
  - Formatting preservation

- **Microsoft PowerPoint** (.pptx, .ppt)
  - Slide text
  - Slide notes
  - Images

- **Microsoft Excel** (.xlsx, .xls)
  - Data tables
  - Formulas (converted to values)
  - Multiple sheets

### Text Formats

- **Plain Text** (.txt)
  - Simple text without formatting

- **Markdown** (.md)
  - Markdown structure preservation
  - Code blocks
  - Links and images

- **HTML** (.html, .htm)
  - Text content extraction
  - Document structure parsing

### E-books

- **EPUB** (.epub)
  - Chapter text
  - Book metadata

### Jupyter Notebooks

- **Jupyter Notebooks** (.ipynb)
  - Code cells (markdown portions)
  - Execution results (text)

### Images

- **Raster Images** (.png, .jpg, .jpeg, .bmp, .tiff, .gif, .webp)
  - OCR for text extraction from images
  - Support for various formats

## 🔧 Technical Details

### Document Processing

All documents are processed through the unified Docling mechanism:

1. **Automatic type detection**: Docling independently determines file format
2. **Markdown conversion**: All formats are converted to unified Markdown format
3. **Structure extraction**: Document structure is preserved (tables, images, headers)

### API Endpoint

To get the current list of supported formats:

```bash
GET /formats
```

**Response:**
```json
{
  "supported_extensions": [".pdf", ".docx", ".doc", ...],
  "formats": {
    "PDF": [".pdf"],
    "Word": [".docx", ".doc"],
    ...
  }
}
```

### Validation

#### Backend Validation

Backend validates file extension before processing:

- ✅ Files with supported extensions are processed automatically
- ❌ Files with unsupported extensions return 400 error with description

**Error example:**
```json
{
  "detail": "Unsupported file format: .zip. Supported formats: .pdf, .docx, ..."
}
```

#### Frontend Validation

Client-side UI validation is for UX improvement:
- File filtering in file selection dialog
- Validation before server submission
- Informative error messages

**Important**: Frontend validation is not a security boundary - backend always performs final validation.

## 📊 Usage Examples

### Upload PDF

```bash
curl -X POST "http://localhost:8000/index/upload?overwrite=false" \
  -F "file=@document.pdf"
```

### Upload Word Document

```bash
curl -X POST "http://localhost:8000/index/upload?overwrite=false" \
  -F "file=@report.docx"
```

### Upload Image

```bash
curl -X POST "http://localhost:8000/index/upload?overwrite=false" \
  -F "file=@scanned_page.png"
```

### Index by Path

```json
POST /index
{
  "file_path": "./data/raw/presentation.pptx",
  "overwrite": false
}
```

## ⚠️ Limitations

### Unsupported Formats

- **Archives**: .zip, .rar, .7z (not automatically extracted)
- **Databases**: .db, .sqlite (text not extracted)
- **Executables**: .exe, .dll (not processed)
- **Video/Audio**: .mp4, .mp3, .wav (require special processing)

### Processing Limitations

1. **Password-protected PDFs**: Files with passwords are not processed
2. **Very large files**: May require more time and memory
3. **Corrupted files**: May not be processed correctly

## 🔄 Automatic Updates

The system is designed for automatic support of new formats:

- **Docling automatically determines supported formats** - no need to specify `allowed_formats`
- When Docling is updated, new formats become available automatically
- The `SUPPORTED_EXTENSIONS` list is used only for validation and can be manually extended

## 📝 Configuration

The list of supported formats can be configured in `config.yaml`:

```yaml
document_processing:
  supported_formats: [
    ".pdf", ".docx", ".doc",
    ".pptx", ".ppt", ".xlsx", ".xls",
    ".txt", ".md", ".html", ".htm",
    ".epub", ".ipynb",
    ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"
  ]
```

**Note**: Configuration is used for validation. Actual processing is performed through Docling, which may support additional formats.
