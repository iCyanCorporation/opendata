<!-- filepath: /home/toyofumi/Project/opendata/README.md -->

# opendata

> **Collect, Structure, and Share Web Data via GitHub Actions**

## 📌 Project Overview

**opendata** is an automated, topic- and country-aware data pipeline that **crawls public data sources** (HTML, PDFs, Excel, CSV, etc.) from the internet and saves them in **CSV files categorized by topic and country** under a GitHub-hosted repository. All data is refreshed and published using GitHub Actions.

### 🎯 Purpose

- Centralize public open data in a consistent and reusable CSV format
- Support cross-country comparisons by categorizing data per topic and per country
- Automate collection and updates via scheduled GitHub Actions
- Use YAML configuration files to make adding new data sources easy and declarative

### 🚨 Problem Being Solved

Public data is fragmented across formats, languages, and domains. This project **unifies** and **standardizes** datasets, making them programmatically accessible and version-controlled.

### 👥 Target Audience

- Data scientists, researchers, and educators
- Developers building open-data tools
- Policy analysts, journalists, and the public
- Open-source contributors interested in data engineering

---

## 🏗 Architecture & Design Principles

### 🧱 Tech Stack

- **Language**: Python 3.11+
- **Automation**: GitHub Actions
- **Parsing**:

  - HTML: `requests`, `BeautifulSoup4`
  - Scraper: `scrapy`
  - PDF: `pdfplumber`, `PyMuPDF`
  - Excel: `pandas`, `openpyxl`, `xlrd`
  - CSV: `pandas`

- **Output Format**: `.csv` files under `data/{topic}/{yyyy}/{mm}/{dd}/`, named as `{countryCode}.csv`

### 🧠 Design Principles

- **Modular**: One configuration file per topic-country pair in `topics/<topic>/<countryCode>/index.yaml`
- **Scalable**: Easy to add new topics or countries by adding new configuration files
- **Lightweight**: Files capped at 100MB to stay within GitHub's limits
- **Auditable**: Every change is tracked with version control
- **Centralized Config**: Country codes and other settings live in a shared `config/` folder
- **Automated**: GitHub Actions handle all scheduled updates
- **Declarative**: Data sources defined in YAML rather than code, making it easier to add new sources

---

## ⚙️ Installation & Setup

### 🔧 Prerequisites

- Python 3.9+
- Git
- (Optional) Virtual environment: `venv` or `poetry`

### 📦 Setup Instructions

```bash
# Clone the repository
git clone https://github.com/iCyanCorporation/opendata.git
cd opendata

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

# Initialize the project
python init.py
```

### ⚙️ Environment Variables

If needed for accessing certain APIs, you can create a `.env` file in the project root:

```ini
API_KEY=your_api_key_here
```

Use `python-dotenv` to load it automatically in your scripts.

---

## 🚀 Usage Guidelines

### 🔹 Run a Specific Topic-Country Crawler (Manually)

```bash
python crawl_all.py --topic health --country us
```

→ Generates `data/health/2025/05/21/us.csv`

### 🔄 Crawl All Topics for All Countries

```bash
python crawl_all.py
```

This script will:

- Read supported country codes from `config/countries.yaml`
- Discover all topic folders and matching YAML configuration files (`topics/<topic>/<countryCode>/index.yaml`)
- Process data sources defined in each configuration file
- Write output to `data/{topic}/{yyyy}/{mm}/{dd}/{countryCode}.csv`
- Generate a status log file in the root folder (`crawl_status_log.md`)

### 🧪 Run Tests

```bash
pytest tests/
```

## 📊 Crawl Status Monitoring

The project maintains a crawl status log file `crawl_status_log.md` in the root directory, which is automatically generated every time the data collection scripts are run. This file provides information about:

- Which topics and countries were successfully crawled
- Any errors or issues encountered during the crawling process
- Timestamps for the most recent data updates

This makes it easy to monitor the health of the data pipeline and identify any issues that need attention.

---

## 🗂 Code & Folder Structure

