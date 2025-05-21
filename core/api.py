#!/usr/bin/env python3
"""
Module for handling API data sources.

This module provides functionality to fetch data from REST APIs with features like:
- API key authentication
- Custom headers
- Query parameters
- Request payloads
- Flexible response processing

Configuration can be either inline within the index.yaml file or in a separate
configuration file referenced by the 'config' property.

Example configuration in index.yaml:
```yaml
sources:
  - name: "API Example"
    enabled: true
    type: "api"
    config: "api-config.yaml"  # External configuration file
```

Example external configuration (api-config.yaml):
```yaml
url: "https://api.example.com/data"
api_key: "your-api-key"
method: "GET"
extraction:
  headers:
    Accept: "application/json"
  params:
    limit: 100
  columns: ["id", "name", "value"]
```
"""

import os
import requests
import json
import logging
import pandas as pd
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_api_data(url: str, api_key: Optional[str] = None, headers: Optional[Dict[str, str]] = None, 
                   params: Optional[Dict[str, Any]] = None, method: str = "GET", 
                   payload: Optional[Dict[str, Any]] = None, sleep_time: float = 0.0) -> Optional[Dict[str, Any]]:
    """
    Fetch data from an API endpoint.
    
    Args:
        url: The API endpoint URL.
        api_key: Optional API key for authentication.
        headers: Optional additional headers.
        params: Optional query parameters.
        method: The HTTP method to use (GET, POST, etc.).
        payload: Optional data payload for POST/PUT requests.
        sleep_time: Optional time in seconds to sleep before making the request (default: 0.0)
        
    Returns:
        The API response data or None if the request failed.
    """
    try:
        # Sleep before making the request if specified
        if sleep_time > 0:
            logger.info(f"Sleeping for {sleep_time} seconds before making API request")
            time.sleep(sleep_time)
        
        # Initialize headers
        request_headers = headers or {}
        
        # Add a default User-Agent if not already provided
        if 'User-Agent' not in request_headers:
            request_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        
        # Add Referer header for Connpass API which might help with 403 errors
        if url and 'connpass.com' in url and 'Referer' not in request_headers:
            request_headers['Referer'] = 'https://connpass.com/'

        # Add API key to headers if provided
        if api_key:
            # Check if X-API-Key is already in headers
            if 'X-API-Key' not in request_headers:
                request_headers['X-API-Key'] = api_key
            # Also add Authorization header as a fallback
            if 'Authorization' not in request_headers:
                request_headers['Authorization'] = f'Bearer {api_key}'
        
        logger.info(f"Making {method} request to {url}")
        logger.info(f"Headers: {request_headers}")
        logger.info(f"Parameters: {params}")
        
        # Add retry mechanism for API requests
        max_retries = 3
        retry_delay = 2  # seconds
        
        for retry in range(max_retries):
            try:
                # Make the request
                if method.upper() == "GET":
                    response = requests.get(url, headers=request_headers, params=params)
                elif method.upper() == "POST":
                    response = requests.post(url, headers=request_headers, params=params, json=payload)
                else:
                    logger.error(f"Unsupported HTTP method: {method}")
                    return None
                
                # Print response details
                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response content type: {response.headers.get('Content-Type', 'Unknown')}")
                
                # If successful, no need to retry
                if response.status_code < 400:
                    break
                
                # If we get a rate limit error (429) or server error (5xx), retry
                if response.status_code in [429, 500, 502, 503, 504]:
                    if retry < max_retries - 1:  # Not the last retry
                        wait_time = retry_delay * (retry + 1)  # Exponential backoff
                        logger.warning(f"Received status code {response.status_code}. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                
                # For 403 errors with Connpass, try a different approach
                if response.status_code == 403 and 'connpass.com' in url:
                    logger.warning("Received 403 from Connpass API. Trying with different headers...")
                    # Try with a completely different User-Agent
                    request_headers['User-Agent'] = f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15'
                    request_headers['Accept-Language'] = 'en-US,en;q=0.9,ja;q=0.8'
                    request_headers['Cache-Control'] = 'no-cache'
                    wait_time = retry_delay * (retry + 1)
                    logger.warning(f"Trying different header approach in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                # For other errors, check if retry would help
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                if retry < max_retries - 1:  # Not the last retry
                    wait_time = retry_delay * (retry + 1)
                    logger.warning(f"Request failed: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                raise  # Re-raise the last exception if all retries failed
        
        # Check response status
        response.raise_for_status()
        
        # Handle possible empty or non-JSON responses
        if not response.content:
            logger.warning(f"Empty response from {url}")
            return {}
            
        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            # Try to handle non-JSON responses
            content_type = response.headers.get('Content-Type', '').lower()
            if 'html' in content_type:
                logger.warning(f"Received HTML response instead of JSON. This might indicate an error page or CAPTCHA.")
                # Save the HTML response for debugging
                debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debug")
                os.makedirs(debug_dir, exist_ok=True)
                html_file = os.path.join(debug_dir, f"html_response_{int(time.time())}.html")
                with open(html_file, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Saved HTML response to {html_file}")
                return {}
            else:
                # For other content types, just log and return empty
                logger.error(f"Received non-JSON response with content type: {content_type}")
                return {}
        
        # Log response structure
        if isinstance(data, dict):
            logger.info(f"API response is a dictionary with keys: {list(data.keys())}")
        elif isinstance(data, list):
            logger.info(f"API response is a list with {len(data)} items")
            if data and isinstance(data[0], dict):
                logger.info(f"First item keys: {list(data[0].keys())}")
        
        return data
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching API data from {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing API response as JSON from {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error when fetching API data from {url}: {e}")
        return None

def process_api_response(response: Dict[str, Any], extraction_config: Dict[str, Any]) -> pd.DataFrame:
    """
    Process an API response to extract specific data.
    
    Args:
        response: The API response data.
        extraction_config: Configuration for extracting data from the response.
        
    Returns:
        A pandas DataFrame with the extracted data.
    """
    if not response:
        logger.error("No API response data to process")
        return pd.DataFrame()
    
    try:
        # Special handling for Doorkeeper API format
        if isinstance(response, list) and response and isinstance(response[0], dict) and "event" in response[0]:
            logger.info("Detected Doorkeeper API response format. Extracting event data.")
            events_data = [item["event"] for item in response if "event" in item]
            if events_data:
                df = pd.DataFrame(events_data)
                return df
        
        # Regular processing for other APIs
        data_path = extraction_config.get('data_path', '')
        
        # Extract data from the specified path
        data = response
        if data_path:
            # Handle paths that don't exist by returning the full response
            # This helps with APIs that return arrays directly
            try:
                for key in data_path.split('.'):
                    if isinstance(data, dict) and key in data:
                        data = data[key]
                    else:
                        logger.warning(f"Key '{key}' not found in API response structure. Using full response data.")
                        break
            except Exception as e:
                logger.warning(f"Error navigating data path: {e}. Using full response data.")
        
        # If data is a list of dictionaries, convert to DataFrame
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            df = pd.DataFrame(data)
        # If data is a dictionary, convert to a single row DataFrame
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        # If data is a list of values, convert to single column DataFrame
        elif isinstance(data, list):
            df = pd.DataFrame({'value': data})
        else:
            logger.error("Unsupported API response format")
            return pd.DataFrame()
        
        # Apply filtering if specified
        filters = extraction_config.get('filters', [])
        for filter_config in filters:
            column = filter_config.get('column')
            operator = filter_config.get('operator', '==')
            value = filter_config.get('value')
            
            if column and value is not None:
                if operator == '==':
                    df = df[df[column] == value]
                elif operator == '!=':
                    df = df[df[column] != value]
                elif operator == '>':
                    df = df[df[column] > value]
                elif operator == '<':
                    df = df[df[column] < value]
                elif operator == 'contains':
                    df = df[df[column].str.contains(value, na=False)]
        
        # Select specific columns if specified
        columns = extraction_config.get('columns', [])
        if columns:
            df = df[[col for col in columns if col in df.columns]]
        
        return df
    
    except Exception as e:
        logger.error(f"Error processing API response: {e}")
        return pd.DataFrame()