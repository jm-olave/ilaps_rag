"""
Test script for Docling Processor
Compatible with pytest
"""

import sys
import os
import tempfile
from unittest.mock import Mock, patch

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.etl.docling_processor import (
    DoclingProcessor, 
    process_document, 
    process_documents, 
    process_directory,
    DocumentChunk,
    ProcessingResult
)

def test_docling_processor_class_exists():
    """Test that DoclingProcessor class exists"""
    assert hasattr(DoclingProcessor, '__class__'), "DoclingProcessor class should exist"

def test_processing_result_class_exists():
    """Test that ProcessingResult class exists"""
    assert hasattr(ProcessingResult, '__class__'), "ProcessingResult class should exist"

def test_document_chunk_class_exists():
    """Test that DocumentChunk class exists"""
    assert hasattr(DocumentChunk, '__class__'), "DocumentChunk class should exist"

def test_convenience_functions_exist():
    """Test that convenience functions exist"""
    assert hasattr(process_document, '__call__'), "process_document function should exist"
    assert hasattr(process_documents, '__call__'), "process_documents function should exist"
    assert hasattr(process_directory, '__call__'), "process_directory function should exist"

# For running directly (not through pytest)
if __name__ == "__main__":
    test_docling_processor_class_exists()
    test_processing_result_class_exists()
    test_document_chunk_class_exists()
    test_convenience_functions_exist()
    print("All tests passed!")