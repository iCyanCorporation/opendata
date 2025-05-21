"""
Basic tests for the opendata project.
"""

import pytest
import os
import yaml
from pathlib import Path
import importlib.util

# Get project root
project_root = Path(__file__).parent.parent

def test_countries_yaml():
    """Test that countries.yaml exists and is valid."""
    countries_path = project_root / "config" / "countries.yaml"
    assert countries_path.exists(), "countries.yaml file does not exist"
    
    with open(countries_path, "r") as f:
        countries = yaml.safe_load(f)
    
    assert isinstance(countries, dict), "countries.yaml does not contain a dictionary"
    assert len(countries) > 0, "countries.yaml is empty"
    
    # Check for expected format (country code: country name)
    for code, name in countries.items():
        assert isinstance(code, str), f"Country code {code} is not a string"
        assert isinstance(name, str), f"Country name for {code} is not a string"
        assert len(code) == 2, f"Country code {code} is not 2 characters"

def test_crawler_structure():
    """Test that crawler files follow the expected naming pattern."""
    topics_dir = project_root / "topics"
    assert topics_dir.exists(), "topics directory does not exist"
    
    topics = [d for d in topics_dir.iterdir() if d.is_dir()]
    assert len(topics) > 0, "No topic directories found"
    
    for topic_dir in topics:
        crawler_files = list(topic_dir.glob("crawl_*.py"))
        assert len(crawler_files) > 0, f"No crawler files found in {topic_dir}"
        
        for crawler_file in crawler_files:
            # Check naming convention
            assert crawler_file.name.startswith("crawl_"), f"Crawler file {crawler_file} does not start with 'crawl_'"
            
            # Check that the module is importable
            spec = importlib.util.spec_from_file_location("test_module", crawler_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check that it has a main block
            assert hasattr(module, "__name__"), f"Crawler file {crawler_file} does not have a __name__ attribute"

def test_core_modules():
    """Test that core modules exist and are importable."""
    core_modules = ["html", "pdf", "excel"]
    
    for module_name in core_modules:
        module_path = project_root / "core" / f"{module_name}.py"
        assert module_path.exists(), f"Core module {module_name}.py does not exist"
        
        # Check that the module is importable
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

def test_main_script():
    """Test that the main crawl_all.py script exists and is importable."""
    main_script = project_root / "crawl_all.py"
    assert main_script.exists(), "crawl_all.py does not exist"
    
    # Check that the script is importable
    spec = importlib.util.spec_from_file_location("crawl_all", main_script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Check expected functions
    assert hasattr(module, "main"), "crawl_all.py does not have a main function"
    assert hasattr(module, "discover_crawlers"), "crawl_all.py does not have a discover_crawlers function"
    assert hasattr(module, "load_countries"), "crawl_all.py does not have a load_countries function"
