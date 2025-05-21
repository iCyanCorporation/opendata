import sys
import os
import argparse
import yaml
import logging
import importlib.util
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.data_collector import DataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_status_log(results):
    """
    Generate a status log file in the root folder.
    
    Args:
        results: List of (crawler, success, source_status) tuples.
    """
    try:
        # Group results by topic
        topics = {}
        for crawler, success, source_status in results:
            topic = crawler['topic']
            country_code = crawler['country_code']
            
            if topic not in topics:
                topics[topic] = {}
            
            if country_code not in topics[topic]:
                topics[topic][country_code] = source_status
        
        # Create the status log file
        log_path = Path(__file__).parent / f"crawl_status_log.md"
        
        with open(log_path, "w") as f:
            f.write(f"# Data Collection Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for topic, countries in topics.items():
                f.write(f"## {topic}\n")
                
                for country_code, sources in countries.items():
                    f.write(f"### {country_code}\n")
                    
                    if sources:
                        for source_name, status in sources.items():
                            status_mark = "[O]" if status else "[X]"
                            f.write(f"{status_mark} {source_name}\n")
                    else:
                        f.write("No sources processed.\n")
                    
                    f.write("\n")
        
        logger.info(f"Status log created at {log_path}")
    except Exception as e:
        logger.error(f"Error generating status log: {e}")

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
        A tuple of (crawler, success, source_status).
    """
    try:
        logger.info(f"Running crawler for {crawler['topic']} - {crawler['country_code']}")
        
        # Use the DataCollector to process the configuration
        collector = DataCollector()
        config_results = collector.process_config(crawler['config_path'])
        
        if config_results and config_results['results']:
            saved_files = collector.save_results(config_results, crawler['config_path'])
            success = len(saved_files) > 0
            return crawler, success, config_results.get('status', {})
        
        logger.error(f"Failed to process configuration for {crawler['topic']} - {crawler['country_code']}")
        return crawler, False, config_results.get('status', {})
        
    except Exception as e:
        logger.error(f"Error running crawler for {crawler['topic']} - {crawler['country_code']}: {e}")
        return crawler, False, {}

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
                    crawler, success, source_status = future.result()
                    results.append((crawler, success, source_status))
                except Exception as e:
                    logger.error(f"Error executing crawler {crawler['topic']} - {crawler['country_code']}: {e}")
                    results.append((crawler, False, {}))
        
        # Report results
        success_count = sum(1 for _, success, _ in results if success)
        logger.info(f"Completed running {len(results)} crawlers. Success: {success_count}, Failed: {len(results) - success_count}")
        
        for crawler, success, _ in results:
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"{status}: {crawler['topic']} - {crawler['country_code']}")
        
        # Generate status log file
        generate_status_log(results)

if __name__ == "__main__":
    main()
