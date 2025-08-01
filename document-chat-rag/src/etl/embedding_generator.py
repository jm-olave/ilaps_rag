"""
Embedding Generator Module

This module generates embeddings for document chunks using a transformer model
and prepares them for storage in the vector database.
"""

import os
import logging
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np

from src.utils.logging import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)

class EmbeddingGenerator:
    """Generates embeddings for document chunks."""
    
    def __init__(self, config_path: str = "config/processing.yaml"):
        """
        Initialize the EmbeddingGenerator with configuration.
        
        Args:
            config_path: Path to the processing configuration file
        """
        self.config = get_config(config_path)
        self.embedding_config = self.config.get('embedding', {})
        
        # Load the embedding model
        model_name = self.embedding_config.get('model', 'sentence-transformers/all-MiniLM-L6-v2')
        self.model = SentenceTransformer(model_name)
        
        logger.info(f"EmbeddingGenerator initialized with model: {model_name}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks.
        
        Args:
            texts: List of text chunks to embed
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} text chunks")
            
            # Generate embeddings in batches
            batch_size = self.embedding_config.get('batch_size', 32)
            embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                batch_embeddings = self.model.encode(batch)
                embeddings.extend(batch_embeddings.tolist())
                
                logger.debug(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text chunk.
        
        Args:
            text: Text chunk to embed
            
        Returns:
            Embedding as a list of floats
        """
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

def generate_embeddings_for_chunks(chunks: List[Dict[str, Any]], 
                                  config_path: str = "config/processing.yaml") -> List[Dict[str, Any]]:
    """
    Generate embeddings for document chunks.
    
    Args:
        chunks: List of document chunks with 'content' field
        config_path: Path to the processing configuration file
        
    Returns:
        List of document chunks with added 'embedding' field
    """
    generator = EmbeddingGenerator(config_path)
    
    # Extract texts from chunks
    texts = [chunk['content'] for chunk in chunks]
    
    # Generate embeddings
    embeddings = generator.generate_embeddings(texts)
    
    # Add embeddings to chunks
    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[i]
    
    return chunks

def generate_embedding_for_text(text: str, 
                               config_path: str = "config/processing.yaml") -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Text to embed
        config_path: Path to the processing configuration file
        
    Returns:
        Embedding as a list of floats
    """
    generator = EmbeddingGenerator(config_path)
    return generator.generate_embedding(text)