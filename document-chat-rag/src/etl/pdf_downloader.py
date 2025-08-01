"""
PDF Downloader Module

This module downloads PDF files from URLs provided by the excel_reader module.
"""

import os
import time
import requests
from typing import List, Dict, Any, Tuple
from src.utils.logging import get_logger

logger = get_logger(__name__)

def download_pdf(url: str, filename: str, download_dir: str, max_retries: int = 3) -> Tuple[bool, str]:
    """
    Downloads a PDF file from a URL.
    
    Args:
        url (str): The URL to download the PDF from
        filename (str): The filename to save the PDF as
        download_dir (str): Directory to save the downloaded PDF
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        Tuple[bool, str]: (success, filepath or error message)
    """
    filepath = os.path.join(download_dir, filename)
    
    # Check if file already exists
    if os.path.exists(filepath):
        logger.info(f"File already exists: {filepath}")
        return True, filepath
    
    # Create download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Downloading PDF from {url} (attempt {attempt+1}/{max_retries})")
            
            # Send GET request with stream=True to download in chunks
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Write the content to file in chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            logger.info(f"Successfully downloaded {filename} ({file_size} bytes)")
            
            return True, filepath
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt+1} failed for {url}: {str(e)}")
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {str(e)}")
            return False, str(e)
    
    error_msg = f"Failed to download {url} after {max_retries} attempts"
    logger.error(error_msg)
    return False, error_msg

def download_pdfs(pdf_data: List[Dict[str, Any]], download_dir: str = "data/raw") -> Dict[str, Any]:
    """
    Downloads multiple PDFs from a list of PDF data dictionaries.
    
    Args:
        pdf_data (List[Dict[str, Any]]): List of dictionaries containing PDF information
            Each dict should contain:
            - url: The PDF download URL
            - filename: The filename to save the PDF as
            - metadata: Other metadata from the Excel file
            - row_index: Row index in the Excel file
        download_dir (str): Directory to save the downloaded PDFs
            
    Returns:
        Dict[str, Any]: Dictionary containing:
            - successful_downloads: List of successfully downloaded files
            - failed_downloads: List of failed downloads with error messages
            - total_files: Total number of files processed
    """
    logger.info(f"Starting download of {len(pdf_data)} PDFs")
    
    successful_downloads = []
    failed_downloads = []
    
    for pdf_info in pdf_data:
        url = pdf_info['url']
        filename = pdf_info['filename']
        metadata = pdf_info['metadata']
        row_index = pdf_info['row_index']
        
        logger.info(f"Processing PDF {row_index}: {filename}")
        
        success, result = download_pdf(url, filename, download_dir)
        
        if success:
            successful_downloads.append({
                'url': url,
                'filename': filename,
                'filepath': result,  # result contains the filepath
                'metadata': metadata,
                'row_index': row_index
            })
        else:
            failed_downloads.append({
                'url': url,
                'filename': filename,
                'error': result,  # result contains the error message
                'metadata': metadata,
                'row_index': row_index
            })
    
    logger.info(f"Download complete. Successful: {len(successful_downloads)}, Failed: {len(failed_downloads)}")
    
    return {
        'successful_downloads': successful_downloads,
        'failed_downloads': failed_downloads,
        'total_files': len(pdf_data)
    }

if __name__ == "__main__":
    # Example usage (for testing purposes)
    print("PDF Downloader Module")
    print("This module is designed to download PDF files from URLs")