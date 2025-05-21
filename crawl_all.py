#!/usr/bin/env python3
"""
Main script to run data collection based on YAML configurations.
"""

import sys
import os
import argparse
import yaml
import logging
import importlib.util
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.data_collector import DataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_countries():
    """
    Loads country codes from the configuration file.
    
    Returns:
        A dictionary of country codes and names.
    """
    config_path = Path(__file__).parent / "config" / "countries.yaml"
    try:
        with open(config_path, "r") as f:
            countries = yaml.safe_load(f)
        return countries
    except Exception as e:
        logger.error(f"Error loading countries: {e}")
        return {}

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Collect data from various sources based on YAML configurations.")
    parser.add_argument("--topic", help="Specific topic to collect data for")
    parser.add_argument("--country", help="Specific country code to collect data for")
    parser.add_argument("--list-configs", action="store_true", help="List available configurations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def discover_crawlers():
    """
    Discovers all available crawlers in the topics directory.
    
    Returns:
        A list of crawler configurations to run.
    """
    crawlers = []
    topics_dir = Path(__file__).parent / "topics"
    
    for topic_dir in topics_dir.iterdir():
        if not topic_dir.is_dir():
            continue
        
        topic = topic_dir.name
        
        # Look for country directories
        for country_dir in topic_dir.iterdir():
            if not country_dir.is_dir():
                continue
                
            country_code = country_dir.name.upper()
            yaml_path = country_dir / "index.yaml"
            
            if yaml_path.exists():
                crawlers.append({
                    "topic": topic,
                    "country_code": country_code,
                    "config_path": str(yaml_path)
                })
    
    return crawlers

def run_crawler(crawler):
    """
    Runs a single crawler.
    
    Args:
        crawler: Dictionary with crawler information.
        
    Returns:
        A tuple of (crawler, success).
    """
    try:
        logger.info(f"Running crawler for {crawler['topic']} - {crawler['country_code']}")
        
        # Use the DataCollector to process the configuration
        collector = DataCollector()
        config_results = collector.process_config(crawler['config_path'])
        
        if config_results:
            saved_files = collector.save_results(config_results, crawler['config_path'])
            if saved_files:
                return crawler, True
        
        logger.error(f"Failed to process configuration for {crawler['topic']} - {crawler['country_code']}")
        return crawler, False
        
    except Exception as e:
        logger.error(f"Error running crawler for {crawler['topic']} - {crawler['country_code']}: {e}")
        return crawler, False

def main():
    """
    Main function to run data collection.
    """
    args = parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize data collector
    collector = DataCollector()
    
    # List available configurations if requested
    if args.list_configs:
        configs = collector.discover_configs(args.topic, args.country)
        if configs:
            logger.info(f"Found {len(configs)} configuration files:")
            for config in configs:
                logger.info(f"  - {config}")
        else:
            logger.info("No configuration files found.")
        return
    
    # If specific topic/country are provided, use the DataCollector directly
    if args.topic or args.country:
        # Load country configurations for validation
        countries = load_countries()
        if not countries:
            logger.warning("No countries configured, proceeding without validation")
        
        # Validate country code if provided
        if args.country and countries and args.country.upper() not in countries:
            logger.error(f"Invalid country code: {args.country}")
            logger.info(f"Available country codes: {', '.join(countries.keys())}")
            return
        
        # Collect data
        results = collector.collect_data(args.topic, args.country)
        
        # Report results
        if results:
            total_files = sum(len(files) for files in results.values())
            logger.info(f"Successfully processed {len(results)} configurations and saved {total_files} output files.")
            
            for config_path, saved_files in results.items():
                logger.info(f"Configuration: {config_path}")
                for file_path in saved_files:
                    logger.info(f"  - {file_path}")
        else:
            logger.error("No data collected. Check logs for errors.")
    else:
        # Run all available crawlers in parallel
        crawlers = discover_crawlers()
        if not crawlers:
            logger.error("No crawlers found, aborting")
            return
        
        logger.info(f"Found {len(crawlers)} crawlers")
        
        # Run crawlers in parallel
        results = []
        with ThreadPoolExecutor(max_workers=min(10, len(crawlers))) as executor:
            future_to_crawler = {executor.submit(run_crawler, crawler): crawler for crawler in crawlers}
            
            for future in as_completed(future_to_crawler):
                crawler = future_to_crawler[future]
                try:
                    crawler, success = future.result()
                    results.append((crawler, success))
                except Exception as e:
                    logger.error(f"Error executing crawler {crawler['topic']} - {crawler['country_code']}: {e}")
                    results.append((crawler, False))
        
        # Report results
        success_count = sum(1 for _, success in results if success)
        logger.info(f"Completed running {len(results)} crawlers. Success: {success_count}, Failed: {len(results) - success_count}")
        
        for crawler, success in results:
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"{status}: {crawler['topic']} - {crawler['country_code']}")

if __name__ == "__main__":
    main()
