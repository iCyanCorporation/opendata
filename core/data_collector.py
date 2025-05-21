#!/usr/bin/env python3
"""
Core module for handling YAML-based configurations and orchestrating data collection.
"""

import os
import sys
import yaml
import json
import pandas as pd
import datetime
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Import core modules for different data sources
from .html import fetch_html, parse_html, extract_table, extract_data_by_selector
from .pdf import fetch_pdf, extract_text_pdfplumber, extract_tables_pdfplumber
from .excel import fetch_excel, read_excel_file
from .scraper import WebScraper
from .api import fetch_api_data, process_api_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCollector:
    """
    Core class for collecting data from various sources based on YAML configurations.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the data collector.
        
        Args:
            config_dir: Directory containing YAML configurations.
        """
        self.config_dir = config_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "topics")
        self.project_root = Path(__file__).parent.parent
        
    def load_yaml_config(self, file_path: str) -> Dict:
        """
        Load a YAML configuration file.
        
        Args:
            file_path: Path to the YAML file.
            
        Returns:
            Dictionary containing the configuration.
        """
        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading YAML file {file_path}: {e}")
            return {}
    
    def discover_configs(self, topic: str = None, country_code: str = None) -> List[str]:
        """
        Discover all available YAML configurations.
        
        Args:
            topic: Optional topic to filter by.
            country_code: Optional country code to filter by.
            
        Returns:
            List of paths to YAML configuration files.
        """
        if topic and country_code:
            # Look for a specific topic-country configuration
            yaml_path = os.path.join(self.config_dir, topic, country_code.lower(), "index.yaml")
            return [yaml_path] if os.path.exists(yaml_path) else []
        
        config_files = []
        
        if topic:
            # Look for all configurations for a specific topic
            topic_dir = os.path.join(self.config_dir, topic)
            if os.path.exists(topic_dir):
                # List all country directories under the topic
                country_dirs = [d for d in os.listdir(topic_dir) if os.path.isdir(os.path.join(topic_dir, d))]
                for country_dir in country_dirs:
                    if not country_code or country_dir.lower() == country_code.lower():
                        yaml_path = os.path.join(topic_dir, country_dir, "index.yaml")
                        if os.path.exists(yaml_path):
                            config_files.append(yaml_path)
        else:
            # Look for all configurations
            for topic_dir in os.listdir(self.config_dir):
                topic_path = os.path.join(self.config_dir, topic_dir)
                if os.path.isdir(topic_path):
                    # List all country directories under each topic
                    country_dirs = [d for d in os.listdir(topic_path) if os.path.isdir(os.path.join(topic_path, d))]
                    for country_dir in country_dirs:
                        if not country_code or country_dir.lower() == country_code.lower():
                            yaml_path = os.path.join(topic_path, country_dir, "index.yaml")
                            if os.path.exists(yaml_path):
                                config_files.append(yaml_path)
        
        return config_files
    
    def process_html_source(self, source: Dict, extraction_config: Dict) -> pd.DataFrame:
        """
        Process an HTML source.
        
        Args:
            source: Source configuration dictionary.
            extraction_config: Extraction configuration dictionary.
            
        Returns:
            A pandas DataFrame with the extracted data.
        """
        html_content = fetch_html(source['url'])
        if not html_content:
            logger.error(f"Failed to fetch HTML from {source['url']}")
            return pd.DataFrame()
        
        soup = parse_html(html_content)
        if not soup:
            logger.error(f"Failed to parse HTML from {source['url']}")
            return pd.DataFrame()
        
        data = []
        
        # Extract data using selectors if available
        if 'selectors' in extraction_config:
            selectors_dict = {item['name']: item['selector'] for item in extraction_config['selectors']}
            extracted_data = extract_data_by_selector(soup, selectors_dict)
            for key, value in extracted_data.items():
                data.append({
                    'Metric': key,
                    'Value': value,
                    'Source': source.get('name', 'HTML'),
                    'URL': source['url']
                })
        
        # Extract tables if a table selector is available
        if 'table_selector' in extraction_config:
            table_data = extract_table(soup, extraction_config['table_selector'])
            if table_data:
                header_row = extraction_config.get('header_row', 0)
                headers = table_data[header_row] if len(table_data) > header_row else []
                
                for row in table_data[header_row+1:]:
                    row_data = {}
                    for i, value in enumerate(row):
                        column_name = headers[i] if i < len(headers) else f"Column {i}"
                        row_data[column_name] = value
                    row_data['Source'] = source.get('name', 'HTML Table')
                    row_data['URL'] = source['url']
                    data.append(row_data)
        
        return pd.DataFrame(data)
    
    def process_pdf_source(self, source: Dict, extraction_config: Dict) -> pd.DataFrame:
        """
        Process a PDF source.
        
        Args:
            source: Source configuration dictionary.
            extraction_config: Extraction configuration dictionary.
            
        Returns:
            A pandas DataFrame with the extracted data.
        """
        pdf_path = fetch_pdf(source['url'])
        if not pdf_path:
            logger.error(f"Failed to fetch PDF from {source['url']}")
            return pd.DataFrame()
        
        data = []
        
        # Extract text from specific pages if specified
        if 'pages' in extraction_config:
            for page_num in extraction_config['pages']:
                text = extract_text_pdfplumber(pdf_path, page_num)
                data.append({
                    'Page': page_num,
                    'Content': text,
                    'Source': source.get('name', 'PDF'),
                    'URL': source['url']
                })
        else:
            # Extract all text
            text = extract_text_pdfplumber(pdf_path)
            data.append({
                'Content': text,
                'Source': source.get('name', 'PDF'),
                'URL': source['url']
            })
        
        # Extract tables if needed
        tables = extract_tables_pdfplumber(pdf_path)
        if tables:
            for i, table in enumerate(tables):
                for row in table:
                    row_data = {f"Column {j}": value for j, value in enumerate(row)}
                    row_data['Table'] = i
                    row_data['Source'] = source.get('name', 'PDF Table')
                    row_data['URL'] = source['url']
                    data.append(row_data)
        
        return pd.DataFrame(data)
    
    def process_excel_source(self, source: Dict, extraction_config: Dict) -> pd.DataFrame:
        """
        Process an Excel source.
        
        Args:
            source: Source configuration dictionary.
            extraction_config: Extraction configuration dictionary.
            
        Returns:
            A pandas DataFrame with the extracted data.
        """
        excel_path = fetch_excel(source['url'])
        if not excel_path:
            logger.error(f"Failed to fetch Excel file from {source['url']}")
            return pd.DataFrame()
        
        sheet_name = extraction_config.get('sheet_name', 0)
        header_row = extraction_config.get('header_row', 0)
        skip_rows = extraction_config.get('skip_rows', None)
        
        # Read the Excel file
        df = read_excel_file(
            excel_path, 
            sheet_name=sheet_name,
            header=header_row,
            skiprows=skip_rows
        )
        
        if df is None or df.empty:
            logger.error(f"Failed to read Excel file from {source['url']}")
            return pd.DataFrame()
        
        # Add source information
        df['Source'] = source.get('name', 'Excel')
        df['URL'] = source['url']
        
        # Extract specific columns if specified
        if 'columns' in extraction_config:
            column_mapping = {item['column']: item['name'] for item in extraction_config['columns']}
            df = df.iloc[:, list(column_mapping.keys())]
            df.columns = list(column_mapping.values())
        
        return df
    
    def process_csv_source(self, source: Dict, extraction_config: Dict) -> pd.DataFrame:
        """
        Process a CSV source.
        
        Args:
            source: Source configuration dictionary.
            extraction_config: Extraction configuration dictionary.
            
        Returns:
            A pandas DataFrame with the extracted data.
        """
        # Extract CSV parsing options from extraction_config if available
        csv_options = extraction_config.get('csv_options', {})
        
        # Default options
        options = {
            'delimiter': csv_options.get('delimiter', ','),
            'encoding': csv_options.get('encoding', 'utf-8'),
            'header': csv_options.get('header', 0),
            'dtype': str,  # Use string data type for all columns to avoid type inference issues
            'low_memory': False,  # Better for handling dynamic columns with varying types
        }
        
        # Try with multiple approaches to maximize success
        try:
            # Try reading with provided options first
            logger.info(f"Reading CSV from {source['url']} with custom options")
            try:
                df = pd.read_csv(source['url'], **options)
            except Exception as e:
                logger.warning(f"Standard CSV parsing failed for {source['url']}: {e}, trying with flexible settings")
                # Try with pandas default options if custom failed
                df = pd.read_csv(source['url'])
            
            # Add source information
            df['Source'] = source.get('name', 'CSV')
            df['URL'] = source['url']
            
            # Ensure all column names are strings
            df.columns = df.columns.astype(str)
            
            # Apply additional transformations from extraction_config if specified
            if 'columns' in extraction_config:
                # Handle column renaming if specified
                column_mapping = {}
                for col_config in extraction_config['columns']:
                    if 'original' in col_config and 'rename' in col_config:
                        column_mapping[col_config['original']] = col_config['rename']
                
                if column_mapping:
                    df = df.rename(columns=column_mapping)
            
            return df
        except pd.errors.ParserError:
            # If parsing fails, try with more flexible settings
            try:
                logger.warning(f"Standard CSV parsing failed for {source['url']}, trying with error_bad_lines=False")
                options['on_bad_lines'] = 'skip'  # In newer pandas, error_bad_lines is replaced with on_bad_lines
                df = pd.read_csv(source['url'], **options)
                
                # Add source information
                df['Source'] = source.get('name', 'CSV')
                df['URL'] = source['url']
                
                # Ensure all column names are strings
                df.columns = df.columns.astype(str)
                
                return df
            except Exception as e:
                logger.error(f"Error processing CSV with flexible settings from {source['url']}: {e}")
                
                # Final attempt with minimal expectations - try reading with Python's built-in csv module
                try:
                    import csv
                    import io
                    import requests
                    
                    logger.warning(f"Attempting final fallback with basic CSV module for {source['url']}")
                    response = requests.get(source['url'])
                    response.raise_for_status()
                    
                    csv_content = response.content.decode(options['encoding'], errors='replace')
                    csv_reader = csv.reader(io.StringIO(csv_content), delimiter=options['delimiter'])
                    
                    # Extract headers from first row if header option is 0
                    rows = list(csv_reader)
                    if rows:
                        if options['header'] == 0 and len(rows) > 0:
                            headers = rows[0]
                            data = rows[1:]
                        else:
                            # Generate column names if no header
                            headers = [f"Column{i}" for i in range(len(rows[0]))]
                            data = rows
                        
                        # Create DataFrame
                        df = pd.DataFrame(data, columns=headers)
                        
                        # Add source information
                        df['Source'] = source.get('name', 'CSV')
                        df['URL'] = source['url']
                        
                        return df
                except Exception as nested_e:
                    logger.error(f"All CSV parsing attempts failed for {source['url']}: {nested_e}")
                    return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error processing CSV from {source['url']}: {e}")
            return pd.DataFrame()
    
    def process_api_source(self, source: Dict, extraction_config: Dict) -> pd.DataFrame:
        """
        Process an API source.
        
        Args:
            source: Source configuration dictionary.
            extraction_config: Extraction configuration dictionary.
            
        Returns:
            A pandas DataFrame with the extracted data.
        """
        # Extract API request options
        url = source.get('url')
        api_key = source.get('api_key')
        method = source.get('method', 'GET')
        sleep_time = source.get('sleep_time', 0.0)  # Get sleep time from config, default to 0
        
        # Get headers, params, and payload from extraction config
        headers = extraction_config.get('headers', {})
        params = extraction_config.get('params', {})
        payload = extraction_config.get('payload', {})
        
        logger.info(f"Fetching data from API: {url}")
        
        try:
            # Fetch data from the API
            response_data = fetch_api_data(
                url=url,
                api_key=api_key,
                headers=headers,
                params=params,
                method=method,
                payload=payload,
                sleep_time=sleep_time
            )
            
            if not response_data:
                logger.error(f"Failed to fetch data from API: {url}")
                return pd.DataFrame()
            
            # Add verbose logging to help diagnose API response handling
            if isinstance(response_data, list):
                logger.info(f"API response is a list with {len(response_data)} items")
                if response_data and isinstance(response_data[0], dict):
                    logger.info(f"First item keys: {list(response_data[0].keys())}")
                    if 'event' in response_data[0]:
                        logger.info("Doorkeeper API format detected")
            elif isinstance(response_data, dict):
                logger.info(f"API response is a dictionary with keys: {list(response_data.keys())}")
            
            # Save the raw API response for debugging
            import os
            import json
            from datetime import datetime
            
            try:
                debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debug")
                os.makedirs(debug_dir, exist_ok=True)
                debug_file = os.path.join(debug_dir, f"api_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                with open(debug_file, 'w') as f:
                    json.dump(response_data, f, indent=2)
                logger.info(f"Saved raw API response to {debug_file}")
            except Exception as e:
                logger.warning(f"Could not save debug file: {e}")
            
            # Process the API response
            df = process_api_response(response_data, extraction_config)
            
            if df.empty:
                logger.warning(f"API response processing returned empty DataFrame for {url}")
                return pd.DataFrame()
            
            logger.info(f"API data processed successfully. DataFrame shape: {df.shape}")
            logger.info(f"DataFrame columns: {df.columns.tolist()}")
            
            # Add source information if not already present
            if 'Source' not in df.columns:
                df['Source'] = source.get('name', 'API')
            if 'URL' not in df.columns:
                df['URL'] = url
            
            # Handle ID column conflicts by renaming it
            if 'id' in df.columns:
                df.rename(columns={'id': 'source_id'}, inplace=True)
            
            # Rename any columns according to the project's standard format
            columns_to_rename = {
                'title': 'title',
                'starts_at': 'datetime',
                'description': 'description',
                'address': 'address',
                'venue_name': 'venue',
                'public_url': 'url',
                'published_at': 'published_at'
            }
            
            # Apply column renaming where columns exist
            for old_col, new_col in columns_to_rename.items():
                if old_col in df.columns and old_col != new_col:
                    df[new_col] = df[old_col]
            
            # Ensure required columns exist
            required_columns = ['title', 'datetime', 'description', 'url']
            for col in required_columns:
                if col not in df.columns:
                    logger.warning(f"Required column '{col}' not found in API data")
                    df[col] = ""  # Add empty column for missing required fields
            
            return df
        except Exception as e:
            logger.error(f"Error processing API source {url}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return pd.DataFrame()
    
    def process_source(self, source: Dict, config_path: str = None) -> pd.DataFrame:
        """
        Process a data source based on its type.
        
        Args:
            source: Source configuration dictionary.
            config_path: Path to the YAML config file (used to resolve relative paths)
            
        Returns:
            A pandas DataFrame with the extracted data.
        """
        if not source.get('enabled', True):
            logger.info(f"Source {source.get('id', 'unknown')} is disabled, skipping")
            return pd.DataFrame()
        
        source_type = source.get('type', '').lower()
        extraction_config = source.get('extraction', {})
        
        # Handle config field (used for scraper type)
        config_file = source.get('config')
        if config_file and config_path:
            # Get the directory of the YAML file
            config_dir = os.path.dirname(config_path)
            config_file_path = os.path.join(config_dir, config_file)
            
            # Load the config if it exists
            if os.path.exists(config_file_path):
                try:
                    # Handle different file types (JSON, YAML)
                    if config_file.endswith('.json'):
                        with open(config_file_path, 'r') as f:
                            external_config = json.load(f)
                    elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                        with open(config_file_path, 'r') as f:
                            external_config = yaml.safe_load(f)
                    else:
                        logger.warning(f"Unknown config file type: {config_file}")
                        external_config = {}
                    
                    # Update source and extraction config based on the file type
                    if source_type == 'scraper':
                        extraction_config.update(external_config.get('extraction', {}))
                    elif source_type == 'api':
                        # For API configs, all top-level fields except certain ones go to source
                        for key, value in external_config.items():
                            if key == 'extraction':
                                extraction_config.update(value)
                            elif key not in ['sources', 'metadata', 'name', 'enabled', 'type', 'config']:
                                source[key] = value
                except Exception as e:
                    logger.error(f"Error loading config {config_file_path}: {e}")
                    logger.error(traceback.format_exc())
        
        logger.info(f"Processing {source_type} source: {source.get('name', source.get('url', 'Unknown'))}")
        
        try:
            if source_type == 'html':
                return self.process_html_source(source, extraction_config)
            elif source_type == 'pdf':
                return self.process_pdf_source(source, extraction_config)
            elif source_type == 'excel':
                return self.process_excel_source(source, extraction_config)
            elif source_type == 'csv':
                return self.process_csv_source(source, extraction_config)
            elif source_type == 'api':
                return self.process_api_source(source, extraction_config)
            elif source_type == 'scraper':
                # For the custom scraper type, ensure we have a config
                if not config_file:
                    logger.error(f"Scraper source missing config field: {source.get('name', 'Unknown')}")
                    return pd.DataFrame()
                
                # Get the directory of the YAML file
                config_dir = os.path.dirname(config_path)
                config_file_path = os.path.join(config_dir, config_file)
                
                if not os.path.exists(config_file_path):
                    logger.error(f"Scraper config file not found: {config_file_path}")
                    return pd.DataFrame()
                
                # Use WebScraper class to process this source
                try:
                    scraper = WebScraper(config_file_path)
                    scraper.scrape()
                    
                    # Convert scraper results to DataFrame
                    if scraper.results:
                        df = pd.DataFrame(scraper.results)
                        # Add source information
                        df['Source'] = source.get('name', 'Scraper')
                        return df
                    else:
                        logger.error(f"No results returned from scraper for {source.get('name', 'Unknown')}")
                        return pd.DataFrame()
                except Exception as e:
                    logger.error(f"Error using WebScraper for {source.get('name', 'Unknown')}: {e}")
                    return pd.DataFrame()
            else:
                logger.error(f"Unsupported source type: {source_type}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error processing source {source.get('id', 'unknown')}: {e}")
            return pd.DataFrame()
    
    def process_config(self, config_path: str) -> Dict[str, tuple]:
        """
        Process a configuration file.
        
        Args:
            config_path: Path to the YAML configuration file.
            
        Returns:
            Dictionary containing:
            - 'results': Dict of source IDs and their corresponding DataFrames
            - 'status': Dict of source names and their success status
        """
        try:
            config = self.load_yaml_config(config_path)
            if not config:
                logger.error(f"Empty or invalid configuration in {config_path}")
                return {'results': {}, 'status': {}}
            
            metadata = config.get('metadata', {})
            sources = config.get('sources', [])
            
            if not sources:
                logger.error(f"No sources defined in {config_path}")
                return {'results': {}, 'status': {}}
            
            results = {}
            status = {}
            
            for source in sources:
                source_name = source.get('name', f"source_{len(results)}")
                source_id = source.get('id', source_name)
                
                try:
                    df = self.process_source(source, config_path)
                    
                    if not df.empty:
                        # Add metadata columns
                        for key, value in metadata.items():
                            if key not in df.columns:
                                df[key] = value
                        
                        # Add source_name column to track which YAML source the data came from
                        df['source_name'] = source_name
                        
                        # Ensure all column names are strings
                        df.columns = df.columns.astype(str)
                        
                        results[source_id] = df
                        status[source_name] = True
                    else:
                        status[source_name] = False
                except Exception as e:
                    logger.error(f"Error processing source {source_name}: {e}")
                    status[source_name] = False
            
            return {'results': results, 'status': status}
        except Exception as e:
            logger.error(f"Error processing configuration {config_path}: {e}")
            return {'results': {}, 'status': {}}
    
    def save_results(self, config_results: Dict, config_path: str) -> List[str]:
        """
        Save the results to CSV files.
        
        Args:
            config_results: Dictionary containing results and status from process_config
            config_path: Path to the YAML configuration file.
            
        Returns:
            List of paths to the saved files.
        """
        results = config_results.get('results', {})
        if not results:
            logger.error("No results to save")
            return []
        
        try:
            # Load the YAML config to get country_code from metadata
            config = self.load_yaml_config(config_path)
            if not config:
                logger.error(f"Failed to load configuration for saving results: {config_path}")
                return []
            
            # Get country_code from metadata section of the YAML file
            metadata = config.get('metadata', {})
            country_code = metadata.get('country_code', '').lower()
            
            # If country_code is not in metadata, extract from path as fallback
            if not country_code:
                path_parts = Path(config_path).parts
                topic_idx = next((i for i, part in enumerate(path_parts) if part == 'topics'), -1)
                
                if topic_idx == -1 or topic_idx + 2 >= len(path_parts):
                    logger.error(f"Invalid configuration path and no country_code in metadata: {config_path}")
                    return []
                
                country_code = path_parts[topic_idx + 2].lower()
            
            # Extract topic from config or from path
            topic = metadata.get('topic')
            if not topic:
                path_parts = Path(config_path).parts
                topic_idx = next((i for i, part in enumerate(path_parts) if part == 'topics'), -1)
                if topic_idx != -1 and topic_idx + 1 < len(path_parts):
                    topic = path_parts[topic_idx + 1]
                else:
                    logger.error(f"Cannot determine topic from path or metadata: {config_path}")
                    return []
            
            # Get current date for directory structure
            now = datetime.datetime.now()
            date_dir = f"{now.year}/{now.month:02d}/{now.day:02d}"
            
            # Create directory structure
            output_dir = self.project_root / "data" / topic / date_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            
            saved_files = []
            
            # Main combined output - ensure all columns from all sources are included
            # Use outer join to preserve all columns from all dataframes
            combined_df = pd.concat(results.values(), ignore_index=True, sort=False, join='outer') if len(results) > 1 else next(iter(results.values()))
            
            # Convert all column names to strings to avoid any issues
            combined_df.columns = combined_df.columns.astype(str)
            
            # Add id column (sequential number for each row)
            combined_df.insert(0, 'id', range(1, len(combined_df) + 1))
            
            # Fill NaN values with empty strings for consistency in CSV
            combined_df = combined_df.fillna('')
            
            output_file = output_dir / f"{country_code}.csv"
            combined_df.to_csv(output_file, index=False)
            saved_files.append(str(output_file))
            
            # Separate outputs for each source (if multiple sources) - disabled
            # if len(results) > 1:
            #     for source_id, df in results.items():
            #         # Add id column (sequential number for each row)
            #         df.insert(0, 'id', range(1, len(df) + 1))
            #         
            #         # Fill NaN values with empty strings
            #         df = df.fillna('')
            #         source_file = output_dir / f"{country_code}_{source_id}.csv"
            #         df.to_csv(source_file, index=False)
            #         saved_files.append(str(source_file))
            
            logger.info(f"Saved {len(saved_files)} files")
            return saved_files
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return []
    
    def collect_data(self, topic: str = None, country_code: str = None) -> Dict[str, List[str]]:
        """
        Collect data based on YAML configurations.
        
        Args:
            topic: Optional topic to filter by.
            country_code: Optional country code to filter by.
            
        Returns:
            Dictionary of configuration paths and their saved output files.
        """
        config_files = self.discover_configs(topic, country_code)
        if not config_files:
            logger.error(f"No configuration files found for topic={topic}, country_code={country_code}")
            return {}
        
        results = {}
        for config_path in config_files:
            logger.info(f"Processing configuration: {config_path}")
            config_results = self.process_config(config_path)
            
            if config_results:
                saved_files = self.save_results(config_results, config_path)
                if saved_files:
                    results[config_path] = saved_files
        
        return results
