# example_usage.py
from main_scraper import MainScraper
import logging

def example_usage():
    """
    Example of how to use the web scraper with authentication and SQLite storage
    """
    print("Creating web scraper with SQLite storage...")
    
    # Initialize the main scraper
    scraper = MainScraper()
    
    try:
        # Setup the scraper (connects to SQLite)
        if not scraper.setup():
            print("Failed to setup scraper")
            return

        print("Setup completed successfully!")
        
        # Define a simple scraping job for a public site
        public_site_config = {
            'name': 'quotes_example',
            'auth_required': False,
            'target_urls': ['https://quotes.toscrape.com/'],
            'extraction_rules': {
                'quotes': 'span.text',
                'authors': 'small.author',
                'tags': 'div.tags a.tag'
            }
        }
        
        print("Starting to scrape public site...")
        scraper.run_scraping_job(public_site_config)
        print("Public site scraping completed!")
        
        # Example of an authenticated site configuration (requires real credentials to work)
        # This is a template - you would need to fill in actual URLs and selectors
        auth_site_config = {
            'name': 'authenticated_example',
            'auth_required': True,
            'auth_type': 'form',  # or 'session', 'token'
            'login_url': 'https://example.com/login',  # Replace with actual login URL
            'target_urls': ['https://example.com/dashboard'],  # Replace with actual URLs to scrape
            'extraction_rules': {
                'content': '.content-class',
                'title': 'h1'
            },
            'selectors': {
                'username_field': 'input#username',  # Replace with actual selector
                'password_field': 'input#password',  # Replace with actual selector
                'login_button': 'button[type="submit"]'  # Replace with actual selector
            }
        }
        
        print("Example configuration for authenticated site prepared.")
        print("(Note: This would require actual credentials and valid selectors to work)")
        
        # Show storage statistics
        stats = scraper.get_storage_stats()
        if stats:
            print(f"\nStorage Statistics:")
            print(f"Size: {stats['size']} bytes")
            print(f"Count: {stats['count']} records")
            print(f"Capped: {stats['capped']}")
            print(f"File Size: {stats['file_size']} bytes")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"Error in example usage: {e}")
    
    finally:
        # Clean up resources
        scraper.close()
        print("\nScraper has been shut down.")

if __name__ == "__main__":
    example_usage()