# sqlite_db_utils.py
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

class SQLiteManager:
    def __init__(self, db_path='scraping_data.db'):
        self.db_path = db_path
        self.connection = None
        # SQLite has a 1TB size limit by default, no application-level size limit

    def connect(self):
        """
        Establish connection to SQLite database
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self.setup_table()
            print(f"Connected to SQLite database successfully: {self.db_path}")
            return True
        except Exception as e:
            print(f"Error connecting to SQLite database: {e}")
            return False

    def setup_table(self):
        """
        Create table for storing scraped data if it doesn't exist
        """
        try:
            cursor = self.connection.cursor()
            
            # Create table with necessary fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,  -- JSON string of the actual data
                    content_hash TEXT UNIQUE,  -- For duplicate detection
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source_url TEXT,
                    site_name TEXT
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON scraped_data(content_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON scraped_data(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_url ON scraped_data(source_url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_site_name ON scraped_data(site_name)')
            
            self.connection.commit()
            print(f"Table 'scraped_data' created or already exists in {self.db_path}")
            return True
        except Exception as e:
            print(f"Error creating table: {e}")
            return False

    def insert_data(self, data):
        """
        Insert data into the database
        """
        try:
            cursor = self.connection.cursor()
            
            # Convert the data dictionary to JSON string for storage
            data_json = json.dumps(data, default=str)  # default=str handles non-serializable objects
            
            cursor.execute('''
                INSERT INTO scraped_data (data, content_hash, timestamp, source_url, site_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data_json,
                data.get('content_hash', ''),
                data.get('timestamp', datetime.utcnow().isoformat()),
                data.get('source_url', ''),
                data.get('site_name', '')
            ))
            
            self.connection.commit()
            inserted_id = cursor.lastrowid
            return inserted_id
        except sqlite3.IntegrityError:
            # This happens when content_hash already exists (duplicate)
            logging.info("Duplicate content detected, skipping storage")
            return None
        except Exception as e:
            logging.error(f"Error inserting data: {e}")
            return None

    def bulk_insert(self, data_list):
        """
        Insert multiple records at once
        """
        try:
            if not data_list:
                return 0
                
            cursor = self.connection.cursor()
            inserted_count = 0
            
            for data in data_list:
                try:
                    # Convert the data dictionary to JSON string for storage
                    data_json = json.dumps(data, default=str)
                    
                    cursor.execute('''
                        INSERT INTO scraped_data (data, content_hash, timestamp, source_url, site_name)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        data_json,
                        data.get('content_hash', ''),
                        data.get('timestamp', datetime.utcnow().isoformat()),
                        data.get('source_url', ''),
                        data.get('site_name', '')
                    ))
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    # This happens when content_hash already exists (duplicate)
                    continue
                except Exception as e:
                    logging.error(f"Error inserting individual data during bulk insert: {e}")
            
            self.connection.commit()
            return inserted_count
        except Exception as e:
            logging.error(f"Error in bulk insert: {e}")
            return 0

    def get_table_stats(self):
        """
        Get statistics about the scraped_data table
        """
        try:
            cursor = self.connection.cursor()

            # Get count of records
            cursor.execute("SELECT COUNT(*) FROM scraped_data")
            count = cursor.fetchone()[0]

            # Get estimated size by calculating the size of all stored data
            cursor.execute("SELECT SUM(LENGTH(data)) FROM scraped_data")
            result = cursor.fetchone()[0]
            size = result if result else 0  # Handle case where table is empty

            # Get file size
            db_file_size = Path(self.db_path).stat().st_size

            return {
                'size': size,
                'count': count,
                'capped': False,  # SQLite doesn't have capped collections like MongoDB
                'file_size': db_file_size,
                'database_path': self.db_path
            }
        except Exception as e:
            logging.error(f"Error getting table stats: {e}")
            return None

    def query_data(self, limit=None, offset=0, filters=None):
        """
        Query data from the database with optional filters and pagination
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)
            filters: Dictionary with filter conditions
        """
        try:
            cursor = self.connection.cursor()
            
            query = "SELECT * FROM scraped_data WHERE 1=1"
            params = []
            
            if filters:
                for key, value in filters.items():
                    if key in ['source_url', 'site_name']:
                        query += f" AND {key} LIKE ?"
                        params.append(f"%{value}%")
                    elif key == 'content_hash':
                        query += " AND content_hash = ?"
                        params.append(value)
            
            query += " ORDER BY timestamp DESC"
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            results = []
            for row in rows:
                data_row = dict(row)
                # Parse the JSON data string back to dictionary
                try:
                    data_row['data'] = json.loads(data_row['data'])
                except json.JSONDecodeError:
                    data_row['data'] = data_row['data']  # Keep as string if JSON parsing fails
                results.append(data_row)
            
            return results
        except Exception as e:
            logging.error(f"Error querying data: {e}")
            return []

    def close_connection(self):
        """
        Close the SQLite connection
        """
        if self.connection:
            self.connection.close()
            print("SQLite connection closed")

    def cleanup_old_data(self, days_to_keep=30):
        """
        Remove data older than specified number of days
        
        Args:
            days_to_keep: Number of days to keep data (default 30)
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                DELETE FROM scraped_data 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days_to_keep))
            
            deleted_count = cursor.rowcount
            self.connection.commit()
            
            print(f"Cleaned up {deleted_count} old records")
            return deleted_count
        except Exception as e:
            logging.error(f"Error cleaning up old data: {e}")
            return 0