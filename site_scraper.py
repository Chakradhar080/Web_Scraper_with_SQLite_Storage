# site_scraper.py
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from auth_manager import AuthManager
import logging


class SiteScraper:
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.auth_manager = AuthManager()

    def setup_driver(self):
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

    def scrape_public_site(self, url, extraction_rules):
        """
        Scrape a public site without authentication

        Args:
            url: URL to scrape
            extraction_rules: Dictionary with CSS selectors for data extraction

        Returns:
            Dictionary containing extracted data
        """
        try:
            # Handle special cases for different sites
            if 'github.com' in url:
                return self._scrape_github_repo(url, extraction_rules)
            elif 'nvd.nist.gov' in url:
                return self._scrape_nvd(url, extraction_rules)
            elif 'gtfobins.github.io' in url:
                return self._scrape_gtfo_bins(url, extraction_rules)
            elif 'attack.mitre.org' in url:
                return self._scrape_mitre_attack(url, extraction_rules)
            elif 'exploit-db.com' in url:
                return self._scrape_exploit_db(url, extraction_rules)
            elif 'hackerone.com' in url:
                return self._scrape_hackerone(url, extraction_rules)
            else:
                response = self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._extract_data(soup, extraction_rules)
        except Exception as e:
            logging.error(f"Error scraping public site {url}: {e}")
            return {}

    def _scrape_github_repo(self, url, extraction_rules):
        """
        Specialized scraping function for GitHub repositories
        """
        try:
            import json
            # For GitHub, we can use the GitHub API to get repository contents
            repo_path = url.replace('https://github.com/', '')
            api_url = f'https://api.github.com/repos/{repo_path}'

            # Get repository info
            response = self.session.get(api_url)
            if response.status_code == 200:
                repo_data = response.json()
                result = {
                    'repository_info': {
                        'name': repo_data.get('name'),
                        'full_name': repo_data.get('full_name'),
                        'description': repo_data.get('description'),
                        'stars': repo_data.get('stargazers_count'),
                        'forks': repo_data.get('forks_count'),
                        'language': repo_data.get('language'),
                        'created_at': repo_data.get('created_at'),
                        'updated_at': repo_data.get('updated_at'),
                        'clone_url': repo_data.get('clone_url')
                    }
                }

                # Also get repository contents using GitHub API
                contents_url = f'https://api.github.com/repos/{repo_path}/contents'
                contents_response = self.session.get(contents_url)

                if contents_response.status_code == 200:
                    contents = contents_response.json()
                    files = []
                    folders = []

                    for item in contents:
                        if item['type'] == 'file':
                            files.append({
                                'name': item['name'],
                                'path': item['path'],
                                'size': item.get('size', 0),
                                'download_url': item.get('download_url'),
                                'sha': item.get('sha')
                            })
                        elif item['type'] == 'dir':
                            folders.append({
                                'name': item['name'],
                                'path': item['path'],
                                'url': item['url'],
                                'sha': item.get('sha')
                            })

                    result['files'] = files
                    result['folders'] = folders

                # Get the README content
                readme_url = f'https://api.github.com/repos/{repo_path}/readme'
                readme_response = self.session.get(readme_url)

                if readme_response.status_code == 200:
                    readme_data = readme_response.json()
                    import base64
                    readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
                    result['readme'] = readme_content

                return result
            else:
                # Fallback to HTML scraping if API fails
                response = self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._extract_data(soup, extraction_rules)

        except Exception as e:
            logging.error(f"Error scraping GitHub repo {url}: {e}")
            # Fallback to regular scraping
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_data(soup, extraction_rules)

    def _scrape_nvd(self, url, extraction_rules):
        """
        Specialized scraping function for NVD
        """
        try:
            # NVD has a public API that's better to use
            if 'vuln/search' in url or 'vuln/full-listing' in url:
                # For demonstration, use regular scraping
                response = self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._extract_data(soup, extraction_rules)
            else:
                response = self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._extract_data(soup, extraction_rules)
        except Exception as e:
            logging.error(f"Error scraping NVD {url}: {e}")
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_data(soup, extraction_rules)

    def _scrape_gtfo_bins(self, url, extraction_rules):
        """
        Specialized scraping function for GTFOBins
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract binaries and their functions
            bins = []
            binary_elements = soup.select('.binary')

            for binary in binary_elements:
                bin_name = binary.select_one('a')
                if bin_name:
                    bin_data = {
                        'name': bin_name.text.strip(),
                        'url': url + bin_name.get('href', '') if bin_name.get('href', '').startswith('/') else bin_name.get('href', ''),
                        'functions': []
                    }

                    # Extract functions for this binary
                    func_elements = binary.select('.func a')
                    for func in func_elements:
                        bin_data['functions'].append({
                            'name': func.text.strip(),
                            'url': func.get('href', '')
                        })

                    bins.append(bin_data)

            result = {'bins': bins}

            # Add any other extracted data using the rules
            other_data = self._extract_data(soup, extraction_rules)
            result.update(other_data)

            return result
        except Exception as e:
            logging.error(f"Error scraping GTFOBins {url}: {e}")
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_data(soup, extraction_rules)

    def _scrape_mitre_attack(self, url, extraction_rules):
        """
        Specialized scraping function for MITRE ATT&CK
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract techniques, tactics, groups, or software based on URL
            result = {}

            if '/techniques/' in url:
                techniques = []
                technique_elements = soup.select('.technique-cell a')
                for tech in technique_elements:
                    techniques.append({
                        'name': tech.text.strip(),
                        'url': tech.get('href', '')
                    })
                result['techniques'] = techniques
            elif '/tactics/' in url:
                tactics = []
                tactic_elements = soup.select('.tactic-cell a')
                for tactic in tactic_elements:
                    tactics.append({
                        'name': tactic.text.strip(),
                        'url': tactic.get('href', '')
                    })
                result['tactics'] = tactics

            # Add any other extracted data using the rules
            other_data = self._extract_data(soup, extraction_rules)
            result.update(other_data)

            return result
        except Exception as e:
            logging.error(f"Error scraping MITRE ATT&CK {url}: {e}")
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_data(soup, extraction_rules)

    def _scrape_exploit_db(self, url, extraction_rules):
        """
        Specialized scraping function for Exploit-DB
        """
        try:
            # Set proper headers to avoid being blocked
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract exploits information
            exploits = []

            # Look for exploit table rows
            exploit_rows = soup.select('.exploit_table tr:not(:first-child)')  # Skip header row

            for row in exploit_rows:
                cells = row.select('td')
                if len(cells) >= 6:  # Make sure we have enough cells
                    exploit_info = {
                        'date': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                        'type': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                        'platform': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                        'title': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                        'author': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                        'description': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                    }
                    # Extract URL if available
                    title_link = cells[3].find('a') if len(cells) > 3 else None
                    if title_link:
                        exploit_info['url'] = title_link.get('href')

                    exploits.append(exploit_info)

            result = {'exploits': exploits}

            # Add any other extracted data using the rules
            other_data = self._extract_data(soup, extraction_rules)
            result.update(other_data)

            return result
        except Exception as e:
            logging.error(f"Error scraping Exploit-DB {url}: {e}")
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_data(soup, extraction_rules)

    def _scrape_hackerone(self, url, extraction_rules):
        """
        Specialized scraping function for HackerOne Hacktivity
        """
        try:
            # Set proper headers to avoid being blocked
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

            response = self.session.get(url)
            response.raise_for_status()

            # For HackerOne, we'll extract JSON data from the page if it's available
            # or do basic HTML scraping
            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find JSON data in script tags
            import re
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'window.initialData' in script.string:
                    # Extract JSON data (this is a simplified example)
                    # In a real implementation, you'd need to parse the JavaScript properly
                    pass

            # Basic scraping for reports
            reports = []
            report_elements = soup.select('.reports-list-item')

            for report in report_elements:
                report_info = {
                    'title': report.select_one('.report-title').get_text(strip=True) if report.select_one('.report-title') else '',
                    'vulnerability_type': report.select_one('.vulnerability-type').get_text(strip=True) if report.select_one('.vulnerability-type') else '',
                    'bounty_amount': report.select_one('.bounty-amount').get_text(strip=True) if report.select_one('.bounty-amount') else '',
                    'disclosure_date': report.select_one('.disclosure-date').get_text(strip=True) if report.select_one('.disclosure-date') else '',
                    'reputation_score': report.select_one('.reputation-score').get_text(strip=True) if report.select_one('.reputation-score') else '',
                }

                # Extract URL if available
                report_link = report.find('a')
                if report_link:
                    report_info['url'] = report_link.get('href')

                reports.append(report_info)

            result = {'reports': reports}

            # Add any other extracted data using the rules
            other_data = self._extract_data(soup, extraction_rules)
            result.update(other_data)

            return result
        except Exception as e:
            logging.error(f"Error scraping HackerOne {url}: {e}")
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_data(soup, extraction_rules)

    def scrape_protected_site(self, login_config, target_urls, extraction_rules):
        """
        Scrape a protected site that requires authentication

        Args:
            login_config: Configuration for authentication
            target_urls: List of URLs to scrape after authentication
            extraction_rules: Dictionary with CSS selectors for data extraction

        Returns:
            Dictionary mapping URLs to extracted data
        """
        # Perform authentication
        if not self.auth_manager.authenticate(login_config):
            logging.error("Authentication failed")
            return {}

        # Update session with authentication cookies after login
        self.session.cookies.update(self.auth_manager.get_session_cookies())

        scraped_data = {}
        for url in target_urls:
            try:
                response = self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                scraped_data[url] = self._extract_data(soup, extraction_rules)
            except Exception as e:
                logging.error(f"Error scraping protected site {url}: {e}")
                scraped_data[url] = {}

        return scraped_data

    def scrape_with_selenium(self, url, extraction_rules, wait_for_element=None):
        """
        Scrape a site using Selenium for JavaScript-rendered content

        Args:
            url: URL to scrape
            extraction_rules: Dictionary with CSS selectors for data extraction
            wait_for_element: Optional CSS selector to wait for before scraping

        Returns:
            Dictionary containing extracted data
        """
        if not self.driver:
            if not self.setup_driver():
                return {}

        try:
            self.driver.get(url)

            # Wait for specific element if provided
            if wait_for_element:
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))

            page_content = self.driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')

            return self._extract_data(soup, extraction_rules)
        except Exception as e:
            logging.error(f"Error scraping with Selenium {url}: {e}")
            return {}

    def _extract_data(self, soup, extraction_rules):
        """
        Extract specific data from the page based on rules

        Args:
            soup: BeautifulSoup object of the page content
            extraction_rules: Dictionary with CSS selectors for data extraction

        Returns:
            Dictionary containing extracted data
        """
        data = {}

        for key, selector in extraction_rules.items():
            try:
                elements = soup.select(selector)
                if elements:
                    # Extract text from all matching elements
                    data[key] = [elem.get_text(strip=True) for elem in elements]
                else:
                    data[key] = []
            except Exception as e:
                logging.error(f"Error extracting data with selector '{selector}' for key '{key}': {e}")
                data[key] = []

        return data

    def close(self):
        """
        Close the scraper and clean up resources
        """
        if self.driver:
            self.driver.quit()
        print("Site scraper closed")