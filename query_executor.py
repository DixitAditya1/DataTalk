import sqlite3
import pandas as pd

class QueryExecutor:
    def __init__(self, db_path):
        """Initialize query executor with database path"""
        self.db_path = db_path
    
    def execute_query(self, sql_query):
        """Execute SQL query and return results as DataFrame"""
        try:
            # Validate query type (only allow SELECT statements)
            if not self._is_safe_query(sql_query):
                raise Exception("Only SELECT queries are allowed for security reasons")
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Execute query and get results
            df = pd.read_sql_query(sql_query, conn)
            
            conn.close()
            return df
            
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        except pd.errors.DatabaseError as e:
            raise Exception(f"Query execution error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def _is_safe_query(self, query):
        """Check if query is safe (only SELECT statements)"""
        # Remove comments and normalize whitespace
        cleaned_query = ' '.join(query.strip().split())
        
        # Convert to lowercase for checking
        query_lower = cleaned_query.lower()
        
        # Check if it starts with SELECT
        if not query_lower.startswith('select'):
            return False
        
        # Check for dangerous keywords
        dangerous_keywords = [
            'insert', 'update', 'delete', 'drop', 'create', 'alter', 
            'truncate', 'replace', 'merge', 'call', 'exec', 'execute',
            'pragma', 'attach', 'detach'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False
        
        return True
    
    def get_table_info(self, table_name):
        """Get information about a specific table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'columns': columns,
                'row_count': row_count
            }
            
        except sqlite3.Error as e:
            raise Exception(f"Error getting table info: {str(e)}")
    
    def validate_connection(self):
        """Validate database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except sqlite3.Error:
            return False
