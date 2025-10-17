"""
Advanced Database Access for data.db

This script uses the SQLite command-line tool to access your database
since it has a newer version that supports STRICT tables.
"""

import subprocess
import json
import pandas as pd
import os

class DatabaseCLIAccess:
    def __init__(self, db_path="database/data.db"):
        self.db_path = db_path
        self.sqlite_available = self._check_sqlite_cli()
    
    def _check_sqlite_cli(self):
        """Check if sqlite3 CLI is available."""
        try:
            result = subprocess.run(['sqlite3', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def execute_query(self, query, output_format="csv"):
        """Execute a SQL query using sqlite3 CLI."""
        if not self.sqlite_available:
            print("❌ SQLite CLI not available")
            return None
        
        try:
            cmd = ['sqlite3', self.db_path]
            
            # Set output format
            if output_format == "csv":
                query = f".mode csv\n.headers on\n{query}"
            elif output_format == "json":
                query = f".mode json\n{query}"
            elif output_format == "table":
                query = f".mode table\n{query}"
            
            result = subprocess.run(cmd, input=query, capture_output=True, 
                                  text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"❌ SQL Error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Query timed out")
            return None
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return None
    
    def get_tables(self):
        """Get list of tables."""
        result = self.execute_query(".tables", "table")
        if result:
            return result.split()
        return []
    
    def get_table_info(self, table_name):
        """Get table schema information."""
        query = f".schema {table_name}"
        return self.execute_query(query, "table")
    
    def query_to_dataframe(self, query):
        """Execute query and return as pandas DataFrame."""
        csv_result = self.execute_query(query, "csv")
        if csv_result:
            try:
                from io import StringIO
                df = pd.read_csv(StringIO(csv_result))
                return df
            except Exception as e:
                print(f"❌ Error creating DataFrame: {e}")
                return pd.DataFrame()
        return pd.DataFrame()
    
    def explore_table(self, table_name, limit=10):
        """Explore a table with basic statistics."""
        print(f"\n🔍 Exploring table: {table_name}")
        print("=" * 50)
        
        # Get schema
        schema = self.get_table_info(table_name)
        print("📋 Schema:")
        print(schema)
        
        # Get row count
        count_query = f"SELECT COUNT(*) as total_rows FROM {table_name};"
        count_result = self.execute_query(count_query, "csv")
        if count_result:
            lines = count_result.strip().split('\n')
            if len(lines) > 1:
                print(f"\n📊 Total rows: {lines[1]}")
        
        # Get sample data
        sample_query = f"SELECT * FROM {table_name} LIMIT {limit};"
        df = self.query_to_dataframe(sample_query)
        
        if not df.empty:
            print(f"\n📋 Sample data (first {limit} rows):")
            print(df.to_string(index=False))
            
            print(f"\n📈 Data types:")
            print(df.dtypes)
        
        return df
    
    def get_countries_summary(self):
        """Get summary of countries data."""
        print("\n🌍 Countries Summary")
        print("=" * 30)
        
        # Total countries
        df = self.query_to_dataframe("SELECT COUNT(*) as total_countries FROM countries;")
        if not df.empty:
            print(f"Total countries: {df.iloc[0]['total_countries']}")
        
        # Sample countries
        sample_df = self.query_to_dataframe("SELECT * FROM countries LIMIT 5;")
        if not sample_df.empty:
            print("\nSample countries:")
            print(sample_df.to_string(index=False))
        
        return sample_df
    
    def get_data_summary(self):
        """Get summary of main data table."""
        print("\n📊 Data Summary")
        print("=" * 20)
        
        # Year range
        year_df = self.query_to_dataframe("""
            SELECT MIN(year) as min_year, MAX(year) as max_year, 
                   COUNT(DISTINCT year) as total_years,
                   COUNT(DISTINCT country_code) as total_countries
            FROM data;
        """)
        
        if not year_df.empty:
            row = year_df.iloc[0]
            print(f"Year range: {row['min_year']} - {row['max_year']}")
            print(f"Total years: {row['total_years']}")
            print(f"Countries with data: {row['total_countries']}")
        
        # Sample data
        sample_df = self.query_to_dataframe("SELECT * FROM data LIMIT 5;")
        if not sample_df.empty:
            print("\nSample data:")
            print(sample_df.to_string(index=False))
        
        return sample_df
    
    def custom_query(self, query):
        """Execute a custom query and display results."""
        print(f"\n🔍 Executing: {query}")
        print("=" * 50)
        
        df = self.query_to_dataframe(query)
        if not df.empty:
            print(df.to_string(index=False))
            return df
        else:
            print("No results or error occurred.")
            return pd.DataFrame()


def main():
    """Main exploration function."""
    print("🗄️ Advanced Database Explorer")
    print("=" * 40)
    
    db = DatabaseCLIAccess()
    
    if not db.sqlite_available:
        print("❌ SQLite CLI not available. Please install SQLite.")
        return
    
    # Get tables
    tables = db.get_tables()
    print(f"📋 Tables found: {tables}")
    
    # Explore each table
    for table in tables:
        db.explore_table(table)
    
    # Specific summaries
    db.get_countries_summary()
    db.get_data_summary()
    
    print("\n💡 You can now use the DatabaseCLIAccess class to run custom queries!")
    print("Example usage:")
    print("  db = DatabaseCLIAccess()")
    print("  df = db.query_to_dataframe('SELECT * FROM countries WHERE country_code = \"US\";')")
    print("  db.custom_query('SELECT country_code, AVG(gdp) FROM data GROUP BY country_code LIMIT 10;')")

if __name__ == "__main__":
    main()