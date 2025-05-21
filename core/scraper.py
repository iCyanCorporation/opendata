#!/usr/bin/env python3
# filepath: /home/toyofumi/Project/open-web-scraper-py/scraper.py

import os
import sys
import json
import csv
import requests
import random
import re
from bs4 import BeautifulSoup
import glob
import time
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, config_path=None, sleep_ms=0):
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
    
    def expand_url_ranges(self, url):
        """Expand URLs with range patterns like [1-3] into multiple URLs.
        For example, 'page=[1-3]' becomes ['page=1', 'page=2', 'page=3']
        
        Args:
            url (str): URL with possible range pattern
            
        Returns:
            list: List of expanded URLs or the original URL in a list if no range found
        """
        # Find ranges in URL like [1-3]
        range_pattern = r'\[(\d+)-(\d+)\]'
        match = re.search(range_pattern, url)
        
        if not match:
            return [url]  # No range found, return original URL
            
        start = int(match.group(1))
        end = int(match.group(2))
        
        # Generate all URLs in the range
        expanded_urls = []
        for i in range(start, end + 1):
            expanded_url = url.replace(match.group(0), str(i))
            expanded_urls.append(expanded_url)
            
        return expanded_urls
    
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
        
        # Check if the URL contains a range pattern and expand it
        urls = self.expand_url_ranges(self.base_url)
        
        for url in urls:
            logger.info(f"Processing URL: {url}")
            
            # Get the starting HTML page
            html = self.get_page(url)
            if not html:
                continue
            
            # Process based on selectors
            self.process_page(html, url, '_root')
        
        logger.info(f"Scraped {len(self.results)} items")
    
    def process_page(self, html, page_url, parent_selector):
        """Process a page based on the selectors configuration.
        
        Args:
            html (str): HTML content of the page
            page_url (str): URL of the current page
            parent_selector (str): ID of the parent selector
        """
        if not html:
            return
            
        soup = BeautifulSoup(html, 'lxml')
        
        # Find all selectors that have this parent
        child_selectors = [s for s in self.config['selectors'] if parent_selector in s.get('parentSelectors', [])]
        
        for selector in child_selectors:
            selector_id = selector.get('id')
            selector_type = selector.get('type')
            css_selector = selector.get('selector')
            is_multiple = selector.get('multiple', False)
            
            elements = soup.select(css_selector) if css_selector else []
            
            if not elements:
                continue
                
            if selector_type == 'SelectorLink':
                self.process_links(elements, selector, page_url)
            elif selector_type in ['SelectorText', 'SelectorImage']:
                self.process_data(elements, selector, page_url, soup)
    
    def process_links(self, elements, selector, page_url):
        """Process link elements and follow them if needed.
        
        Args:
            elements (list): List of BeautifulSoup elements
            selector (dict): Selector configuration
            page_url (str): URL of the current page
        """
        selector_id = selector.get('id')
        is_multiple = selector.get('multiple', False)
        
        for element in elements:
            href = element.get('href')
            if not href:
                continue
                
            link_url = urljoin(page_url, href)
            logger.info(f"Following link: {link_url}")
            
            # Get the linked page
            link_html = self.get_page(link_url)
            if not link_html:
                continue
                
            # Create a data item for this link if we're at a leaf
            if any(s.get('parentSelectors', []) == [selector_id] for s in self.config['selectors']):
                # Process the linked page with this selector as parent
                item = {'url': link_url}
                self.results.append(item)
                self.process_page(link_html, link_url, selector_id)
            
            if not is_multiple:
                break
    
    def process_data(self, elements, selector, page_url, soup):
        """Process data elements (text, images) and add them to results.
        
        Args:
            elements (list): List of BeautifulSoup elements
            selector (dict): Selector configuration
            page_url (str): URL of the current page
            soup (BeautifulSoup): BeautifulSoup object of the page
        """
        selector_id = selector.get('id')
        selector_type = selector.get('type')
        is_multiple = selector.get('multiple', False)
        
        # Make sure we have at least one result item
        if not self.results:
            self.results.append({'url': page_url})
            
        current_item = self.results[-1]
        
        # Process based on selector type
        if selector_type == 'SelectorText':
            values = [element.get_text().strip() for element in elements]
        elif selector_type == 'SelectorImage':
            values = []
            for element in elements:
                if element.name == 'img':
                    src = element.get('src', '')
                    if src:
                        values.append(urljoin(page_url, src))
        else:
            values = []
            
        if values:
            if is_multiple:
                current_item[selector_id] = values
            else:
                current_item[selector_id] = values[0]
    
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
    
    def expand_url_ranges(self, url):
        """Expand URLs with range patterns like [1-3] into multiple URLs.
        For example, 'page=[1-3]' becomes ['page=1', 'page=2', 'page=3']
        
        Args:
            url (str): URL with possible range pattern
            
        Returns:
            list: List of expanded URLs or the original URL in a list if no range found
        """
        import re
        
        # Find ranges in URL like [1-3]
        range_pattern = r'\[(\d+)-(\d+)\]'
        match = re.search(range_pattern, url)
        
        if not match:
            return [url]  # No range found, return original URL
            
        start = int(match.group(1))
        end = int(match.group(2))
        
        # Generate all URLs in the range
        expanded_urls = []
        for i in range(start, end + 1):
            expanded_url = url.replace(match.group(0), str(i))
            expanded_urls.append(expanded_url)
            
        return expanded_urls
    
    def scrape(self):
        """Perform the web scraping based on the configuration."""
        if not self.config:
            logger.error("No configuration loaded.")
            return
        
        logger.info(f"Starting scraping from {self.base_url}")
        
        # Check if the URL contains a range pattern and expand it
        urls = self.expand_url_ranges(self.base_url)
        
        for url in urls:
            logger.info(f"Processing URL: {url}")
            
            # Get the starting HTML page
            html = self.get_page(url)
            if not html:
                continue
            
            # Process based on selectors
            self.process_page(html, url, '_root')
        
        logger.info(f"Scraped {len(self.results)} items")
    
    def process_page(self, html, page_url, parent_selector):
        """Process a page based on the selectors configuration.
        
        Args:
            html (str): HTML content of the page
            page_url (str): URL of the current page
            parent_selector (str): ID of the parent selector
        """
        if not html:
            return
            
        soup = BeautifulSoup(html, 'lxml')
        
        # Find all selectors that have this parent
        child_selectors = [s for s in self.config['selectors'] if parent_selector in s.get('parentSelectors', [])]
        
        for selector in child_selectors:
            selector_id = selector.get('id')
            selector_type = selector.get('type')
            css_selector = selector.get('selector')
            is_multiple = selector.get('multiple', False)
            
            elements = soup.select(css_selector) if css_selector else []
            
            if not elements:
                continue
                
            if selector_type == 'SelectorLink':
                self.process_links(elements, selector, page_url)
            elif selector_type in ['SelectorText', 'SelectorImage']:
                self.process_data(elements, selector, page_url, soup)
    
    def process_links(self, elements, selector, page_url):
        """Process link elements and follow them if needed.
        
        Args:
            elements (list): List of BeautifulSoup elements
            selector (dict): Selector configuration
            page_url (str): URL of the current page
        """
        selector_id = selector.get('id')
        is_multiple = selector.get('multiple', False)
        
        for element in elements:
            href = element.get('href')
            if not href:
                continue
                
            link_url = urljoin(page_url, href)
            logger.info(f"Following link: {link_url}")
            
            # Get the linked page
            link_html = self.get_page(link_url)
            if not link_html:
                continue
                
            # Create a data item for this link if we're at a leaf
            if any(s.get('parentSelectors', []) == [selector_id] for s in self.config['selectors']):
                # Process the linked page with this selector as parent
                self.process_page(link_html, link_url, selector_id)
            
            if not is_multiple:
                break
    
    def process_data(self, elements, selector, page_url, soup):
        """Process data elements (text, images) and add them to results.
        
        Args:
            elements (list): List of BeautifulSoup elements
            selector (dict): Selector configuration
            page_url (str): URL of the current page
            soup (BeautifulSoup): BeautifulSoup object of the page
        """
        selector_id = selector.get('id')
        selector_type = selector.get('type')
        is_multiple = selector.get('multiple', False)
        
        # Create new item if this is the first data we're collecting
        if not self.results or selector_id == self.config['selectors'][0].get('id'):
            self.results.append({'url': page_url})
            
        current_item = self.results[-1]
        
        # Process based on selector type
        if selector_type == 'SelectorText':
            values = [element.get_text().strip() for element in elements]
        elif selector_type == 'SelectorImage':
            values = []
            for element in elements:
                if element.name == 'img':
                    src = element.get('src', '')
                    if src:
                        values.append(urljoin(page_url, src))
        else:
            values = []
            
        if values:
            if is_multiple:
                current_item[selector_id] = values
            else:
                current_item[selector_id] = values[0]
    
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
