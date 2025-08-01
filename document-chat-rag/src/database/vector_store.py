"""
Vector Store Module

This module handles storage and retrieval of document embeddings in PostgreSQL with pgvector.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

from src.utils.logging import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)

class VectorStore:
    """Handles storage and retrieval of document embeddings in PostgreSQL with pgvector."""
    
    def __init__(self, config_path: str = "config/database.yaml"):
        """
        Initialize the VectorStore with database configuration.
        
        Args:
            config_path: Path to the database configuration file
        """
        # Load database configuration
        try:
            db_config = get_config(config_path)
        except FileNotFoundError:
            # If config file doesn't exist, use environment variables
            db_config = {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_PORT', 5432)),
                'database': os.getenv('POSTGRES_DB', 'legal_docs'),
                'user': os.getenv('POSTGRES_USER', 'postgres'),
                'password': os.getenv('POSTGRES_PASSWORD', 'password')
            }
        
        # Store connection parameters
        self.connection_params = {
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 5432),
            'database': db_config.get('database', 'legal_docs'),
            'user': db_config.get('user', 'postgres'),
            'password': db_config.get('password', 'password')
        }
        
        # Test connection
        try:
            conn = psycopg2.connect(**self.connection_params)
            conn.close()
            logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL database: {str(e)}")
            raise
    
    def create_tables(self):
        """Create the necessary tables in the database."""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            # Create documents table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    source_url TEXT,
                    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size BIGINT,
                    document_type VARCHAR(100),
                    metadata JSONB
                )
            """)
            
            # Create document_chunks table with vector embedding
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id),
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding VECTOR(1536),  -- Adjust dimension based on embedding model
                    chunk_metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create vector index for similarity search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
                ON document_chunks 
                USING ivfflat (embedding vector_cosine_ops)
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    def store_document(self, filename: str, source_url: Optional[str] = None, 
                      file_size: Optional[int] = None, document_type: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Store document metadata in the database.
        
        Args:
            filename: Name of the document file
            source_url: URL from which the document was downloaded
            file_size: Size of the document file in bytes
            document_type: Type of document
            metadata: Additional metadata as JSON
            
        Returns:
            ID of the inserted document
        """
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO documents (filename, source_url, file_size, document_type, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (filename, source_url, file_size, document_type, metadata))
            
            document_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Stored document {filename} with ID {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error storing document {filename}: {str(e)}")
            raise
    
    def store_chunks(self, document_id: int, chunks: List[Dict[str, Any]]):
        """
        Store document chunks with embeddings in the database.
        
        Args:
            document_id: ID of the parent document
            chunks: List of chunk dictionaries with content, embedding, and metadata
        """
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            # Prepare data for batch insert
            chunk_data = []
            for i, chunk in enumerate(chunks):
                chunk_data.append((
                    document_id,
                    i,
                    chunk['content'],
                    chunk['embedding'],  # This should be a list of floats
                    chunk.get('chunk_metadata', {})
                ))
            
            # Batch insert using execute_values
            execute_values(cur, """
                INSERT INTO document_chunks (document_id, chunk_index, content, embedding, chunk_metadata)
                VALUES %s
            """, chunk_data)
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Stored {len(chunks)} chunks for document ID {document_id}")
            
        except Exception as e:
            logger.error(f"Error storing chunks for document ID {document_id}: {str(e)}")
            raise
    
    def search_similar_chunks(self, query_embedding: List[float], 
                             limit: int = 10, 
                             similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for chunks similar to the query embedding.
        
        Args:
            query_embedding: Embedding vector of the query
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score (cosine similarity)
            
        Returns:
            List of similar chunks with similarity scores
        """
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            # Search for similar chunks using cosine similarity
            cur.execute("""
                SELECT dc.id, dc.document_id, dc.chunk_index, dc.content, dc.chunk_metadata,
                       1 - (dc.embedding <=> %s) as similarity
                FROM document_chunks dc
                WHERE 1 - (dc.embedding <=> %s) >= %s
                ORDER BY similarity DESC
                LIMIT %s
            """, (query_embedding, query_embedding, similarity_threshold, limit))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    'id': row[0],
                    'document_id': row[1],
                    'chunk_index': row[2],
                    'content': row[3],
                    'chunk_metadata': row[4],
                    'similarity': row[5]
                })
            
            cur.close()
            conn.close()
            
            logger.info(f"Found {len(results)} similar chunks")
            return results
            
        except Exception as e:
            logger.error(f"Error searching for similar chunks: {str(e)}")
            raise

# Convenience functions for simpler usage
def create_vector_store(config_path: str = "config/database.yaml") -> VectorStore:
    """
    Create a VectorStore instance.
    
    Args:
        config_path: Path to the database configuration file
        
    Returns:
        VectorStore instance
    """
    return VectorStore(config_path)

def initialize_database(config_path: str = "config/database.yaml"):
    """
    Initialize the database by creating tables.
    
    Args:
        config_path: Path to the database configuration file
    """
    vector_store = VectorStore(config_path)
    vector_store.create_tables()