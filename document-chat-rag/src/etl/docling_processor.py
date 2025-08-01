"""
Document Processing Module using Docling

This module processes PDF documents using Docling's DocumentConverter and HybridChunker
to generate structured chunks with preserved document hierarchy and metadata, specifically
designed for legal documents.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DoclingDocument
from docling.chunking import HybridChunker

from src.utils.logging import get_logger
from src.utils.config import get_config

# Initialize logger
logger = get_logger(__name__)

@dataclass
class DocumentChunk:
    """Represents a chunk of a document with content and metadata."""
    document_id: str
    chunk_index: int
    content: str
    page_numbers: List[int]
    section_title: Optional[str]
    hierarchy_level: int
    chunk_metadata: Dict[str, Any]
    position: Dict[str, Any]  # Positional information within the document

@dataclass
class ProcessingResult:
    """Result of processing a single document."""
    document_id: str
    file_path: str
    status: str  # 'success' or 'error'
    chunks: List[DocumentChunk]
    error_message: Optional[str] = None

class DoclingProcessor:
    """Processor for PDF documents using Docling's DocumentConverter and HybridChunker."""
    
    def __init__(self, config_path: str = "config/processing.yaml"):
        """
        Initialize the DoclingProcessor with configuration.
        
        Args:
            config_path: Path to the processing configuration file
        """
        self.config = get_config(config_path)
        self.chunking_config = self.config.get('chunking', {})
        
        # Initialize Docling components with options optimized for legal documents
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False  # Assuming we're working with text-based PDFs
        pipeline_options.preserve_structure = self.chunking_config.get('preserve_structure', True)
        
        format_options = {
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
        
        self.converter = DocumentConverter(format_options=format_options)
        self.chunker = HybridChunker(
            max_chunk_size=self.chunking_config.get('max_chunk_size', 1000),
            overlap_size=self.chunking_config.get('overlap', 200)
        )
        
        logger.info("DoclingProcessor initialized with chunk size %d and overlap %d",
                    self.chunking_config.get('max_chunk_size', 1000),
                    self.chunking_config.get('overlap', 200))

    def process_document(self, file_path: str, document_id: Optional[str] = None) -> ProcessingResult:
        """
        Process a single PDF document using Docling.
        
        Args:
            file_path: Path to the PDF file
            document_id: Optional identifier for the document
            
        Returns:
            ProcessingResult with chunks or error information
        """
        if document_id is None:
            document_id = os.path.basename(file_path)
            
        try:
            logger.info("Processing document: %s", file_path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                return ProcessingResult(
                    document_id=document_id,
                    file_path=file_path,
                    status="error",
                    chunks=[],
                    error_message=error_msg
                )
            
            # Convert document using Docling
            result = self.converter.convert(file_path)
            docling_doc: DoclingDocument = result.document
            
            # Chunk the document
            chunks = self.chunker.chunk(docling_doc)
            
            # Process chunks and extract metadata
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                # Extract page numbers
                page_numbers = list(set([item.page_no for item in chunk.refs if hasattr(item, 'page_no')]))
                
                # Extract section information
                section_title = None
                hierarchy_level = 0
                
                # Try to get section information from the chunk
                if hasattr(chunk, 'section_title'):
                    section_title = chunk.section_title
                if hasattr(chunk, 'hierarchy_level'):
                    hierarchy_level = chunk.hierarchy_level
                    
                # Extract more detailed metadata for legal documents
                chunk_metadata = {
                    "word_count": len(chunk.text.split()),
                    "char_count": len(chunk.text),
                    "citation_count": chunk.text.count("Art.") + chunk.text.count("§") + chunk.text.count("Inciso"),
                }
                
                # Create DocumentChunk
                doc_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=i,
                    content=chunk.text,
                    page_numbers=page_numbers,
                    section_title=section_title,
                    hierarchy_level=hierarchy_level,
                    chunk_metadata=chunk_metadata,
                    position={
                        "start": i * self.chunking_config.get('max_chunk_size', 1000),
                        "end": (i + 1) * self.chunking_config.get('max_chunk_size', 1000)
                    }
                )
                
                processed_chunks.append(doc_chunk)
            
            logger.info("Successfully processed %s into %d chunks", file_path, len(processed_chunks))
            
            return ProcessingResult(
                document_id=document_id,
                file_path=file_path,
                status="success",
                chunks=processed_chunks
            )
            
        except Exception as e:
            error_msg = f"Error processing document {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return ProcessingResult(
                document_id=document_id,
                file_path=file_path,
                status="error",
                chunks=[],
                error_message=error_msg
            )

    def process_documents(self, file_paths: List[str]) -> List[ProcessingResult]:
        """
        Process multiple PDF documents.
        
        Args:
            file_paths: List of paths to PDF files
            
        Returns:
            List of ProcessingResult objects
        """
        results = []
        for file_path in file_paths:
            result = self.process_document(file_path)
            results.append(result)
        return results

    def process_directory(self, directory_path: str) -> List[ProcessingResult]:
        """
        Process all PDF documents in a directory.
        
        Args:
            directory_path: Path to directory containing PDF files
            
        Returns:
            List of ProcessingResult objects
        """
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        file_paths = [str(pdf_file) for pdf_file in pdf_files]
        return self.process_documents(file_paths)

# Convenience functions for simpler usage
def process_document(file_path: str, config_path: str = "config/processing.yaml") -> ProcessingResult:
    """
    Process a single document using Docling.
    
    Args:
        file_path: Path to the PDF file
        config_path: Path to the processing configuration file
        
    Returns:
        ProcessingResult with chunks or error information
    """
    processor = DoclingProcessor(config_path)
    return processor.process_document(file_path)

def process_documents(file_paths: List[str], config_path: str = "config/processing.yaml") -> List[ProcessingResult]:
    """
    Process multiple documents using Docling.
    
    Args:
        file_paths: List of paths to PDF files
        config_path: Path to the processing configuration file
        
    Returns:
        List of ProcessingResult objects
    """
    processor = DoclingProcessor(config_path)
    return processor.process_documents(file_paths)

def process_directory(directory_path: str, config_path: str = "config/processing.yaml") -> List[ProcessingResult]:
    """
    Process all PDF documents in a directory using Docling.
    
    Args:
        directory_path: Path to directory containing PDF files
        config_path: Path to the processing configuration file
        
    Returns:
        List of ProcessingResult objects
    """
    processor = DoclingProcessor(config_path)
    return processor.process_directory(directory_path)