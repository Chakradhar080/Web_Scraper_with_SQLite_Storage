# auth_manager.py
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging


class AuthManager:
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.cookies = {}

    def authenticate(self, login_config):
        """
        Authenticate based on configuration

        Args:
            login_config: Dictionary containing authentication configuration

        Returns:
            Boolean indicating success of authentication
        """
        auth_type = login_config.get('auth_type', 'form')

        if auth_type == 'form':
            return self._form_based_auth(login_config)
        elif auth_type == 'session':
            return self._session_based_auth(login_config)
        elif auth_type == 'token':
            return self._token_based_auth(login_config)
        elif auth_type == 'cookie':
            return self._cookie_based_auth(login_config)
        else:
            logging.error(f"Unknown authentication type: {auth_type}")
            return False

    def _form_based_auth(self, login_config):
        """
        Handle form-based authentication
        """
        try:
            if not self.driver:
                self._setup_driver()

            self.driver.get(login_config['login_url'])

            # Wait for login elements to load
            wait = WebDriverWait(self.driver, 10)
            username_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, login_config['selectors']['username_field']))
            )
            password_field = self.driver.find_element(By.CSS_SELECTOR, login_config['selectors']['password_field'])
            login_button = self.driver.find_element(By.CSS_SELECTOR, login_config['selectors']['login_button'])

            # Fill in credentials
            username_field.send_keys(login_config['username'])
            password_field.send_keys(login_config['password'])

            # Click login
            login_button.click()

            # Wait for login to complete
            time.sleep(3)

            # Check if login was successful by checking for a known element on the logged-in page
            # This is a simplified check - you might need to customize based on the site
            current_url = self.driver.current_url
            if current_url != login_config['login_url']:
                print("Form-based authentication successful")
                return True
            else:
                print("Form-based authentication failed - still on login page")
                return False

        except Exception as e:
            logging.error(f"Form-based authentication failed: {e}")
            return False

    def _session_based_auth(self, login_config):
        """
        Handle session-based authentication
        """
        try:
            data_format = login_config.get('data_format', 'form')
            login_data = {
                'username': login_config['username'],
                'password': login_config['password']
            }

            # Send login request
            if data_format == 'json':
                response = self.session.post(login_config['login_url'], json=login_data)
            else:
                response = self.session.post(login_config['login_url'], data=login_data)

            if response.status_code == 200:
                print("Session-based authentication successful")
                return True
            else:
                print("Session-based authentication failed")
                return False
        except Exception as e:
            logging.error(f"Session-based authentication failed: {e}")
            return False

    def _token_based_auth(self, login_config):
        """
        Handle token-based authentication
        """
        try:
            # Get token
            headers = {'Content-Type': 'application/json'}
            auth_data = {
                'username': login_config['username'],
                'password': login_config['password']
            }

            response = self.session.post(login_config['auth_url'], json=auth_data, headers=headers)

            if response.status_code == 200:
                token_response = response.json()
                token = token_response.get(login_config.get('token_field', 'access_token'))
                self.session.headers.update({'Authorization': f'Bearer {token}'})

                print("Token-based authentication successful")
                return True
            else:
                print("Token-based authentication failed")
                return False
        except Exception as e:
            logging.error(f"Token-based authentication failed: {e}")
            return False

    def _cookie_based_auth(self, login_config):
        """
        Handle cookie-based authentication
        """
        try:
            # Set cookies directly
            cookies = login_config.get('cookies', {})
            for name, value in cookies.items():
                # This is simplified; actual cookie setting may require different handling depending on the domain
                self.session.cookies.set(name, value)

            print("Cookie-based authentication successful")
            return True
        except Exception as e:
            logging.error(f"Cookie-based authentication failed: {e}")
            return False

    def _setup_driver(self):
        """
        Set up Chrome driver with options
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = webdriver.chrome.service.Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Remove the webdriver property to avoid detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except Exception as e:
            logging.error(f"Error setting up Chrome driver: {e}")
            return False

    def get_session_cookies(self):
        """
        Get cookies from the current session
        """
        if self.driver:
            # Get cookies from Selenium driver
            selenium_cookies = self.driver.get_cookies()
            # Convert to requests cookie format
            for cookie in selenium_cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
        
        return self.session.cookies

    def close(self):
        """
        Close the auth manager and clean up resources
        """
        if self.driver:
            self.driver.quit()
        print("Auth manager closed")