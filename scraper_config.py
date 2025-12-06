# scraper_config.py
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite Configuration
DB_PATH = os.getenv('DB_PATH', 'scraping_data.db')

# Authentication credentials
CREDENTIALS = {
    'username': os.getenv('SCRAPER_USERNAME'),
    'password': os.getenv('SCRAPER_PASSWORD')
}

# Sites configuration
SITES_CONFIG = [
    {
        'name': 'example_site',
        'url': 'https://example.com/login',
        'auth_type': 'form',  # form, session, token
        'selectors': {
            'username_field': 'input#username',
            'password_field': 'input#password',
            'login_button': 'button[type="submit"]'
        }
    }
]

# Data sources configurations
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
    },
    {
        'name': 'PayloadsAllTheThings',
        'auth_required': False,
        'target_urls': [
            'https://github.com/swisskyrepo/PayloadsAllTheThings'
        ],
        'extraction_rules': {
            'folders': '.js-details-container Details ul li a',
            'files': '.js-details-container Details ul li[role="row"] a',
            'readme': '.Box-body .readme blob',
            'descriptions': '.repository-content .Box-row a'
        }
    },
    {
        'name': 'SecLists',
        'auth_required': False,
        'target_urls': [
            'https://github.com/danielmiessler/SecLists'
        ],
        'extraction_rules': {
            'folders': '.js-details-container Details ul li a',
            'files': '.js-details-container Details ul li[role="row"] a',
            'readme': '.Box-body .readme blob',
            'descriptions': '.repository-content .Box-row a'
        }
    },
    {
        'name': 'GTFOBins',
        'auth_required': False,
        'target_urls': [
            'https://gtfobins.github.io'
        ],
        'extraction_rules': {
            'bins': '.binary a',
            'functions': '.func a',
            'descriptions': '.binary .description'
        }
    },
    {
        'name': 'PEASS-ng',
        'auth_required': False,
        'target_urls': [
            'https://github.com/carlospolop/PEASS-ng'
        ],
        'extraction_rules': {
            'folders': '.js-details-container Details ul li a',
            'files': '.js-details-container Details ul li[role="row"] a',
            'readme': '.Box-body .readme blob',
            'descriptions': '.repository-content .Box-row a'
        }
    },
    {
        'name': 'NVD',
        'auth_required': False,
        'target_urls': [
            'https://nvd.nist.gov/vuln/search',
            'https://nvd.nist.gov/vuln/full-listing'
        ],
        'extraction_rules': {
            'cves': '.row .col-md-2 a',
            'titles': '.row .col-md-10',
            'descriptions': '.row .col-md-10 .vuln-summary',
            'cvss_scores': '.row .col-md-10 .vuln-cvss3-panel',
            'published_dates': '.row .col-md-10 .vuln-published-date'
        }
    },
    {
        'name': 'HackerOne',
        'auth_required': False,
        'target_urls': [
            'https://hackerone.com/hacktivity'
        ],
        'extraction_rules': {
            'reports': '.reports-list-item a',
            'titles': '.reports-list-item .report-title',
            'vulnerability_types': '.reports-list-item .vulnerability-type',
            'bounty_amounts': '.reports-list-item .bounty-amount',
            'disclosure_dates': '.reports-list-item .disclosure-date',
            'reputation_scores': '.reports-list-item .reputation-score'
        }
    },
    {
        'name': 'MITRE ATT&CK',
        'auth_required': False,
        'target_urls': [
            'https://attack.mitre.org/techniques/',
            'https://attack.mitre.org/tactics/',
            'https://attack.mitre.org/groups/',
            'https://attack.mitre.org/software/'
        ],
        'extraction_rules': {
            'techniques': '.technique-cell a',
            'tactics': '.tactic-cell a',
            'groups': '.group-cell a',
            'software': '.software-cell a',
            'descriptions': '.description'
        }
    }
]

# Security blogs configurations (non-authenticated since these are public sites)
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
    },
    {
        'name': 'Project Discovery Blog',
        'auth_required': False,
        'target_urls': [
            'https://blog.projectdiscovery.io',
        ],
        'extraction_rules': {
            'titles': 'h2 a, h1 a',
            'summaries': '.post-excerpt, .summary, .content',
            'dates': '.post-meta time, .date, time',
            'links': 'h2 a, h1 a'
        }
    },
    {
        'name': 'Orange Tsai Blog',
        'auth_required': False,
        'target_urls': [
            'https://blog.orange.tw',
        ],
        'extraction_rules': {
            'titles': 'h1.post-title, h2.post-title, .post-title a',
            'summaries': '.post-excerpt, .excerpt, .summary',
            'dates': '.post-date, .date, time',
            'links': 'h1.post-title a, h2.post-title a, .post-title a'
        }
    },
    {
        'name': 'MDSec Blog',
        'auth_required': False,
        'target_urls': [
            'https://www.mdsec.co.uk/blog',
        ],
        'extraction_rules': {
            'titles': 'h2 a, h3 a, .blog-title a',
            'summaries': '.excerpt, .summary, .post-content',
            'dates': '.date, .publish-date, time',
            'links': 'h2 a, h3 a'
        }
    },
    {
        'name': 'Google Project Zero',
        'auth_required': False,
        'target_urls': [
            'https://googleprojectzero.blogspot.com',
        ],
        'extraction_rules': {
            'titles': 'h3.post-title a, .post-title',
            'summaries': '.post-body, .post-summary',
            'dates': '.post-date, .date-header span',
            'links': 'h3.post-title a'
        }
    }
]

# Other settings