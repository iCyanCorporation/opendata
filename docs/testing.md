# Testing Individual Scrapers

This document explains how to test individual scrapers without running the entire crawl process.

## Using the Single Scraper Test Script

The `test_single_scraper.py` script allows you to run a single scraper source from a YAML configuration file. This is useful for testing and debugging individual scrapers.

### Basic Usage

```bash
python tests/test_single_scraper.py <yaml_path> <source_name> [--output <output_dir>]
```

Where:
- `<yaml_path>` is the path to the YAML configuration file
- `<source_name>` is the name of the source to run (must match a source name in the YAML file)
- `<output_dir>` (optional) is the directory to save the output data

### Example

To test the "TOKYO　東京ソラマチ" scraper from the test YAML:

```bash
python tests/test_single_scraper.py tests/test_source.yaml "TOKYO　東京ソラマチ" --output tests/custom_output
```

Or to test it from the main configuration:

```bash
python tests/test_single_scraper.py topics/event/jp/index.yaml "TOKYO　東京ソラマチ"
```

### Output

The script will:
1. Load the specified YAML file
2. Find the specified source
3. Run the scraper with the associated config file
4. Save the results as JSON and CSV (if pandas is available) in a timestamped directory under `tests/test_results/` by default
5. Print status information

### Creating Custom Test YAML Files

You can create custom YAML files for testing purposes. A minimal test YAML file might look like this:

```yaml
# Configuration for testing a single scraper
sources:
  - name: "SourceName"
    enabled: true
    type: "scraper"
    config: "config-file-name.json"
```

Make sure the config file referenced in the YAML is available in the same directory as the YAML file.

## Debugging Tips

If you encounter issues with a scraper:

1. Check that the source is correctly defined in the YAML file
2. Verify that the config file exists and is valid JSON
3. Look for error messages in the logs
4. Try modifying the scraper's configuration for troubleshooting

## Advanced Usage

You can also import and use the `run_single_source` function in your own Python scripts:

```python
from tests.test_single_scraper import run_single_source

success, results = run_single_source('path/to/config.yaml', 'Source Name', 'output/dir')
```
