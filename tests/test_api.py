#!/usr/bin/env python3
"""
Test script for the API module.
"""

import os
import sys
import logging
import traceback
import pandas as pd
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging to write to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import our API module
try:
    from core.api import fetch_api_data, process_api_response
    logger.info("Successfully imported API module")
except Exception as e:
    logger.error(f"Failed to import API module: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

def test_doorkeeper_api():
    """Test the Doorkeeper API integration."""
    try:
        url = "https://api.doorkeeper.jp/events"
        headers = {"Accept": "application/json"}
        params = {
            "locale": "en",
            "since": "2023-01-01"
        }
        
        # Fetch data from the API
        logger.info("Fetching data from Doorkeeper API...")
        response_data = fetch_api_data(
            url=url,
            headers=headers,
            params=params
        )
        
        if not response_data:
            logger.error("Failed to fetch data from API")
            return
        
        # Save the raw response to a file for inspection
        import json
        with open("doorkeeper_response.json", "w") as f:
            json.dump(response_data, f, indent=2)
        logger.info("Saved raw API response to doorkeeper_response.json")
        
        # Print response details for debugging
        if isinstance(response_data, dict):
            logger.info(f"Response is a dictionary with keys: {list(response_data.keys())}")
        elif isinstance(response_data, list):
            logger.info(f"Response is a list with {len(response_data)} items")
            if response_data and isinstance(response_data[0], dict):
                logger.info(f"First item has keys: {list(response_data[0].keys())}")
                
                # For a list of dicts, where each dict is an event object
                if 'event' in response_data[0]:
                    logger.info(f"Event object has keys: {list(response_data[0]['event'].keys())}")
                    
                    # Try extracting events directly (special case for Doorkeeper)
                    events_data = [item["event"] for item in response_data if "event" in item]
                    if events_data:
                        df = pd.DataFrame(events_data)
                        logger.info(f"Success with special Doorkeeper handler!")
                        logger.info(f"DataFrame shape: {df.shape}")
                        logger.info(f"DataFrame columns: {df.columns.tolist()}")
                        if not df.empty:
                            logger.info(f"First row sample: {dict(list(df.iloc[0].items())[:5])}")
                        
                        # Save this to a CSV
                        df.to_csv("doorkeeper_events.csv", index=False)
                        logger.info("Saved extracted events to doorkeeper_events.csv")
        
        # Try various data path configurations
        test_configs = [
            {"data_path": ""},  # Use the entire response
            {"data_path": "events"}, # Try the 'events' key
            {"data_path": "0.event"}, # If response is a list and each item has an 'event' key
        ]
        
        for i, config in enumerate(test_configs):
            logger.info(f"Testing config {i+1}: {config}")
            try:
                df = process_api_response(response_data, config)
                if not df.empty:
                    logger.info(f"Success with config {i+1}!")
                    logger.info(f"DataFrame shape: {df.shape}")
                    logger.info(f"DataFrame columns: {df.columns.tolist()}")
                    logger.info(f"First row: {df.iloc[0].to_dict() if len(df) > 0 else 'No data'}")
                else:
                    logger.info(f"Config {i+1} produced empty DataFrame")
            except Exception as e:
                logger.error(f"Error processing with config {i+1}: {e}")
                logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Unexpected error in test_doorkeeper_api: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    try:
        logger.info("Starting API test script")
        test_doorkeeper_api()
        logger.info("API test script completed")
    except Exception as e:
        logger.error(f"Unhandled exception in main: {e}")
        logger.error(traceback.format_exc())
