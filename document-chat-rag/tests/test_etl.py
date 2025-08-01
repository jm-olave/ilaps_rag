"""
Test script for ETL modules (Excel Reader and PDF Downloader)
Compatible with pytest
"""

import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.etl.excel_reader import read_excel_file, validate_excel_format
from src.etl.pdf_downloader import download_pdf, download_pdfs

def test_excel_reader_functions():
    """Test that Excel reader functions exist"""
    assert hasattr(read_excel_file, '__call__'), "read_excel_file function should exist"
    assert hasattr(validate_excel_format, '__call__'), "validate_excel_format function should exist"

def test_pdf_downloader_functions():
    """Test that PDF downloader functions exist"""
    assert hasattr(download_pdf, '__call__'), "download_pdf function should exist"
    assert hasattr(download_pdfs, '__call__'), "download_pdfs function should exist"

# For running directly (not through pytest)
if __name__ == "__main__":
    test_excel_reader_functions()
    test_pdf_downloader_functions()
    print("All tests passed!")