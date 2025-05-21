"""
Initialization script for the opendata project.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory_structure():
    """
    Creates the initial directory structure for the project.
    """
    project_root = Path(__file__).parent
    
    # Define directories to create
    directories = [
        "config",
        "core",
        "data",
        "tests",
        ".github/workflows",
    ]
    
    # Add topic directories from existing crawlers
    topics_dir = project_root / "topics"
    if topics_dir.exists():
        for topic_dir in topics_dir.iterdir():
            if topic_dir.is_dir():
                directories.append(f"data/{topic_dir.name}")
    
    # Create directories
    for directory in directories:
        dir_path = project_root / directory
        if not dir_path.exists():
            logger.info(f"Creating directory: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
        else:
            logger.info(f"Directory already exists: {dir_path}")

def check_dependencies():
    """
    Checks that all required dependencies are installed.
    """
    try:
        import pandas
        import numpy
        import yaml
        import requests
        import bs4
        import pdfplumber
        import fitz  # PyMuPDF
        import openpyxl
        
        logger.info("All required dependencies are installed.")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Please install all dependencies with: pip install -r requirements.txt")
        return False

def create_sample_data():
    """
    Creates sample data files.
    """
    import pandas as pd
    import datetime
    
    project_root = Path(__file__).parent
    
    # Sample health data for US
    health_data = [
        {"Metric": "Health expenditure per capita", "Value": "$12,530", "Year": "2023", "Source": "CDC"},
        {"Metric": "Life expectancy", "Value": "77.5 years", "Year": "2023", "Source": "CDC"},
        {"Metric": "Physicians per 1,000 people", "Value": "2.6", "Year": "2023", "Source": "CDC"}
    ]
    
    # Get current date for directory structure
    now = datetime.datetime.now()
    date_dir = f"{now.year}/{now.month:02d}/{now.day:02d}"
    
    # Create directory structure for health data
    health_dir = project_root / "data" / "health" / date_dir
    health_dir.mkdir(parents=True, exist_ok=True)
    
    # Save sample health data for US
    health_df = pd.DataFrame(health_data)
    health_df.to_csv(health_dir / "us.csv", index=False)
    logger.info(f"Created sample health data for US at {health_dir / 'us.csv'}")

def main():
    """
    Main initialization function.
    """
    parser = argparse.ArgumentParser(description="Initialize the opendata project.")
    parser.add_argument("--sample-data", action="store_true", help="Create sample data files")
    args = parser.parse_args()
    
    logger.info("Initializing opendata project...")
    
    # Create directory structure
    create_directory_structure()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create sample data if requested
    if args.sample_data:
        create_sample_data()
    
    logger.info("Initialization complete.")

if __name__ == "__main__":
    main()
