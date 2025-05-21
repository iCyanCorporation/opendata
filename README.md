# opendata

> \*\*Collect, Structure, and Sh### 🧠 Design Principles

- **Modular**: One YAML configuration file per topic-country pair
- **Scalable**: Easy to add new topics or countries by adding new configuration files
- **Lightweight**: Files capped at 100MB to stay within GitHub's limits
- **Auditable**: Every change is tracked with version control
- **Centralized Config**: Country codes and other settings live in a shared `config/` folder
- **Automated**: GitHub Actions handle all scheduled updates
- **Declarative**: Data sources defined in YAML rather than code, making it easier to add new sources Web Data via GitHub Actions\*\*

## 📌 Project Overview

**opendata** is an automated, topic- and country-aware data pipeline that **crawls public data sources** (HTML, PDFs, Excel, CSV, etc.) from the internet and saves them in **CSV files categorized by topic and country** under a GitHub-hosted repository. All data is refreshed and published using GitHub Actions.

### 🎯 Purpose

- Centralize public open data in a consistent and reusable CSV format.
- Support cross-country comparisons by categorizing data per topic and per country.
- Automate collection and updates via scheduled GitHub Actions.

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
  - PDF: `pdfplumber`, `PyMuPDF`
  - Excel: `pandas`, `openpyxl`, `xlrd`
  - CSV: `pandas`

- **Output Format**: `.csv` files under `data/`, named as `{topic}_{countryCode}.csv`

### 🧠 Design Principles

- **Modular**: One crawler per topic-country pair
- **Scalable**: Easy to add new topics or countries
- **Lightweight**: Files capped at 100MB to stay within GitHub’s limits
- **Auditable**: Every change is tracked with version control
- **Centralized Config**: Country codes and other settings live in a shared `config/` folder
- **Automated**: GitHub Actions handle all scheduled updates

---

## ⚙️ Installation & Setup

### 🔧 Prerequisites

- Python 3.11+
- Git
- (Optional) Virtual environment: `venv` or `poetry`

### 📦 Setup Instructions

```bash
git clone https://github.com/<your-org>/opendata.git
cd opendata
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### ⚙️ Environment Variables

If needed, create a `.env` file:

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
- Discover all topic folders and matching YAML configuration files
- Run the appropriate crawler based on the source type specified in the YAML file
- Write output to `data/{topic}/{yyyy}/{mm}/{dd}/{countryCode}.csv`

### 🧪 Run Tests

```bash
pytest tests/
```

---

## 🗂 Code & Folder Structure

```
opendata/
├── config/
│   └── countries.yaml              # ISO codes and country metadata
├── core/
│   ├── html.py                     # Shared HTML parsing utilities
│   ├── pdf.py
│   └── excel.py
├── data/
│   └── health/
│       └── 2025/
│           └── 05/
│               └── 21/
│                   ├── us.csv
│                   └── ja.csv
├── topics/
│   ├── health/
│   │   ├── us.yaml                 # Configuration for US health data
│   │   └── ja.yaml                 # Configuration for Japan health data
│   └── education/
│       └── us.yaml                 # Configuration for US education data
├── init.py                         # For first run
├── crawl_all.py                    # Runs all crawlers daily
├── requirements.txt
├── tests/
├── .env
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

Each data source is defined by a YAML file in the format `topics/<topic>/<countryCode>.yaml`.

### Example YAML Configuration

```yaml
# topics/health/us.yaml
source:
  type: html # Can be: html, pdf, excel, csv
  url: https://www.cdc.gov/nchs/fastats/health-expenditures.htm

extraction:
  selectors:
    - name: "Health Expenditure"
      selector: ".health-expenditure-value"
    - name: "Per Capita Spending"
      selector: ".per-capita-value"

  # For table extraction
  table_selector: "#health-data-table"
  header_row: 0

metadata:
  year: 2025
  source_name: "CDC"
  update_frequency: "annual"
```

### Source Types and Required Fields

| Source Type | Required Fields                                              | Description                        |
| ----------- | ------------------------------------------------------------ | ---------------------------------- |
| `html`      | `url`, `extraction.selectors` or `extraction.table_selector` | For crawling HTML pages            |
| `pdf`       | `url`                                                        | For extracting data from PDF files |
| `excel`     | `url`, `extraction.sheet_name`                               | For processing Excel spreadsheets  |
| `csv`       | `url`                                                        | For direct CSV downloads           |

---

## 📏 Naming & Formatting Conventions

- **CSV File Naming**: `{countryCode}.csv`
- **YAML Config Naming**: `{countryCode}.yaml`
- **Code Format**: `black`
- **Linting**: `ruff`

---

## 🤝 Contribution & Collaboration

### 🌱 How to Contribute

1. Fork the repository
2. Add or update a configuration YAML file in `topics/<topic>/{countryCode}.yaml`
3. The crawler will automatically save output to `data/{topic}/{yyyy}/{mm}/{dd}/{countryCode}.csv`
4. Ensure the file is under 100MB
5. Open a PR and follow the review process

### 🌿 Branching Strategy

- `main`: Stable, production-ready
- `dev`: Active development and testing

### ✅ PR Checklist

- [ ] YAML configuration file added or updated
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
- [ ] Standardized CSV naming `{topic}_{countryCode}.csv`
- [x] Central `config/` folder for settings
- [x] GitHub Actions automation
- [ ] Web frontend for browsing datasets
- [ ] Auto-documentation of available datasets
- [ ] Language localization support
