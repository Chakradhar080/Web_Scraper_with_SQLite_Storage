import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
from scraper_config import *
from data_handler import DataHandler

class WebScraper:
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.data_handler = DataHandler()

        # Connect to SQLite
        self.data_handler.connect_to_db()
    
    def _setup_collection(self):
        """
        Set up MongoDB collection with 50MB size limit
        """
        try:
            # Drop collection if it exists and recreate with size limit
            print("Initialized collection for storing scraped data")
        except Exception as e:
            print(f"Error setting up collection: {e}")
    
    def setup_driver(self):
        """
        Set up Chrome driver with options
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(),
            options=chrome_options
        )
        return self.driver
    
    def authenticate_form_based(self, site_config):
        """
        Handle form-based authentication
        """
        try:
            self.driver.get(site_config['url'])
            
            # Wait for login elements to load
            wait = WebDriverWait(self.driver, 10)
            username_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, site_config['selectors']['username_field']))
            )
            password_field = self.driver.find_element(By.CSS_SELECTOR, site_config['selectors']['password_field'])
            login_button = self.driver.find_element(By.CSS_SELECTOR, site_config['selectors']['login_button'])
            
            # Fill in credentials
            username_field.send_keys(CREDENTIALS['username'])
            password_field.send_keys(CREDENTIALS['password'])
            
            # Click login
            login_button.click()
            
            # Wait for login to complete
            time.sleep(3)
            
            print("Form-based authentication successful")
            return True
        except Exception as e:
            print(f"Form-based authentication failed: {e}")
            return False
    
    def authenticate_session_based(self, site_config):
        """
        Handle session-based authentication
        """
        try:
            login_data = {
                'username': CREDENTIALS['username'],
                'password': CREDENTIALS['password']
            }
            
            # Send login request
            response = self.session.post(site_config['url'], data=login_data)
            
            if response.status_code == 200:
                print("Session-based authentication successful")
                return True
            else:
                print("Session-based authentication failed")
                return False
        except Exception as e:
            print(f"Session-based authentication failed: {e}")
            return False
    
    def authenticate_token_based(self, site_config):
        """
        Handle token-based authentication
        """
        try:
            # Get token (this is a simplified example - actual implementation depends on the API)
            headers = {'Content-Type': 'application/json'}
            auth_data = {
                'username': CREDENTIALS['username'],
                'password': CREDENTIALS['password']
            }
            
            response = self.session.post(site_config['auth_url'], json=auth_data, headers=headers)
            
            if response.status_code == 200:
                token = response.json().get('token')
                self.session.headers.update({'Authorization': f'Bearer {token}'})
                
                print("Token-based authentication successful")
                return True
            else:
                print("Token-based authentication failed")
                return False
        except Exception as e:
            print(f"Token-based authentication failed: {e}")
            return False
    
    def authenticate(self, site_config):
        """
        Authenticate based on site configuration
        """
        auth_type = site_config.get('auth_type', 'form')
        
        if auth_type == 'form':
            return self.authenticate_form_based(site_config)
        elif auth_type == 'session':
            return self.authenticate_session_based(site_config)
        elif auth_type == 'token':
            return self.authenticate_token_based(site_config)
        else:
            print(f"Unknown authentication type: {auth_type}")
            return False
    
    def scrape_page(self, url, use_selenium=False):
        """
        Scrape a specific page
        """
        try:
            if use_selenium and self.driver:
                self.driver.get(url)
                time.sleep(2)  # Wait for page to load
                page_content = self.driver.page_source
            else:
                response = self.session.get(url)
                page_content = response.text
            
            soup = BeautifulSoup(page_content, 'html.parser')
            return soup
        except Exception as e:
            print(f"Error scraping page {url}: {e}")
            return None
    
    def extract_data(self, soup, extraction_rules):
        """
        Extract specific data from the page based on rules
        """
        data = {}
        
        for key, selector in extraction_rules.items():
            elements = soup.select(selector)
            if elements:
                # Extract text from all matching elements
                data[key] = [elem.get_text(strip=True) for elem in elements]
            else:
                data[key] = []
        
        return data
    
    def store_data(self, data):
        """
        Store scraped data in SQLite
        """
        try:
            # Add timestamp to data
            import datetime
            data['timestamp'] = datetime.datetime.utcnow().isoformat()

            # Store data using DataHandler
            result_id = self.data_handler.store_scraped_data(data)
            if result_id is not None:
                print(f"Data stored with ID: {result_id}")
            return result_id
        except Exception as e:
            print(f"Error storing data: {e}")
            return None
    
    def scrape_site(self, site_config, extraction_rules):
        """
        Complete process: authenticate and scrape a specific site
        """
        print(f"Starting to scrape {site_config['name']}")
        
        # Authenticate if required
        if 'auth_type' in site_config:
            if not self.setup_driver():
                print("Failed to setup driver")
                return False
                
            if not self.authenticate(site_config):
                print("Authentication failed")
                return False
        else:
            # For non-authenticated sites, just set up session
            self.setup_driver()
        
        # Scrape the target pages
        success_count = 0
        for page_url in site_config['pages_to_scrape']:
            print(f"Scraping: {page_url}")
            
            soup = self.scrape_page(page_url, 'auth_type' in site_config)
            if soup:
                extracted_data = self.extract_data(soup, extraction_rules)
                if extracted_data:
                    self.store_data(extracted_data)
                    success_count += 1
                else:
                    print(f"No data extracted from {page_url}")
            else:
                print(f"Failed to scrape {page_url}")
        
        print(f"Successfully scraped {success_count} pages from {site_config['name']}")
        return success_count > 0
    
    def close(self):
        """
        Close the scraper and clean up resources
        """
        if self.driver:
            self.driver.quit()
        if self.data_handler:
            self.data_handler.close_connection()
        print("Scraper closed")

# Example usage
if __name__ == "__main__":
    # Example configuration for a site requiring authentication
    authenticated_site = {
        'name': 'example_auth_site',
        'url': 'https://httpbin.org/forms/post',  # Example login page
        'auth_type': 'form',
        'selectors': {
            'username_field': 'input[name="custname"]',  # Example selector
            'password_field': 'input[name="custemail"]',  # Example selector
            'login_button': 'button[type="submit"]'  # Example selector
        },
        'pages_to_scrape': [
            'https://httpbin.org/get'  # Example page to scrape after login
        ]
    }
    
    # Example configuration for a public site (no auth)
    public_site = {
        'name': 'example_public_site',
        'pages_to_scrape': [
            'https://quotes.toscrape.com/'
        ]
    }
    
    # Extraction rules
    extraction_rules = {
        'quotes': 'span.text',
        'authors': 'small.author',
        'tags': 'div.tags a.tag'
    }
    
    # Initialize and run scraper
    scraper = WebScraper()
    
    try:
        # Example for public site (no authentication)
        scraper.scrape_site(public_site, extraction_rules)
        
        # Example for authenticated site (you'd need to configure actual selectors)
        # scraper.scrape_site(authenticated_site, extraction_rules)
        
    finally:
        scraper.close()