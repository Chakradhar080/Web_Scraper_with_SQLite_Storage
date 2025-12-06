# Web Scraper with SQLite Storage - Security Data Aggregator

A comprehensive web scraping tool specifically designed to aggregate security data from multiple sources including vulnerability databases, security blogs, and security research repositories. The tool stores scraped data in SQLite with unlimited storage capacity and exports data to multiple file formats.

## Features

- **Unlimited Storage**: No size restriction (unlimited storage, limited only by available disk space)
- **Security Data Sources**: Pre-configured to scrape major security data sources:
  - **Exploit-DB**: https://www.exploit-db.com (exploits, shellcodes, papers)
  - **PayloadsAllTheThings**: https://github.com/swisskyrepo/PayloadsAllTheThings (security payloads)
  - **SecLists**: https://github.com/danielmiessler/SecLists (security lists)
  - **GTFOBins**: https://gtfobins.github.io (Unix binaries for exploitation)
  - **PEASS-ng**: https://github.com/carlospolop/PEASS-ng (privilege escalation tools)
  - **NVD**: https://nvd.nist.gov (National Vulnerability Database)
  - **HackerOne**: https://hackerone.com/hacktivity (security vulnerability reports)
  - **MITRE ATT&CK**: https://attack.mitre.org (framework techniques and tactics)
- **Security Blog Scraping**: Pre-configured to scrape major security research blogs:
  - **PortSwigger Research**: https://portswigger.net/research
  - **Project Discovery**: https://blog.projectdiscovery.io
  - **Orange Tsai**: https://blog.orange.tw
  - **MDSec**: https://www.mdsec.co.uk/blog
  - **Google Project Zero**: https://googleprojectzero.blogspot.com
- **Multiple Authentication Methods**: Form-based, session-based, token-based, and cookie-based authentication
- **Dynamic Content Scraping**: Supports JavaScript-rendered content using Selenium
- **Data Export**: Automatically exports scraped data to JSON, CSV, and TXT formats
- **Duplicate Detection**: Uses content hashing to avoid storing duplicate content
- **Data Validation**: Validates content before storage
- **Specialized Handlers**: Custom scraping logic for GitHub, Exploit-DB, and other complex sites
- **Anti-Detection Measures**: Chrome driver configured to avoid bot detection

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. No database setup needed:
   - SQLite is file-based and no separate installation is required
   - The database file will be created automatically

3. Create a `.env` file in the project root with your credentials (optional):
```env
DB_PATH=scraping_data.db
SCRAPER_USERNAME=your_username
SCRAPER_PASSWORD=your_password
```

## Usage

### Basic Usage

Run the main scraper to scrape all security data sources and security blogs:
```bash
python main_scraper.py
```

The scraper will automatically:
1. Scrape configured security data sources
2. Scrape configured security blogs
3. Store data in SQLite database (unlimited storage)
4. Export data to JSON, CSV, and TXT files in the `scraped_data` directory

### Data Export

All scraped data is automatically exported to multiple formats:
- JSON: Complete structured data export
- CSV: Tabular format suitable for spreadsheets
- TXT: Human-readable format

Exported files are saved in the `scraped_data/` directory with timestamped names.

### Configuration

Edit `scraper_config.py` to add custom scraping jobs:

```python
# Custom site configuration
SITES_CONFIG = [
    {
        'name': 'my_auth_site',
        'auth_required': True,
        'auth_type': 'form',  # form, session, token
        'login_url': 'https://example.com/login',
        'target_urls': [
            'https://example.com/page1',
            'https://example.com/page2'
        ],
        'extraction_rules': {
            'titles': 'h1, h2, h3',
            'content': '.content-class',
            'links': 'a[href]'
        },
        'selectors': {
            'username_field': 'input#username',
            'password_field': 'input#password',
            'login_button': 'button[type="submit"]'
        }
    }
]

# Data sources configurations (pre-configured)
DATA_SOURCES = [
    {
        'name': 'Exploit-DB',
        'auth_required': False,
        'target_urls': [
            'https://www.exploit-db.com',
            'https://www.exploit-db.com/exploits',
            'https://www.exploit-db.com/shellcodes',
            'https://www.exploit-db.com/papers'
        ],
        'extraction_rules': {
            'exploits': '.exploit_table tr td a',
            'titles': '.exploit_table tr td:nth-child(4) a',
            'dates': '.exploit_table tr td:nth-child(1) span',
            'authors': '.exploit_table tr td:nth-child(5) a',
            'platforms': '.exploit_table tr td:nth-child(3) a',
            'types': '.exploit_table tr td:nth-child(2) a',
            'description': '.exploit_table tr td:nth-child(6) span'
        }
    }
]

# Security blog configurations (pre-configured)
SECURITY_BLOGS = [
    {
        'name': 'PortSwigger Research',
        'auth_required': False,
        'target_urls': [
            'https://portswigger.net/research',
        ],
        'extraction_rules': {
            'titles': 'h3 a, h2 a',
            'summaries': '.summary, .excerpt',
            'dates': '.date, .publish-date, time',
            'links': 'h3 a, h2 a'
        }
    }
]
```

