"""
Core Excel parsing utilities for the opendata project.
"""

import pandas as pd
import requests
import tempfile
import os
from typing import List, Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

def fetch_excel(url: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Downloads an Excel file from a URL.
    
    Args:
        url: The URL of the Excel file.
        output_path: Optional path to save the file. If None, a temporary file is created.
        
    Returns:
        The path to the downloaded file, or None if there was an error.
    """
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        if output_path is None:
            # Determine file extension from Content-Type or URL
            if 'xls' in url.lower():
                ext = '.xls' if 'xls' in url.lower() and 'xlsx' not in url.lower() else '.xlsx'
            else:
                ext = '.xlsx'  # Default to xlsx
            
            fd, output_path = tempfile.mkstemp(suffix=ext)
            os.close(fd)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    except Exception as e:
        logger.error(f"Error downloading Excel file from {url}: {e}")
        return None

def read_excel_file(file_path: str, sheet_name: Optional[Union[str, int]] = 0, 
                   header: Optional[int] = 0, **kwargs) -> Optional[pd.DataFrame]:
    """
    Reads an Excel file into a pandas DataFrame.
    
    Args:
        file_path: Path to the Excel file.
        sheet_name: Sheet to read. Either sheet name or sheet index.
        header: Row to use as column names (0-indexed).
        **kwargs: Additional arguments to pass to pd.read_excel().
        
    Returns:
        A pandas DataFrame or None if there was an error.
    """
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name, header=header, **kwargs)
    except Exception as e:
        logger.error(f"Error reading Excel file {file_path}: {e}")
        return None

def inspect_excel_metadata(file_path: str) -> Dict[str, Any]:
    """
    Returns metadata about an Excel file, including sheet names and dimensions.
    
    Args:
        file_path: Path to the Excel file.
        
    Returns:
        A dictionary with metadata about the Excel file.
    """
    try:
        excel_info = {}
        xls = pd.ExcelFile(file_path)
        excel_info["sheet_names"] = xls.sheet_names
        
        sheet_dimensions = {}
        for sheet in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet, header=None)
            sheet_dimensions[sheet] = {
                "rows": df.shape[0],
                "columns": df.shape[1]
            }
        
        excel_info["sheet_dimensions"] = sheet_dimensions
        return excel_info
    except Exception as e:
        logger.error(f"Error inspecting Excel file {file_path}: {e}")
        return {"error": str(e)}
