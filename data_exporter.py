# data_exporter.py
import json
import csv
import os
from datetime import datetime
import logging


class DataExporter:
    def __init__(self, export_dir='scraped_data'):
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def export_to_json(self, data_list, filename=None):
        """
        Export data to JSON file

        Args:
            data_list: List of data dictionaries to export
            filename: Optional filename (will generate timestamp-based name if not provided)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.json"

        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, indent=2, ensure_ascii=False, default=str)
            logging.info(f"Data exported to JSON file: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Error exporting data to JSON: {e}")
            return None

    def export_to_csv(self, data_list, filename=None):
        """
        Export data to CSV file

        Args:
            data_list: List of data dictionaries to export
            filename: Optional filename (will generate timestamp-based name if not provided)
        """
        if not data_list:
            logging.warning("No data to export to CSV")
            return None

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.csv"

        filepath = os.path.join(self.export_dir, filename)

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if data_list:
                    # Get all unique keys from all dictionaries
                    fieldnames = set()
                    for item in data_list:
                        fieldnames.update(item.keys())
                    
                    # Sort fieldnames for consistent column order
                    fieldnames = sorted(list(fieldnames))
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data_list)
                    
            logging.info(f"Data exported to CSV file: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Error exporting data to CSV: {e}")
            return None

    def export_to_txt(self, data_list, filename=None):
        """
        Export data to text file

        Args:
            data_list: List of data dictionaries to export
            filename: Optional filename (will generate timestamp-based name if not provided)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.txt"

        filepath = os.path.join(self.export_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for i, data in enumerate(data_list):
                    f.write(f"--- Record {i+1} ---\n")
                    for key, value in data.items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
            logging.info(f"Data exported to TXT file: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Error exporting data to TXT: {e}")
            return None

    def export_from_db(self, sqlite_manager, filters=None, format_type='json'):
        """
        Export data directly from the SQLite database

        Args:
            sqlite_manager: SQLiteManager instance
            filters: Optional filters for querying data
            format_type: Export format ('json', 'csv', or 'txt')
        """
        try:
            # Query all data from the database
            data_list = sqlite_manager.query_data(limit=None, offset=0, filters=filters)
            
            if not data_list:
                logging.warning("No data found in database to export")
                return None

            # Extract the actual data from the JSON strings stored in the db
            processed_data = []
            for row in data_list:
                # Remove the raw 'data' JSON string and work with parsed data
                if 'data' in row and isinstance(row['data'], dict):
                    processed_row = row['data'].copy()
                    processed_row['id'] = row['id']
                    processed_row['timestamp'] = row['timestamp']
                    processed_row['source_url'] = row['source_url']
                    processed_row['site_name'] = row['site_name']
                    processed_data.append(processed_row)
                else:
                    # If 'data' is still a string, parse it
                    processed_data.append(row)

            # Export based on format
            if format_type.lower() == 'json':
                return self.export_to_json(processed_data)
            elif format_type.lower() == 'csv':
                return self.export_to_csv(processed_data)
            elif format_type.lower() == 'txt':
                return self.export_to_txt(processed_data)
            else:
                logging.error(f"Unsupported format type: {format_type}")
                return None

        except Exception as e:
            logging.error(f"Error exporting from database: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Example of how to use the DataExporter
    exporter = DataExporter()
    
    sample_data = [
        {
            "title": "Sample Title",
            "content": "Sample content for testing",
            "url": "https://example.com",
            "date": str(datetime.now())
        }
    ]
    
    # Export to different formats
    json_file = exporter.export_to_json(sample_data)
    csv_file = exporter.export_to_csv(sample_data)
    txt_file = exporter.export_to_txt(sample_data)
    
    print(f"Exported to: {json_file}, {csv_file}, {txt_file}")