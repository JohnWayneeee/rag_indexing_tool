import os
import logging
from typing import List, Dict, Optional, Set

logger = logging.getLogger(__name__)

# Full list of supported Docling extensions
SUPPORTED_EXTENSIONS: Set[str] = {
    # PDF
    '.pdf',
    # Word
    '.docx', '.doc',
    # PowerPoint
    '.pptx', '.ppt',
    # Excel
    '.xlsx', '.xls',
    # Text
    '.txt',
    # Markdown
    '.md',
    # HTML
    '.html', '.htm',
    # EPUB
    '.epub',
    # Jupyter Notebooks
    '.ipynb',
    # Images
    '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif', '.webp',
}


class DocumentProcessor:
    def __init__(self):
        """
        Initialize document processor.
        Uses universal Docling approach - without allowed_formats restriction,
        so Docling determines supported formats itself.
        """
        try:
            from docling.document_converter import DocumentConverter

            # Don't specify allowed_formats - Docling will determine supported formats itself
            # This allows automatic support for new formats when Docling is updated
            self.converter = DocumentConverter()
            self.converter_available = True
            logger.info("Docling DocumentConverter initialized successfully")
        except ImportError as e:
            logger.error(f"Docling not installed: {e}")
            self.converter_available = False

    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in SUPPORTED_EXTENSIONS

    def process_document(self, file_path: str) -> Optional[Dict]:
        """
        Process one document and return structured data.
        
        Args:
            file_path: Path to file for processing
            
        Returns:
            Dictionary with processed data or None on error
        """
        if not self.converter_available:
            logger.error("Docling not available")
            return None

        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None

            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Format check (warning, but don't block - Docling may support more)
            if file_ext not in SUPPORTED_EXTENSIONS:
                logger.warning(
                    f"Extension {file_ext} not in list of known supported formats. "
                    f"Attempting processing via Docling..."
                )

            # Document conversion via Docling
            result = self.converter.convert(file_path)
            
            # Check conversion status
            if hasattr(result, 'status') and result.status.name != 'SUCCESS':
                error_msg = f"Docling failed to process file: {file_path} (status: {result.status})"
                logger.error(error_msg)
                return None

            # Basic information
            stats = os.stat(file_path)

            # Extract main text in Markdown
            full_text = result.document.export_to_markdown()

            content = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_type': file_ext,
                'full_text': full_text,
                'tables': self._extract_tables_safe(result),
                'images': self._extract_images_safe(result, file_path),
                'metadata': {
                    'file_size': stats.st_size,
                    'creation_time': stats.st_ctime,
                    'modification_time': stats.st_mtime,
                }
            }

            logger.info(f"Successfully processed: {file_path} (type: {file_ext})")
            return content

        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def _extract_tables_safe(self, result) -> List[Dict]:
        """Safe table extraction"""
        tables = []

        try:
            # Check for tables
            if hasattr(result.document, 'tables') and result.document.tables:
                for i, table in enumerate(result.document.tables):
                    table_info = {
                        'table_index': i,
                        'caption': getattr(table, 'caption', f'Table {i + 1}'),
                        'content': str(table)  # Basic string representation
                    }

                    # Try to get more table information
                    try:
                        if hasattr(table, 'to_markdown'):
                            table_info['markdown'] = table.to_markdown()
                        elif hasattr(table, 'content'):
                            table_info['content'] = str(table.content)
                    except Exception as e:
                        logger.warning(f"Failed to process table {i} in detail: {e}")

                    tables.append(table_info)
        except Exception as e:
            logger.warning(f"Error extracting tables: {e}")

        return tables

    def _extract_images_safe(self, result, file_path: str) -> List[Dict]:
        """Safe image information extraction"""
        images = []

        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            # If it's an image itself (PNG, JPG, etc.)
            if file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                images.append({
                    'image_index': 0,
                    'caption': f"Image: {os.path.basename(file_path)}",
                    'file_path': file_path,
                    'file_size': os.path.getsize(file_path),
                    'type': 'standalone_image',
                    'text_content': result.document.export_to_markdown() if hasattr(result.document,
                                                                                    'export_to_markdown') else ""
                })
            else:
                # For documents (PDF, DOCX, etc.) search for embedded images
                if hasattr(result.document, 'images') and result.document.images:
                    for i, img in enumerate(result.document.images):
                        image_info = {
                            'image_index': i,
                            'caption': getattr(img, 'caption', f'Image {i + 1}')
                        }

                        # Add available attributes
                        for attr in ['size', 'mode', 'format']:
                            if hasattr(img, attr):
                                image_info[attr] = getattr(img, attr)

                        images.append(image_info)

        except Exception as e:
            logger.warning(f"Error extracting images: {e}")

        return images

    def process_directory(self, directory_path: str) -> List[Dict]:
        """
        Process all documents in directory.
        
        Args:
            directory_path: Path to directory for processing
            
        Returns:
            List of processed documents
        """
        if not self.converter_available:
            logger.error("Docling not available")
            return []

        processed_docs = []
        skipped_count = 0

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                
                # Use general list of supported formats
                if file_ext in SUPPORTED_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    logger.info(f"Processing file: {file_path} (type: {file_ext})")
                    result = self.process_document(file_path)
                    if result:
                        processed_docs.append(result)
                    else:
                        skipped_count += 1
                else:
                    skipped_count += 1
                    logger.debug(f"Skipped file with unsupported extension: {file} ({file_ext})")

        logger.info(
            f"Directory processing completed: processed {len(processed_docs)}, "
            f"skipped {skipped_count}"
        )
        return processed_docs