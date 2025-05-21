"""
Core HTML parsing utilities for the opendata project.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

def fetch_html(url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    Fetches HTML content from a URL.
    
    Args:
        url: The URL to fetch.
        headers: Optional request headers.
        
    Returns:
        The HTML content as a string, or None if there was an error.
    """
    try:
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        headers = headers or default_headers
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None

def parse_html(html_content: str) -> Optional[BeautifulSoup]:
    """
    Parses HTML content into a BeautifulSoup object.
    
    Args:
        html_content: The HTML content to parse.
        
    Returns:
        A BeautifulSoup object, or None if there was an error.
    """
    try:
        return BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return None

def extract_table(soup: BeautifulSoup, table_selector: str) -> List[List[str]]:
    """
    Extracts a table from HTML into a list of rows and columns.
    
    Args:
        soup: The BeautifulSoup object.
        table_selector: CSS selector for the target table.
        
    Returns:
        A list of rows, where each row is a list of column values.
    """
    table = soup.select_one(table_selector)
    if not table:
        logger.error(f"Table not found using selector: {table_selector}")
        return []
    
    rows = []
    for tr in table.select('tr'):
        row = []
        for cell in tr.select('td, th'):
            row.append(cell.text.strip())
        if row:  # Skip empty rows
            rows.append(row)
    
    return rows

def extract_data_by_selector(soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, str]:
    """
    Extracts data from HTML using CSS selectors.
    
    Args:
        soup: The BeautifulSoup object.
        selectors: A dictionary where keys are field names and values are CSS selectors.
        
    Returns:
        A dictionary of extracted data.
    """
    result = {}
    for key, selector in selectors.items():
        element = soup.select_one(selector)
        if element:
            result[key] = element.text.strip()
        else:
            logger.warning(f"Element not found for selector: {selector}")
            result[key] = ""
    
    return result
