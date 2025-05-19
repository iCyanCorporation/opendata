# opendata

> **Collect, Structure, and Share Open Web Data via GitHub Actions**

## 📌 Project Overview

**opendata** is an automated, topic- and country-aware data pipeline that **crawls public data sources** (HTML, PDFs, Excel, CSV, etc.) from the internet and saves them in **CSV files categorized by topic and country** under a GitHub-hosted repository. All data is refreshed and published using GitHub Actions.

### 🎯 Purpose

* Centralize public open data in a consistent and reusable CSV format.
* Support cross-country comparisons by categorizing data per topic and per country.
* Automate collection and updates via scheduled GitHub Actions.

### 🚨 Problem Being Solved

Public data is fragmented across formats, languages, and domains. This project **unifies** and **standardizes** datasets, making them programmatically accessible and version-controlled.

### 👥 Target Audience

* Data scientists, researchers, and educators
* Developers building open-data tools
* Policy analysts, journalists, and the public
* Open-source contributors interested in data engineering

---

## 🏗 Architecture & Design Principles

### 🧱 Tech Stack

* **Language**: Python 3.11+
* **Automation**: GitHub Actions
* **Parsing**:

  * HTML: `requests`, `BeautifulSoup4`
  * PDF: `pdfplumber`, `PyMuPDF`
  * Excel: `pandas`, `openpyxl`, `xlrd`
  * CSV: `pandas`
* **Output Format**: `.csv` files under `data/`, named as `{topic}_{countryCode}.csv`

### 🧠 Design Principles

* **Modular**: One crawler per topic-country pair
* **Scalable**: Easy to add new topics or countries
* **Lightweight**: Files capped at 100MB to stay within GitHub’s limits
* **Auditable**: Every change is tracked with version control
* **Centralized Config**: Country codes and other settings live in a shared `config/` folder
* **Automated**: GitHub Actions handle all scheduled updates

---

## ⚙️ Installation & Setup

### 🔧 Prerequisites

* Python 3.11+
* Git
* (Optional) Virtual environment: `venv` or `poetry`

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
python topics/health/crawl_us.py
```

→ Generates `data/health/2025/05/19/us.csv`

### 🔄 Crawl All Topics for All Countries

```bash
python crawl_all.py
```

This script will:

* Read supported country codes from `config/countries.yaml`
* Discover all topic folders and matching crawler scripts
* Run each crawler and write output to `data/{topic}/{yyyy}/{mm}/{dd}/{countryCode}.csv`

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
│               └── 19/
│                   ├── us.csv
│                   └── ja.csv
├── topics/
│   ├── health/
│   │   ├── crawl_us.py
│   │   └── crawl_ja.py
│   └── education/
│       └── crawl_us.py
├── init.py                         # For first run
├── crawl.py                        # Runs all crawlers daily
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
...
```

Use this file to:

* Ensure consistent country codes across scripts
* Prevent typos in filenames or crawler logic
* Drive dynamic discovery and validation

---

## 📏 Naming & Formatting Conventions

* **CSV File Naming**: `{countryCode}.csv`
* **Crawler Script Naming**: `crawl_{countryCode}.py`
* **Code Format**: `black`
* **Linting**: `ruff`

---

## 🤝 Contribution & Collaboration

### 🌱 How to Contribute

1. Fork the repository
2. Add or update a crawler script in `topics/<topic>/crawl_<countryCode>.py`
3. Save output to `data/{topic}/{yyyy}/{mm}/{dd}/{countryCode}.csv`
4. Ensure the file is under 100MB
5. Open a PR and follow the review process

### 🌿 Branching Strategy

* `main`: Stable, production-ready
* `dev`: Active development and testing

### ✅ PR Checklist

* [ ] Crawler implemented and tested
* [ ] Output CSV placed correctly under `data/`
* [ ] File size < 100MB
* [ ] `config/countries.yaml` updated (if new country)
* [ ] Tests included (if applicable)

### 🐞 Issues & Features

Open a GitHub Issue for:

* Bug reports
* Feature requests
* Country/topic suggestions

---

## 📄 Licensing & Contact Information

### 📜 License

**MIT License** – Open source and free to reuse. See [`LICENSE`](./LICENSE).

### 📬 Maintainer

[@iCyan](https://github.com/iCyanCorporation)

---

## 🛣️ Roadmap

* [ ] Modular crawler per topic/country
* [ ] Standardized CSV naming `{topic}_{countryCode}.csv`
* [ ] Central `config/` folder for settings
* [ ] GitHub Actions automation
* [ ] Web frontend for browsing datasets
* [ ] Auto-documentation of available datasets
* [ ] Language localization support
