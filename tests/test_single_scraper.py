#!/usr/bin/env python3
"""
Test script to run a single scraper source from a YAML configuration
"""

import os
import sys
import yaml
import argparse
import logging
import json
from pathlib import Path

# Add parent directory to path to import from core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.scraper import WebScraper
from core.data_collector import DataCollector

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_single_source(yaml_path, source_name, output_dir=None):
    """
    Run a single scraper source from a YAML configuration.
    
    Args:
        yaml_path (str): Path to the YAML configuration file
        source_name (str): Name of the source to run (must match a source name in the YAML file)
        output_dir (str, optional): Directory to save the output data. If None, 
                                    uses the default output directory structure.
    
    Returns:
        bool: True if scraping was successful, False otherwise
        list: The scraped data results
    """
    # Load the YAML configuration
    try:
        with open(yaml_path, 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Failed to load YAML file: {e}")
        return False, []
    
    # Find the specified source
    source_config = None
    for source in config.get('sources', []):
        if source.get('name') == source_name:
            source_config = source
            break
    
    if not source_config:
        logger.error(f"Source '{source_name}' not found in the YAML file")
        return False, []
    
    if not source_config.get('enabled', True):
        logger.warning(f"Source '{source_name}' is disabled in the YAML file")
        return False, []
    
    # Get the source type and config file
    source_type = source_config.get('type')
    config_file = source_config.get('config')
    
    if source_type != 'scraper':
        logger.error(f"Source '{source_name}' is not a scraper (type: {source_type})")
        return False, []
    
    if not config_file:
        logger.error(f"No config file specified for source '{source_name}'")
        return False, []
    
    # Determine the config file path (in the same directory as the YAML file)
    yaml_dir = os.path.dirname(yaml_path)
    config_path = os.path.join(yaml_dir, config_file)
    
    if not os.path.exists(config_path):
        logger.error(f"Config file '{config_path}' does not exist")
        return False, []
    
    # Initialize the scraper
    try:
        scraper = WebScraper(config_path)
        scraper.scrape()  # Use scrape() instead of run()
        results = scraper.results  # Get results from the scraper object
        
        # Save results
        if results and output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{source_name.lower().replace(' ', '_')}_results.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Results saved to {output_file}")
            
            # Also save as CSV for easier viewing
            try:
                # Try to import pandas - it might not be installed
                try:
                    import pandas as pd
                    df = pd.json_normalize(results)
                    csv_file = os.path.join(output_dir, f"{source_name.lower().replace(' ', '_')}_results.csv")
                    df.to_csv(csv_file, index=False, encoding='utf-8')
                    logger.info(f"Results also saved as CSV to {csv_file}")
                except ImportError:
                    logger.warning("Pandas is not installed. CSV output is disabled.")
            except Exception as e:
                logger.warning(f"Could not save results as CSV: {e}")
        
        return True, results
    except Exception as e:
        logger.error(f"Error running scraper: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, []

def main():
    parser = argparse.ArgumentParser(description='Run a single scraper source from a YAML configuration')
    parser.add_argument('yaml_path', help='Path to the YAML configuration file')
    parser.add_argument('source_name', help='Name of the source to run')
    parser.add_argument('--output', '-o', help='Directory to save output data')
    
    args = parser.parse_args()
    
    # Set default output directory if not specified
    if not args.output:
        # Save in test_results directory inside the tests folder
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 'test_results', 
                                 datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    else:
        output_dir = args.output
    
    # Run the scraper
    success, results = run_single_source(args.yaml_path, args.source_name, output_dir)
    
    if success:
        logger.info(f"Successfully scraped {len(results)} items from '{args.source_name}'")
    else:
        logger.error(f"Failed to scrape data from '{args.source_name}'")
        sys.exit(1)

if __name__ == "__main__":
    # Add missing import
    import datetime
    main()
