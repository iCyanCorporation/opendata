#!/usr/bin/env python3
# filepath: /home/toyofumi/Project/open-web-scraper-py/scraper.py

import os
import sys
import json
import csv
import requests
import random
from bs4 import BeautifulSoup
import glob
import time
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, config_path=None, sleep_ms=500):
        """Initialize the web scraper with a configuration file.
        
        Args:
            config_path (str, optional): Path to the JSON configuration file.
            sleep_ms (int, optional): Milliseconds to sleep between requests. Default is 0.
        """
        self.config = None
        self.base_url = None
        self.results = []
        self.sleep_ms = sleep_ms
        
        if config_path:
            self.load_config(config_path)
        else:
            # If no config specified, use all JSON files in the input folder
            input_files = glob.glob('input/*.json')
            if input_files:
                self.load_config(input_files[0])
            else:
                logger.error("No input JSON files found in the 'input' directory")
                sys.exit(1)
    
    def load_config(self, config_path):
        """Load the scraper configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                
            # Verify that the config has the required fields
            if 'startUrl' not in self.config or 'selectors' not in self.config:
                logger.error("Invalid configuration file. Missing required fields.")
                sys.exit(1)
                
            # Set the base URL
            if isinstance(self.config['startUrl'], list):
                self.base_url = self.config['startUrl'][0]
            else:
                self.base_url = self.config['startUrl']
                
            self.config_name = os.path.basename(config_path).split('.')[0]
            logger.info(f"Loaded configuration from {config_path}")
            logger.info(f"Starting URL: {self.base_url}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            sys.exit(1)
    
    def get_page(self, url):
        """Fetch the HTML content of a web page."""
        try:
            # Apply sleep if configured (convert milliseconds to seconds)
            if self.sleep_ms > 0:
                # Add a small random variation to sleep time (±10%) to appear more human-like
                variation = 0.1  # 10% variation
                rand_factor = 1.0 - variation + (2 * variation * random.random())
                sleep_sec = (self.sleep_ms / 1000.0) * rand_factor
                logger.info(f"Sleeping for {sleep_sec:.2f} seconds before fetching {url}")
                time.sleep(sleep_sec)
                
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None
    
    def scrape(self):
        """Perform the web scraping based on the configuration."""
        if not self.config:
            logger.error("No configuration loaded.")
            return
        
        logger.info(f"Starting scraping from {self.base_url}")
        
        # Get the starting HTML page
        html = self.get_page(self.base_url)
        if not html:
            return
        
        # Get the categories
        soup = BeautifulSoup(html, 'lxml')
        categories = soup.select('a.category-link')
        
        # Process each category
        for category in categories:
            category_name = category.text.strip()
            category_url = urljoin(self.base_url, category.get('href'))
            logger.info(f"Processing category: {category_name} ({category_url})")
            
            # Get the category page
            category_html = self.get_page(category_url)
            if not category_html:
                continue
            
            # Get the subcategories
            category_soup = BeautifulSoup(category_html, 'lxml')
            subcategories = category_soup.select('a.subcategory-link')
            
            # Process each subcategory
            for subcategory in subcategories:
                subcategory_name = subcategory.text.strip()
                subcategory_url = urljoin(self.base_url, subcategory.get('href'))
                logger.info(f"Processing subcategory: {subcategory_name} ({subcategory_url})")
                
                # Get the subcategory page
                subcategory_html = self.get_page(subcategory_url)
                if not subcategory_html:
                    continue
                
                # Get all product links
                subcategory_soup = BeautifulSoup(subcategory_html, 'lxml')
                products = subcategory_soup.select('a.title')
                
                # Process each product
                for product in products:
                    product_url = urljoin(self.base_url, product.get('href'))
                    logger.info(f"Processing product: {product_url}")
                    
                    # Get the product page
                    product_html = self.get_page(product_url)
                    if not product_html:
                        continue
                    
                    # Extract product information
                    product_soup = BeautifulSoup(product_html, 'lxml')
                    
                    try:
                        # Extract information using the selectors from the config
                        product_info = {
                            'category': category_name,
                            'subcategory': subcategory_name,
                            'prod-link': product_url,
                            'name': product_soup.select_one('h4.title').text.strip() if product_soup.select_one('h4.title') else "",
                            'price': product_soup.select_one('h4.price').text.strip() if product_soup.select_one('h4.price') else "",
                            'description': product_soup.select_one('p.description').text.strip() if product_soup.select_one('p.description') else "",
                        }
                        
                        # Get the image if available
                        image_element = product_soup.select_one('img.image')
                        if image_element and image_element.get('src'):
                            product_info['image'] = urljoin(self.base_url, image_element.get('src'))
                        
                        # Add to results
                        self.results.append(product_info)
                        logger.info(f"Extracted product: {product_info['name']}")
                    except Exception as e:
                        logger.error(f"Error extracting product data: {e}")
                        continue
        
        logger.info(f"Scraped {len(self.results)} items")
    
    def save_results(self, output_format='csv'):
        """Save the scraping results to a file."""
        if not self.results:
            logger.warning("No results to save.")
            return
        
        os.makedirs('output', exist_ok=True)
        output_path = f"output/{self.config_name}.{output_format}"
        
        if output_format == 'csv':
            # Get all unique field names across all results
            fieldnames = set()
            for item in self.results:
                fieldnames.update(item.keys())
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(self.results)
        elif output_format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_path}")

def main():
    """Main entry point for the application."""
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    # Initialize and run the scraper
    scraper = WebScraper(config_path)
    scraper.scrape()
    scraper.save_results()

if __name__ == "__main__":
    main()
