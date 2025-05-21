"""
Core PDF parsing utilities for the opendata project.
"""

import pdfplumber
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional, Union
import logging
import os
import tempfile
import requests

logger = logging.getLogger(__name__)

def fetch_pdf(url: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Downloads a PDF from a URL.
    
    Args:
        url: The URL of the PDF.
        output_path: Optional path to save the PDF. If None, a temporary file is created.
        
    Returns:
        The path to the downloaded PDF, or None if there was an error.
    """
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        if output_path is None:
            # Create a temporary file
            fd, output_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        return None

def extract_text_pdfplumber(pdf_path: str, page_num: Optional[int] = None) -> str:
    """
    Extracts text from a PDF using pdfplumber.
    
    Args:
        pdf_path: Path to the PDF file.
        page_num: Optional specific page number to extract (0-indexed).
        
    Returns:
        Extracted text as a string.
    """
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            if page_num is not None:
                if 0 <= page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    text = page.extract_text() or ""
                else:
                    logger.error(f"Page number {page_num} out of range (0-{len(pdf.pages)-1})")
            else:
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text with pdfplumber: {e}")
        return ""

def extract_text_pymupdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF using PyMuPDF.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        Extracted text as a string.
    """
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text with PyMuPDF: {e}")
        return ""

def extract_tables_pdfplumber(pdf_path: str) -> List[List[List[str]]]:
    """
    Extracts tables from a PDF using pdfplumber.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        A list of tables, where each table is a list of rows, and each row is a list of cell values.
    """
    try:
        all_tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)
        return all_tables
    except Exception as e:
        logger.error(f"Error extracting tables with pdfplumber: {e}")
        return []
