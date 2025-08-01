"""
Main ETL Pipeline Script

This script orchestrates the complete ETL (Extract, Transform, Load) pipeline
for processing jep documents and preparing them for the RAG system.
"""

import os
import sys
import argparse
from typing import Optional

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.etl.excel_reader import read_excel_file
from src.etl.pdf_downloader import download_pdfs
from src.etl.docling_processor import process_document
from src.etl.embedding_generator import generate_embeddings_for_chunks
from src.database.vector_store import initialize_database, VectorStore
from src.utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

def run_etl_pipeline(excel_file_path: str, 
                    download_dir: str = "data/raw",
                    max_documents: Optional[int] = None):
    """
    Run the complete ETL pipeline.
    
    Args:
        excel_file_path: Path to the Excel file containing PDF links
        download_dir: Directory to download PDFs to
        max_documents: Maximum number of documents to process (for testing)
    """
    logger.info("=== Starting ETL Pipeline ===")
    
    try:
        # Step 1: Read Excel file
        logger.info("Step 1: Reading Excel file...")
        pdf_data = read_excel_file(excel_file_path)
        logger.info(f"Found {len(pdf_data)} PDF links in the Excel file")
        
        # Limit number of documents for testing if specified
        if max_documents:
            pdf_data = pdf_data[:max_documents]
            logger.info(f"Limited to {len(pdf_data)} documents for processing")
        
        # Step 2: Download PDFs
        logger.info("Step 2: Downloading PDFs...")
        download_result = download_pdfs(pdf_data, download_dir=download_dir)
        logger.info(f"Successfully downloaded {len(download_result['successful_downloads'])} PDFs")
        
        if not download_result['successful_downloads']:
            logger.error("No PDFs were successfully downloaded. Exiting pipeline.")
            return
        
        # Step 3: Initialize database
        logger.info("Step 3: Initializing database...")
        initialize_database()
        vector_store = VectorStore()
        logger.info("Database initialized successfully")
        
        # Step 4: Process documents and generate embeddings
        logger.info("Step 4: Processing documents and generating embeddings...")
        processed_count = 0
        
        for i, download in enumerate(download_result['successful_downloads']):
            logger.info(f"Processing document {i+1}/{len(download_result['successful_downloads'])}: {download['filename']}")
            
            try:
                # Process document with Docling
                processing_result = process_document(download['filepath'])
                
                if processing_result.status == 'success':
                    logger.info(f"  Generated {len(processing_result.chunks)} chunks")
                    
                    # Convert chunks for embedding generation
                    chunks_for_embedding = [
                        {
                            'content': chunk.content,
                            'chunk_metadata': chunk.chunk_metadata
                        }
                        for chunk in processing_result.chunks
                    ]
                    
                    # Generate embeddings
                    chunks_with_embeddings = generate_embeddings_for_chunks(chunks_for_embedding)
                    
                    # Store document metadata
                    document_id = vector_store.store_document(
                        filename=download['filename'],
                        source_url=download['url'],
                        metadata=download['metadata']
                    )
                    
                    # Store chunks with embeddings
                    vector_store.store_chunks(document_id, chunks_with_embeddings)
                    logger.info(f"  Stored document and {len(chunks_with_embeddings)} chunks")
                    processed_count += 1
                else:
                    logger.error(f"  Processing failed: {processing_result.error_message}")
            except Exception as e:
                logger.error(f"  Error processing document: {str(e)}")
        
        logger.info(f"=== ETL Pipeline Complete ===")
        logger.info(f"Successfully processed {processed_count} documents")
        
    except Exception as e:
        logger.error(f"Error in ETL pipeline: {str(e)}")
        raise

def main():
    """Main entry point for the ETL pipeline."""
    parser = argparse.ArgumentParser(description="Legal Document Chatbot ETL Pipeline")
    parser.add_argument(
        "--excel-file",
        required=True,
        help="Path to the Excel file containing PDF links"
    )
    parser.add_argument(
        "--download-dir",
        default="data/raw",
        help="Directory to download PDFs to"
    )
    parser.add_argument(
        "--max-documents",
        type=int,
        help="Maximum number of documents to process (for testing)"
    )
    
    args = parser.parse_args()
    
    # Run the ETL pipeline
    run_etl_pipeline(
        excel_file_path=args.excel_file,
        download_dir=args.download_dir,
        max_documents=args.max_documents
    )

if __name__ == "__main__":
    main()