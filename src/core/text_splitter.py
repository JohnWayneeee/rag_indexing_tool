"""
Module for splitting text into chunks of 500-1000 characters
"""
import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class TextSplitter:
    """Class for smart text splitting into chunks"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 500
    ):
        """
        Args:
            chunk_size: Maximum chunk size (characters)
            chunk_overlap: Overlap between chunks (characters)
            min_chunk_size: Minimum chunk size
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # Regular expressions for splitting at sentence boundaries
        self.sentence_endings = re.compile(r'([.!?]\s+|\.\n+|\n\n+)')
    
    def split_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Split text into chunks preserving context
        
        Args:
            text: Text to split
            metadata: Metadata to add to each chunk
            
        Returns:
            List of dictionaries with chunks and metadata
        """
        if not text or not text.strip():
            logger.warning("Empty text for splitting")
            return []
        
        # Normalize text
        text = text.strip()
        
        # If text is smaller than minimum size, return as whole
        if len(text) <= self.chunk_size:
            chunk_data = {
                'text': text,
                'chunk_index': 0,
                'start_char': 0,
                'end_char': len(text),
                'char_count': len(text)
            }
            if metadata:
                chunk_data['metadata'] = metadata.copy()
            return [chunk_data]
        
        chunks = []
        current_pos = 0
        chunk_index = 0
        
        while current_pos < len(text):
            # Determine end of current chunk
            end_pos = min(current_pos + self.chunk_size, len(text))
            
            # If not end of text, search for sentence boundary
            if end_pos < len(text):
                # Search for nearest sentence boundary in last 20% of chunk
                search_start = max(current_pos, end_pos - int(self.chunk_size * 0.2))
                text_slice = text[search_start:end_pos]
                
                matches = list(self.sentence_endings.finditer(text_slice))
                if matches:
                    # Take last found boundary
                    last_match = matches[-1]
                    # Adjust position accounting for search start
                    actual_end = search_start + last_match.end()
                    end_pos = actual_end
            
            # Extract chunk
            chunk_text = text[current_pos:end_pos].strip()
            
            # Skip too small chunks (except first and last)
            if len(chunk_text) >= self.min_chunk_size or chunk_index == 0:
                chunk_data = {
                    'text': chunk_text,
                    'chunk_index': chunk_index,
                    'start_char': current_pos,
                    'end_char': end_pos,
                    'char_count': len(chunk_text)
                }
                
                # Add metadata
                if metadata:
                    chunk_data['metadata'] = metadata.copy()
                    chunk_data['metadata']['chunk_index'] = chunk_index
                
                chunks.append(chunk_data)
                chunk_index += 1
            
            # Move accounting for overlap
            current_pos = max(current_pos + 1, end_pos - self.chunk_overlap)
            
            # Protection from infinite loop
            if current_pos >= end_pos:
                current_pos = end_pos
        
        logger.info(f"Split text into {len(chunks)} chunks (size: {self.chunk_size}, overlap: {self.chunk_overlap})")
        return chunks
    
    def split_document(self, document: Dict) -> List[Dict]:
        """
        Split document into chunks
        
        Args:
            document: Dictionary with document (must contain 'full_text' and metadata)
            
        Returns:
            List of chunks with metadata
        """
        if 'full_text' not in document:
            logger.error("Document does not contain 'full_text'")
            return []
        
        # Prepare metadata for chunks
        metadata = {
            'file_path': document.get('file_path', ''),
            'file_name': document.get('file_name', ''),
            'file_type': document.get('file_type', ''),
            'document_metadata': document.get('metadata', {})
        }
        
        # Add information about tables and images to metadata
        if document.get('tables'):
            metadata['has_tables'] = True
            metadata['tables_count'] = len(document['tables'])
        
        if document.get('images'):
            metadata['has_images'] = True
            metadata['images_count'] = len(document['images'])
        
        return self.split_text(document['full_text'], metadata)