```
opendata/
├── config/
│   └── countries.yaml              # ISO codes and country metadata
├── core/
│   ├── data_collector.py          # Main data collection logic
│   ├── html.py                    # HTML parsing utilities
│   ├── pdf.py                     # PDF processing utilities
│   ├── excel.py                   # Excel processing utilities
│   └── scraper.py                 # Web scraping functionality
├── data/
│   ├── education/
│   │   └── 2025/
│   │       └── 05/
│   │           └── 21/
│   │               ├── us.csv
│   │               └── jp.csv
│   └── health/
│       └── 2025/
│           └── 05/
│               └── 21/
│                   ├── us.csv
│                   └── jp.csv
├── topics/
│   ├── education/
│   │   ├── us/
│   │   │   └── index.yaml         # Configuration for US education data
│   │   └── ja/
│   │       ├── index.yaml         # Configuration for Japan education data
│   │       └── test.json          # Test data
│   └── health/
│       ├── us/
│       │   └── index.yaml         # Configuration for US health data
│       └── ja/
│           └── index.yaml         # Configuration for Japan health data
├── init.py                         # Project initialization script
├── crawl_all.py                    # Script to run all crawlers
├── crawl_status_log.md             # Log file for crawl operations
├── requirements.txt
├── tests/
│   └── test_basic.py
├── docs/                           # Documentation folder
└── .github/
    └── workflows/
        └── crawl.yml               # GitHub Action (runs daily)
```

---

## 📁 `config/` Folder Details

### `countries.yaml`

```yaml
# ISO 3166-1 alpha-2 country codes used for naming files
US: United States
CN: China
KR: South Korea
JP: Japan
FR: France
IN: India
BR: Brazil
```

Use this file to:

- Ensure consistent country codes across scripts
- Prevent typos in filenames or crawler logic
- Drive dynamic discovery and validation

---

## 📄 YAML Configuration Format

Each data source is defined by a YAML file in the format `topics/<topic>/<countryCode>/index.yaml`.

### Example YAML Configuration

```yaml
# topics/health/ja/index.yaml
# Configuration for Japan health data
metadata:
  country_code: "JP"
  topic: "health"
  description: "Health expenditure data for Japan"
  year: 2025
  update_frequency: "annual"

# Multiple data sources can be configured
sources:
  - name: "MHLW Health Statistics"
    enabled: true
    type: "html"
    url: "https://www.mhlw.go.jp/english/database/db-hh/index.html"

  - name: "Annual Health Report"
    enabled: true
    type: "pdf"
    url: "https://www.mhlw.go.jp/english/wp/wp-hw/index.html"

  - name: "Health Insurance Statistics"
    enabled: true
    type: "excel"
    url: "https://www.mhlw.go.jp/english/database/excel/health_insurance_2023.xlsx"
```

### Source Types and Required Fields

Each source in the YAML configuration has the following structure:

```yaml
- name: "Source Name"
  enabled: true|false # Whether this source should be processed
  type: "html|pdf|excel|csv"
  url: "https://example.com/data-source"
```

| Source Type | Description                                                 |
| ----------- | ----------------------------------------------------------- |
| `html`      | For crawling a HTML page using BeautifulSoup                |
| `scraper`   | For crawling pages using Scrapy as webs craper              |
| `pdf`       | For extracting data from PDF files using pdfplumber/PyMuPDF |
| `excel`     | For processing Excel spreadsheets using pandas              |
| `csv`       | For direct CSV downloads processed by pandas                |

---

## 📏 Naming & Formatting Conventions

- **CSV File Naming**: `{countryCode}.csv` in date-structured folders
- **YAML Config Naming**: `index.yaml` within country-specific folders
- **Code Format**: `black`
- **Linting**: `ruff`

---

## 🤝 Contribution & Collaboration

### 🌱 How to Contribute

1. Fork the repository
2. Add or update a configuration YAML file in `topics/<topic>/<countryCode>/index.yaml`
3. The crawler will automatically save output to `data/{topic}/{yyyy}/{mm}/{dd}/{countryCode}.csv`
4. Ensure the file is under 100MB
5. Open a PR and follow the review process

### 🌿 Branching Strategy

- `main`: Stable, production-ready
- `dev`: Active development and testing

### ✅ PR Checklist

- [ ] YAML configuration file added or updated in the correct location
- [ ] Output CSV placed correctly under `data/` when tested locally
- [ ] File size < 100MB
- [ ] `config/countries.yaml` updated (if new country)
- [ ] Tests included (if applicable)

### 🐞 Issues & Features

Open a GitHub Issue for:

- Bug reports
- Feature requests
- Country/topic suggestions

---

## 📄 Licensing & Contact Information

### 📜 License

**MIT License** – Open source and free to reuse. See [`LICENSE`](./LICENSE).

### 📬 Maintainer

[@iCyan](https://github.com/iCyanCorporation)

---

## 🛣️ Roadmap

- [x] Modular data source configuration via YAML
- [x] Date-based output structure `data/{topic}/{yyyy}/{mm}/{dd}/{countryCode}.csv`
- [x] Central `config/` folder for settings
- [x] GitHub Actions automation
- [ ] Web frontend for browsing datasets
- [ ] Auto-documentation of available datasets
- [ ] Language localization support
