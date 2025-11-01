"""
Module for creating vector representations of text using all-MiniLM-L6-v2
"""
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Class for working with all-MiniLM-L6-v2 model"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = "cpu"):
        """
        Args:
            model_name: Sentence Transformers model name
            device: Device for computation ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Sentence Transformers model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading model {self.model_name} on device {self.device}...")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.get_embedding_dim()}")
        except ImportError:
            logger.error("sentence-transformers not installed. Install: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def get_embedding_dim(self) -> int:
        """Returns embedding dimension"""
        if self.model is None:
            return 384  # Default dimension for all-MiniLM-L6-v2
        
        # Get dimension by creating a test embedding
        test_embedding = self.model.encode(["test"], show_progress_bar=False)
        return len(test_embedding[0])
    
    def encode(self, texts: List[str], batch_size: int = 32, normalize: bool = True) -> np.ndarray:
        """
        Create vector representations for a list of texts
        
        Args:
            texts: List of texts to vectorize
            batch_size: Batch size for processing
            normalize: Normalize vectors (for cosine similarity)
            
        Returns:
            NumPy array of embeddings with shape (n_texts, embedding_dim)
        """
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        if not texts:
            logger.warning("Empty list of texts for vectorization")
            return np.array([])
        
        try:
            # Encode texts
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=normalize,
                convert_to_numpy=True
            )
            
            # Check type and shape of embeddings
            if isinstance(embeddings, tuple):
                embeddings = embeddings[0]  # Take first element if tuple
            
            if hasattr(embeddings, 'shape') and len(embeddings.shape) >= 2:
                logger.debug(f"Created {len(embeddings)} embeddings with dimension {embeddings.shape[1]}")
            else:
                logger.debug(f"Created {len(embeddings)} embeddings")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Create vector representation for a single text
        
        Args:
            text: Text to vectorize
            normalize: Normalize vector
            
        Returns:
            NumPy array of embedding (1D)
        """
        return self.encode([text], normalize=normalize)[0]
    
    def encode_chunks(self, chunks: List[dict], batch_size: int = 32) -> List[dict]:
        """
        Vectorize list of chunks, adding embeddings to each chunk
        
        Args:
            chunks: List of dictionaries with chunks (must contain 'text')
            batch_size: Batch size
            
        Returns:
            List of chunks with added 'embedding' field
        """
        if not chunks:
            return []
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Create embeddings
        embeddings = self.encode(texts, batch_size=batch_size)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i].tolist()  # Convert to list for JSON
        
        logger.info(f"Vectorized {len(chunks)} chunks")
        return chunks

