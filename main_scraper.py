# main_scraper.py
import time
import logging
from scraper_config import SITES_CONFIG, CREDENTIALS, SECURITY_BLOGS, DATA_SOURCES
from site_scraper import SiteScraper
from data_handler import DataHandler

class MainScraper:
    def __init__(self):
        self.scraper = SiteScraper()
        self.data_handler = DataHandler()
        self.running = False
        
    def setup(self):
        """
        Setup the scraper environment
        """
        print("Setting up scraper environment...")
        
        # Connect to SQLite
        if not self.data_handler.connect_to_db():
            print("Failed to connect to SQLite")
            return False
        
        print("Setup completed successfully")
        return True
    
    def run_scraping_job(self, site_config):
        """
        Run a scraping job for a specific site
        
        Args:
            site_config: Configuration dictionary for the site to scrape
        """
        print(f"Starting scraping job for: {site_config['name']}")
        
        try:
            extraction_rules = site_config.get('extraction_rules', {})
            target_urls = site_config.get('target_urls', [])
            
            if 'auth_required' in site_config and site_config['auth_required']:
                # Handle authenticated site
                login_config = {
                    'auth_type': site_config.get('auth_type', 'form'),
                    'login_url': site_config['login_url'],
                    'username': CREDENTIALS['username'],
                    'password': CREDENTIALS['password']
                }
                
                # Add selectors if form-based auth
                if site_config.get('auth_type') == 'form':
                    login_config['selectors'] = site_config.get('selectors', {})
                
                scraped_data = self.scraper.scrape_protected_site(
                    login_config,
                    target_urls,
                    extraction_rules
                )
            else:
                # Handle public site (no authentication)
                scraped_data = {}
                for url in target_urls:
                    print(f"Scraping public URL: {url}")
                    page_data = self.scraper.scrape_public_site(url, extraction_rules)
                    scraped_data[url] = page_data
            
            # Store the scraped data
            if scraped_data:
                for url, data in scraped_data.items():
                    if data:  # Only store non-empty data
                        data['source_url'] = url
                        data['site_name'] = site_config['name']
                        self.data_handler.store_scraped_data(data)
                        print(f"Stored data from {url}")
            else:
                print(f"No data scraped from {site_config['name']}")
                
        except Exception as e:
            logging.error(f"Error in scraping job for {site_config['name']}: {e}")
            print(f"Error scraping {site_config['name']}: {e}")
    
    def run_multiple_sites(self, sites_configs):
        """
        Run scraping jobs for multiple sites
        
        Args:
            sites_configs: List of site configuration dictionaries
        """
        for site_config in sites_configs:
            try:
                self.run_scraping_job(site_config)
                
                # Add delay between sites to be respectful
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error processing site {site_config.get('name', 'Unknown')}: {e}")
    
    def run_continuous_scraping(self, sites_configs, interval_minutes=60):
        """
        Run continuous scraping at specified intervals
        
        Args:
            sites_configs: List of site configuration dictionaries
            interval_minutes: Time interval between scraping runs in minutes
        """
        self.running = True
        print(f"Starting continuous scraping, checking every {interval_minutes} minutes...")
        
        while self.running:
            try:
                print(f"\n--- Scraping run started at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
                self.run_multiple_sites(sites_configs)
                
                print(f"Waiting {interval_minutes} minutes until next run...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\nStopping continuous scraping...")
                self.running = False
            except Exception as e:
                logging.error(f"Error in continuous scraping: {e}")
                print(f"Error in continuous scraping: {e}")
                time.sleep(interval_minutes * 60)  # Continue after error
    
    def get_storage_stats(self):
        """
        Get current storage statistics
        """
        return self.data_handler.get_storage_stats()
    
    def close(self):
        """
        Close the scraper and clean up resources
        """
        print("Shutting down scraper...")
        self.running = False
        self.scraper.close()
        self.data_handler.close_connection()
        print("Scraper shutdown complete")

# Example configurations
EXAMPLE_SITES = [
    # Example of a public site (no auth)
    {
        'name': 'quotes_to_scrape',
        'auth_required': False,
        'target_urls': ['https://quotes.toscrape.com/'],
        'extraction_rules': {
            'quotes': 'span.text',
            'authors': 'small.author',
            'tags': 'div.tags a.tag'
        }
    },
    # Example of an authenticated site (form-based auth)
    {
        'name': 'example_auth_site',
        'auth_required': True,
        'auth_type': 'form',
        'login_url': 'https://example.com/login',
        'target_urls': ['https://example.com/dashboard', 'https://example.com/profile'],
        'extraction_rules': {
            'content': '.content',
            'title': 'h1'
        },
        'selectors': {
            'username_field': 'input#username',
            'password_field': 'input#password', 
            'login_button': 'button[type="submit"]'
        }
    },
    # Example of a site requiring dynamic interactions
    {
        'name': 'dynamic_content_site',
        'auth_required': False,
        'target_urls': ['https://quotes.toscrape.com/'],
        'extraction_rules': {
            'quotes': 'span.text',
            'authors': 'small.author'
        }
    }
]

if __name__ == "__main__":
    # Initialize main scraper
    main_scraper = MainScraper()

    try:
        # Setup the scraper
        if not main_scraper.setup():
            print("Setup failed, exiting...")
            exit(1)

        # Run scraping for configured sites
        print("Starting scraping process...")
        main_scraper.run_multiple_sites(EXAMPLE_SITES)

        # Scrape data sources
        print("\nStarting scraping of security data sources...")
        main_scraper.run_multiple_sites(DATA_SOURCES)

        # Scrape security blogs
        print("\nStarting scraping of security blogs...")
        main_scraper.run_multiple_sites(SECURITY_BLOGS)

        # Display storage statistics
        stats = main_scraper.get_storage_stats()
        if stats:
            print(f"\nStorage Statistics:")
            print(f"Size: {stats['size']} bytes")
            print(f"Count: {stats['count']} records")
            print(f"Capped: {stats['capped']}")
            print(f"File Size: {stats['file_size']} bytes")

        # Export data to files after scraping
        print("\nExporting scraped data to files...")
        json_file = main_scraper.data_handler.export_data(format_type='json')
        csv_file = main_scraper.data_handler.export_data(format_type='csv')
        txt_file = main_scraper.data_handler.export_data(format_type='txt')

        if json_file:
            print(f"JSON export successful: {json_file}")
        if csv_file:
            print(f"CSV export successful: {csv_file}")
        if txt_file:
            print(f"TXT export successful: {txt_file}")

    finally:
        main_scraper.close()