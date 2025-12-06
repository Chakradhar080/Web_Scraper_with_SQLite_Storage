# data_handler.py
import json
import logging
from datetime import datetime
from sqlite_db_utils import SQLiteManager
from scraper_config import DB_PATH
from data_exporter import DataExporter
import hashlib

class DataHandler:
    def __init__(self):
        self.sqlite_manager = SQLiteManager(db_path=DB_PATH)
        # SQLite has a 1TB size limit by default, no application-level size limit

    def connect_to_db(self):
        """
        Connect to SQLite database and set up table
        """
        return self.sqlite_manager.connect()

    def validate_data(self, data):
        """
        Validate scraped data before storing

        Args:
            data: Dictionary containing scraped data
        """
        if not isinstance(data, dict):
            logging.error("Data must be a dictionary")
            return False, "Data must be a dictionary"

        # Validate data types
        for key, value in data.items():
            # Ensure values are of acceptable types that can be JSON serialized
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                error_msg = f"Invalid data type for key '{key}': {type(value)}"
                logging.error(error_msg)
                return False, error_msg

        return True, "Valid"

    def clean_data(self, data):
        """
        Clean and preprocess data before storage

        Args:
            data: Dictionary containing scraped data
        """
        cleaned_data = {}

        for key, value in data.items():
            if isinstance(value, list):
                # Clean each item in the list
                cleaned_list = []
                for item in value:
                    if isinstance(item, str):
                        # Remove extra whitespace and clean string
                        cleaned_item = item.strip()
                        if cleaned_item:  # Only add non-empty strings
                            cleaned_list.append(cleaned_item)
                    else:
                        cleaned_list.append(item)

                # Only add the list if it's not empty
                if cleaned_list:
                    cleaned_data[key] = cleaned_list
            elif isinstance(value, str):
                # Clean string values
                cleaned_str = value.strip()
                if cleaned_str:  # Only add non-empty strings
                    cleaned_data[key] = cleaned_str
            elif value is not None:  # Add non-empty non-string values
                cleaned_data[key] = value

        # Add a hash of the content to avoid duplicates
        # Use our serialization helper to handle datetime objects
        serializable_data = self._prepare_for_serialization(cleaned_data)
        content_str = json.dumps(serializable_data, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
        cleaned_data['content_hash'] = content_hash

        return cleaned_data

    def _prepare_for_serialization(self, obj):
        """
        Recursively convert non-serializable objects (like datetime) to serializable ones
        """
        if isinstance(obj, dict):
            return {key: self._prepare_for_serialization(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_serialization(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO string format
        else:
            return obj

    def store_scraped_data(self, data):
        """
        Store scraped data in SQLite with validation and cleaning

        Args:
            data: Dictionary containing scraped data
        """
        # Clean the data first
        cleaned_data = self.clean_data(data)

        # Validate the cleaned data
        is_valid, validation_message = self.validate_data(cleaned_data)

        if not is_valid:
            logging.error(f"Data validation failed: {validation_message}")
            return None

        # Store data in SQLite
        try:
            result_id = self.sqlite_manager.insert_data(cleaned_data)
            if result_id is not None:
                logging.info(f"Successfully stored data with ID: {result_id}")

            # Log table stats
            stats = self.sqlite_manager.get_table_stats()
            if stats:
                logging.info(f"Table stats - Size: {stats['size']} bytes, Count: {stats['count']} records")

            return result_id
        except Exception as e:
            logging.error(f"Error storing data in SQLite: {e}")
            return None

    def bulk_store_data(self, data_list):
        """
        Store multiple records at once

        Args:
            data_list: List of dictionaries containing scraped data
        """
        valid_records = []

        for data in data_list:
            cleaned_data = self.clean_data(data)
            is_valid, validation_message = self.validate_data(cleaned_data)

            if is_valid:
                valid_records.append(cleaned_data)
            else:
                logging.error(f"Skipping invalid document: {validation_message}")

        if not valid_records:
            logging.info("No valid documents to store")
            return 0

        try:
            result_count = self.sqlite_manager.bulk_insert(valid_records)
            logging.info(f"Successfully bulk stored {result_count} records")

            # Log table stats
            stats = self.sqlite_manager.get_table_stats()
            if stats:
                logging.info(f"Table stats - Size: {stats['size']} bytes, Count: {stats['count']} records")

            return result_count
        except Exception as e:
            logging.error(f"Error in bulk storage: {e}")
            return 0

    def get_storage_stats(self):
        """
        Get current statistics about the storage
        """
        return self.sqlite_manager.get_table_stats()

    def export_data(self, format_type='json', filters=None):
        """
        Export scraped data to file

        Args:
            format_type: Export format ('json', 'csv', or 'txt')
            filters: Optional filters for querying data
        """
        try:
            exporter = DataExporter()
            file_path = exporter.export_from_db(self.sqlite_manager, filters=filters, format_type=format_type)
            if file_path:
                logging.info(f"Data exported to: {file_path}")
                return file_path
            else:
                logging.error("Failed to export data")
                return None
        except Exception as e:
            logging.error(f"Error in export_data: {e}")
            return None

    def close_connection(self):
        """
        Close SQLite connection
        """
        self.sqlite_manager.close_connection()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)