### Authentication Methods

#### Form-based Authentication
```python
{
    'auth_type': 'form',
    'login_url': 'https://example.com/login',
    'selectors': {
        'username_field': 'input[name="username"]',
        'password_field': 'input[name="password"]',
        'login_button': 'button[type="submit"]'
    }
}
```

#### Token-based Authentication
```python
{
    'auth_type': 'token',
    'auth_url': 'https://api.example.com/auth',
    'token_field': 'access_token'  # Field name in response that contains the token
}
```

#### Session-based Authentication
```python
{
    'auth_type': 'session',
    'login_url': 'https://example.com/login',
    'data_format': 'json'  # or 'form'
}
```

### Extraction Rules

Define what data to extract using CSS selectors:

```python
extraction_rules = {
    'headings': 'h1, h2, h3',
    'paragraphs': 'p',
    'links': 'a[href]',
    'images': 'img',
    'specific_content': '.class-name'
}
```

## Project Structure

```
Scraping/
├── auth_manager.py        # Handles various authentication methods
├── data_handler.py        # Manages data validation and SQLite storage
├── data_exporter.py       # Handles data export to file formats
├── sqlite_db_utils.py     # SQLite utilities and connection management
├── main_scraper.py        # Main application orchestrator
├── scraper.py             # Main scraper class (legacy)
├── scraper_config.py      # Configuration settings
├── site_scraper.py        # Site-specific scraping logic
├── scraped_data/          # Directory for exported data files
├── scraping_data.db       # SQLite database file
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── PROJECT_SUMMARY.md     # Project overview
```

## SQLite Storage

- Data is stored in SQLite database file with comprehensive tracking
- Automatic duplicate detection using content hashing
- Data validation before storage
- Unlimited storage capacity (no size limitations)
- Logging of storage statistics

## Data Export

The system automatically exports scraped data in three formats:
- **JSON**: Full structured data export in JSON format
- **CSV**: Tabular data export suitable for analysis
- **TXT**: Human-readable format with clear record separation

All exported files include:
- Full content data
- Source URLs
- Scraping timestamps
- Site names
- Content hashes for deduplication

## Specialized Scraping Functions

The system includes specialized handlers for different platforms:

### GitHub Repositories
- Uses GitHub API for repository metadata
- Extracts repository information, files, folders, and README content
- Handles authentication and rate limiting

### Exploit-DB
- Parses exploit tables with detailed information
- Extracts exploit titles, dates, authors, platforms, and descriptions
- Handles multiple exploit categories (exploits, shellcodes, papers)

### NVD (National Vulnerability Database)
- Extracts CVE information and vulnerability details
- Retrieves CVSS scores and published dates
- Handles vulnerability search and listing pages

### GTFOBins
- Extracts Unix binary names and available functions
- Retrieves privilege escalation techniques
- Organizes data by binary and function

### MITRE ATT&CK
- Extracts techniques, tactics, groups, and software
- Retrieves framework classifications
- Handles different ATT&CK matrix sections

### HackerOne
- Extracts vulnerability report information
- Retrieves bounty amounts and disclosure dates
- Handles hacktivity feed scraping

## Usage Examples

### Running Security Data Aggregation
```bash
python main_scraper.py
```
This will scrape all security data sources and security blogs, store data in SQLite, and export to all three formats.

### Using as an Import Module
```python
from main_scraper import MainScraper

scraper = MainScraper()
if scraper.setup():
    # Scrape custom sites
    custom_config = [{
        'name': 'my_site',
        'auth_required': False,
        'target_urls': ['https://example.com'],
        'extraction_rules': {
            'titles': 'h1, h2',
            'content': '.content'
        }
    }]

    scraper.run_multiple_sites(custom_config)

    # Export data
    json_file = scraper.data_handler.export_data(format_type='json')
    csv_file = scraper.data_handler.export_data(format_type='csv')
    txt_file = scraper.data_handler.export_data(format_type='txt')

    scraper.close()
```

## Logging

The application logs to both file (`scraper.log`) and console with different levels of detail.

## Important Notes

1. Be respectful of websites' terms of service and robots.txt
2. Add appropriate delays between requests to avoid overwhelming servers
3. Store credentials securely and never commit them to version control
4. SQLite has unlimited storage capacity (limited only by available disk space)
5. For large-scale scraping, consider data retention strategies
6. All security data sources and blogs are pre-configured in `scraper_config.py`

