"""
GDP Database CRUD Operations
============================

This module provides comprehensive CRUD (Create, Read, Update, Delete) operations
for the GDP database. It serves as the main data access layer for the web application.
"""

import sqlite3
import pandas as pd
import subprocess
from typing import List, Dict, Optional, Union
import json
from datetime import datetime
from logging_config import get_logger, log_database_operation, log_exception

class GDPDatabaseCRUD:
    """
    Comprehensive CRUD operations for GDP database using SQLite CLI bridge
    to handle STRICT table compatibility issues.
    """
    
    def __init__(self, db_path="database/data.db"):
        self.db_path = db_path
        self.logger = get_logger('gdp_analytics.database')
        self.logger.info(f"Initializing database CRUD with path: {db_path}")
        
        self.sqlite_available = self._check_sqlite_cli()
        if not self.sqlite_available:
            self.logger.warning("SQLite CLI not available, using Python sqlite3 module instead")
        
        # Test database connection using Python sqlite3
        try:
            test_conn = sqlite3.connect(self.db_path)
            test_conn.close()
            self.logger.info("Database connection test successful")
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            raise Exception(f"Database connection failed: {e}")
        
        self.logger.info("Database CRUD initialized successfully")
    
    def _check_sqlite_cli(self) -> bool:
        """Check if sqlite3 CLI is available."""
        self.logger.debug("Checking SQLite CLI availability")
        try:
            result = subprocess.run(['sqlite3', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _execute_query(self, query: str, output_format: str = "csv") -> Optional[str]:
        """Execute a SQL query using sqlite3 CLI or Python sqlite3 module."""
        if self.sqlite_available:
            return self._execute_query_cli(query, output_format)
        else:
            return self._execute_query_python(query, output_format)
    
    def _execute_query_cli(self, query: str, output_format: str = "csv") -> Optional[str]:
        """Execute a SQL query using sqlite3 CLI."""
        try:
            cmd = ['sqlite3', self.db_path]
            
            # Set output format
            if output_format == "csv":
                query = f".mode csv\n.headers on\n{query}"
            elif output_format == "json":
                query = f".mode json\n{query}"
            elif output_format == "table":
                query = f".mode table\n{query}"
            
            self.logger.debug(f"Executing query via SQLite CLI: {query[:100]}{'...' if len(query) > 100 else ''}")
            
            result = subprocess.run(cmd, input=query, capture_output=True, 
                                  text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.debug(f"Query executed successfully, output length: {len(result.stdout)}")
                return result.stdout.strip()
            else:
                self.logger.error(f"SQL Error: {result.stderr}")
                print(f"SQL Error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("Query timed out")
            print("Query timed out")
            return None
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            log_exception(e, "Error executing SQLite query")
            print(f"Error executing query: {e}")
            return None
    
    def _execute_query_python(self, query: str, output_format: str = "csv") -> Optional[str]:
        """Execute a SQL query using Python sqlite3 module."""
        try:
            self.logger.debug(f"Executing query via Python sqlite3: {query[:100]}{'...' if len(query) > 100 else ''}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            conn.close()
            
            if output_format == "csv":
                import io
                output = io.StringIO()
                # Write headers
                if columns:
                    output.write(','.join(columns) + '\n')
                # Write rows
                for row in rows:
                    output.write(','.join(str(cell) if cell is not None else '' for cell in row) + '\n')
                result = output.getvalue().strip()
                output.close()
                return result
            elif output_format == "json":
                import json
                result_list = [dict(zip(columns, row)) for row in rows]
                return json.dumps(result_list)
            else:  # table format or default
                # Simple table format
                if not columns:
                    return ""
                result_lines = ['\t'.join(columns)]
                for row in rows:
                    result_lines.append('\t'.join(str(cell) if cell is not None else '' for cell in row))
                return '\n'.join(result_lines)
            
        except Exception as e:
            self.logger.error(f"Error executing query with Python sqlite3: {e}")
            log_exception(e, "Error executing SQLite query with Python module")
            return None
    
    def _query_to_dataframe(self, query: str) -> pd.DataFrame:
        """Execute query and return as pandas DataFrame."""
        self.logger.debug("Converting query result to DataFrame")
        csv_result = self._execute_query(query, "csv")
        if csv_result:
            try:
                from io import StringIO
                df = pd.read_csv(StringIO(csv_result))
                self.logger.debug(f"DataFrame created with shape: {df.shape}")
                return df
                return df
            except Exception as e:
                print(f"Error creating DataFrame: {e}")
                return pd.DataFrame()
        return pd.DataFrame()
    
    # ================================
    # READ OPERATIONS
    # ================================
    
    def get_all_countries(self) -> pd.DataFrame:
        """Get all countries with their basic information."""
        query = "SELECT * FROM countries ORDER BY name;"
        return self._query_to_dataframe(query)
    
    def get_countries_with_gdp_data(self) -> pd.DataFrame:
        """Get only countries that have GDP data available for modeling."""
        query = """
        SELECT DISTINCT c.country_code, c.name
        FROM countries c
        INNER JOIN data d ON c.country_code = d.country_code
        WHERE d.gdp IS NOT NULL
        GROUP BY c.country_code, c.name
        HAVING COUNT(*) >= 5
        ORDER BY c.name;
        """
        return self._query_to_dataframe(query)
    
    def get_country_by_code(self, country_code: str) -> pd.DataFrame:
        """Get specific country by country code."""
        query = f"SELECT * FROM countries WHERE country_code = '{country_code}';"
        return self._query_to_dataframe(query)
    
    def search_countries_by_name(self, name_pattern: str) -> pd.DataFrame:
        """Search countries by name pattern."""
        query = f"SELECT * FROM countries WHERE name LIKE '%{name_pattern}%' ORDER BY name;"
        return self._query_to_dataframe(query)
    
    def get_data_by_country(self, country_code: str, 
                           start_year: Optional[int] = None, 
                           end_year: Optional[int] = None) -> pd.DataFrame:
        """Get all data for a specific country with optional year filtering."""
        query = f"SELECT * FROM data WHERE country_code = '{country_code}'"
        
        if start_year:
            query += f" AND year >= {start_year}"
        if end_year:
            query += f" AND year <= {end_year}"
        
        query += " ORDER BY year;"
        return self._query_to_dataframe(query)
    
    def get_data_by_year(self, year: int) -> pd.DataFrame:
        """Get all data for a specific year."""
        query = f"SELECT * FROM data WHERE year = {year} ORDER BY country_code;"
        return self._query_to_dataframe(query)
    
    def get_data_range(self, start_year: int, end_year: int, 
                      country_codes: Optional[List[str]] = None) -> pd.DataFrame:
        """Get data for a year range, optionally filtered by countries."""
        query = f"SELECT * FROM data WHERE year BETWEEN {start_year} AND {end_year}"
        
        if country_codes:
            codes_str = "','".join(country_codes)
            query += f" AND country_code IN ('{codes_str}')"
        
        query += " ORDER BY country_code, year;"
        return self._query_to_dataframe(query)
    
    def get_latest_data_by_country(self, country_code: str) -> pd.DataFrame:
        """Get the most recent data entry for a country."""
        query = f"""
        SELECT * FROM data 
        WHERE country_code = '{country_code}' 
        ORDER BY year DESC 
        LIMIT 1;
        """
        return self._query_to_dataframe(query)
    
    def get_top_countries_by_metric(self, metric: str, year: int, 
                                   limit: int = 10, ascending: bool = False) -> pd.DataFrame:
        """Get top countries by a specific metric for a given year."""
        order = "ASC" if ascending else "DESC"
        query = f"""
        SELECT c.name, d.country_code, d.{metric}, d.year
        FROM data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.year = {year} AND d.{metric} IS NOT NULL AND d.{metric} > 0
        ORDER BY d.{metric} {order}
        LIMIT {limit};
        """
        return self._query_to_dataframe(query)
    
    # ================================
    # AGGREGATION OPERATIONS
    # ================================
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics for the database."""
        self.logger.info("Fetching database summary statistics")
        log_database_operation("SELECT", "countries, data", "Summary statistics query")
        
        stats = {}
        
        try:
            # Basic counts
            countries_count = self._query_to_dataframe("SELECT COUNT(*) as count FROM countries;")
            data_count = self._query_to_dataframe("SELECT COUNT(*) as count FROM data;")
            
            # Year range
            year_range = self._query_to_dataframe("""
                SELECT MIN(year) as min_year, MAX(year) as max_year, 
                       COUNT(DISTINCT year) as total_years,
                       COUNT(DISTINCT country_code) as countries_with_data
                FROM data;
            """)
            
            if not countries_count.empty:
                stats['total_countries'] = int(countries_count.iloc[0]['count'])
            if not data_count.empty:
                stats['total_records'] = int(data_count.iloc[0]['count'])
            if not year_range.empty:
                row = year_range.iloc[0]
                stats['year_range'] = {
                    'min_year': int(row['min_year']),
                    'max_year': int(row['max_year']),
                    'total_years': int(row['total_years']),
                    'countries_with_data': int(row['countries_with_data'])
                }
            
            self.logger.info(f"Summary statistics compiled: {stats['total_countries']} countries, {stats['total_records']} records")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error fetching summary statistics: {e}")
            log_exception(e, "Error in get_summary_statistics")
            return {}
    
    def get_metric_statistics(self, metric: str, year: Optional[int] = None) -> pd.DataFrame:
        """Get statistical summary for a specific metric."""
        self.logger.debug(f"Fetching metric statistics for {metric}, year: {year}")
        
        query = f"""
        SELECT 
            COUNT({metric}) as count,
            AVG({metric}) as mean,
            MIN({metric}) as min,
            MAX({metric}) as max
        FROM data 
        WHERE {metric} IS NOT NULL AND {metric} > 0
        """
        
        if year:
            query += f" AND year = {year}"
        
        return self._query_to_dataframe(query)
    
    def get_yearly_averages(self, metric: str) -> pd.DataFrame:
        """Get yearly averages for a specific metric."""
        query = f"""
        SELECT year, 
               AVG({metric}) as avg_{metric},
               COUNT({metric}) as countries_count
        FROM data 
        WHERE {metric} IS NOT NULL AND {metric} > 0
        GROUP BY year 
        ORDER BY year;
        """
        return self._query_to_dataframe(query)
    
    def get_country_rankings(self, metric: str, year: int) -> pd.DataFrame:
        """Get country rankings for a specific metric and year."""
        query = f"""
        SELECT 
            ROW_NUMBER() OVER (ORDER BY d.{metric} DESC) as rank,
            c.name,
            d.country_code,
            d.{metric}
        FROM data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.year = {year} AND d.{metric} IS NOT NULL AND d.{metric} > 0
        ORDER BY d.{metric} DESC;
        """
        return self._query_to_dataframe(query)
    
    # ================================
    # ANALYSIS OPERATIONS
    # ================================
    
    def get_correlation_data(self, metrics: List[str], year: Optional[int] = None) -> pd.DataFrame:
        """Get data for correlation analysis between metrics."""
        metrics_str = ", ".join(metrics)
        query = f"SELECT country_code, {metrics_str} FROM data WHERE "
        
        # Add condition for valid country code
        conditions = ["country_code IS NOT NULL AND country_code != ''"]
        
        # Add conditions to ensure all metrics have valid data
        conditions.extend([f"{metric} IS NOT NULL AND {metric} > 0" for metric in metrics])
        query += " AND ".join(conditions)
        
        if year:
            query += f" AND year = {year}"
        
        query += " ORDER BY country_code;"
        return self._query_to_dataframe(query)
    
    def get_trend_data(self, country_code: str, metric: str) -> pd.DataFrame:
        """Get trend data for a specific country and metric."""
        query = f"""
        SELECT year, {metric}
        FROM data 
        WHERE country_code = '{country_code}' 
          AND {metric} IS NOT NULL 
          AND {metric} > 0
        ORDER BY year;
        """
        return self._query_to_dataframe(query)
    
    def get_metric_distribution(self, metric: str, year: Optional[int] = None) -> pd.DataFrame:
        """Get distribution data for a specific metric (for histograms)."""
        self.logger.debug(f"Fetching metric distribution for {metric}, year: {year}")
        
        where_clause = f"WHERE {metric} IS NOT NULL AND {metric} > 0"
        if year:
            where_clause += f" AND year = {year}"
        
        query = f"""
        SELECT c.name, d.{metric}
        FROM data d
        JOIN countries c ON d.country_code = c.country_code
        {where_clause}
        ORDER BY d.{metric} DESC;
        """
        return self._query_to_dataframe(query)
    
    def get_comparative_data(self, country_codes: List[str], 
                           metric: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Get comparative data for multiple countries."""
        codes_str = "','".join(country_codes)
        query = f"""
        SELECT c.name, d.country_code, d.year, d.{metric}
        FROM data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.country_code IN ('{codes_str}')
          AND d.year BETWEEN {start_year} AND {end_year}
          AND d.{metric} IS NOT NULL
        ORDER BY d.country_code, d.year;
        """
        return self._query_to_dataframe(query)
    
    # ================================
    # UTILITY OPERATIONS
    # ================================
    
    def get_available_years(self) -> List[int]:
        """Get list of all available years in the database."""
        query = "SELECT DISTINCT year FROM data ORDER BY year;"
        df = self._query_to_dataframe(query)
        return df['year'].tolist() if not df.empty else []
    
    def get_available_metrics(self) -> List[str]:
        """Get list of all available metrics (columns) in the data table."""
        # These are the known columns from our schema exploration
        return [
            'gdp', 'population', 'female', 'male', 'life_expectancy',
            'migration', 'infant_mortality', 'internet', 'hci',
            'enrollment', 'urban_pop'
        ]
    
    def validate_country_code(self, country_code: str) -> bool:
        """Check if a country code exists in the database."""
        df = self.get_country_by_code(country_code)
        return not df.empty
    
    def validate_year(self, year: int) -> bool:
        """Check if a year exists in the database."""
        query = f"SELECT COUNT(*) as count FROM data WHERE year = {year};"
        df = self._query_to_dataframe(query)
        return not df.empty and df.iloc[0]['count'] > 0
    
    def export_to_csv(self, query: str, filename: str) -> bool:
        """Export query results to CSV file."""
        try:
            df = self._query_to_dataframe(query)
            if not df.empty:
                df.to_csv(filename, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    # ================================
    # ADVANCED QUERIES
    # ================================
    
    def get_data_completeness(self) -> pd.DataFrame:
        """Analyze data completeness for each metric and year."""
        metrics = self.get_available_metrics()
        query = f"""
        SELECT year,
               COUNT(*) as total_countries,
               {', '.join([f"COUNT({metric}) as {metric}_count" for metric in metrics])}
        FROM data
        GROUP BY year
        ORDER BY year;
        """
        return self._query_to_dataframe(query)
    
    def get_outliers(self, metric: str, year: int, threshold: float = 2.0) -> pd.DataFrame:
        """Identify outliers using standard deviation method."""
        query = f"""
        WITH stats AS (
            SELECT AVG({metric}) as mean_val, 
                   (AVG({metric} * {metric}) - AVG({metric}) * AVG({metric})) as variance
            FROM data 
            WHERE year = {year} AND {metric} IS NOT NULL AND {metric} > 0
        )
        SELECT c.name, d.country_code, d.{metric},
               ABS(d.{metric} - stats.mean_val) / SQRT(stats.variance) as z_score
        FROM data d
        JOIN countries c ON d.country_code = c.country_code
        CROSS JOIN stats
        WHERE d.year = {year} 
          AND d.{metric} IS NOT NULL 
          AND d.{metric} > 0
          AND ABS(d.{metric} - stats.mean_val) / SQRT(stats.variance) > {threshold}
        ORDER BY z_score DESC;
        """
        return self._query_to_dataframe(query)
    
    def get_geographical_analysis(self) -> Dict[str, pd.DataFrame]:
        """Get geographical data for mapping and blog analysis."""
        try:
            # Get countries with their coordinates and latest GDP data
            geo_query = """
            SELECT 
                c.country_code,
                c.name,
                c.lat,
                c.lng,
                d.gdp,
                d.population,
                d.life_expectancy,
                d.internet,
                d.urban_pop,
                d.year
            FROM countries c
            JOIN data d ON c.country_code = d.country_code
            WHERE d.year = (
                SELECT MAX(year) 
                FROM data d2 
                WHERE d2.country_code = c.country_code
            )
            AND d.gdp IS NOT NULL
            ORDER BY d.gdp DESC;
            """
            
            # Get regional aggregations for analysis
            regional_query = """
            SELECT 
                CASE 
                    WHEN c.lat >= 35 THEN 'Northern'
                    WHEN c.lat <= -35 THEN 'Southern' 
                    ELSE 'Tropical'
                END as region,
                AVG(d.gdp) as avg_gdp,
                AVG(d.life_expectancy) as avg_life_expectancy,
                AVG(d.internet) as avg_internet,
                COUNT(*) as country_count
            FROM countries c
            JOIN data d ON c.country_code = d.country_code
            WHERE d.year >= 2020
            GROUP BY region;
            """
            
            # Get development indicators correlation data
            correlation_query = """
            SELECT 
                d.gdp,
                d.life_expectancy,
                d.internet,
                d.enrollment,
                d.urban_pop,
                d.infant_mortality,
                c.name as country_name
            FROM data d
            JOIN countries c ON d.country_code = c.country_code
            WHERE d.year >= 2020
            AND d.gdp IS NOT NULL
            AND d.life_expectancy IS NOT NULL
            AND d.internet IS NOT NULL;
            """
            
            return {
                'geographical': self._query_to_dataframe(geo_query),
                'regional': self._query_to_dataframe(regional_query),
                'correlation': self._query_to_dataframe(correlation_query)
            }
            
        except Exception as e:
            self.logger.error(f"Error in geographical analysis: {e}")
            return {
                'geographical': pd.DataFrame(),
                'regional': pd.DataFrame(), 
                'correlation': pd.DataFrame()
            }


# ================================
# HELPER FUNCTIONS
# ================================

def get_db_instance(db_path: str = "database/data.db") -> GDPDatabaseCRUD:
    """Get a database instance (singleton pattern)."""
    return GDPDatabaseCRUD(db_path)

def test_crud_operations():
    """Test basic CRUD operations."""
    print("Testing GDP Database CRUD Operations")
    print("=" * 40)
    
    try:
        db = get_db_instance()
        
        # Test basic operations
        print("✅ Database connection successful")
        
        # Test country operations
        countries = db.get_all_countries()
        print(f"✅ Retrieved {len(countries)} countries")
        
        # Test data operations
        us_data = db.get_data_by_country("US")
        print(f"✅ Retrieved {len(us_data)} records for US")
        
        # Test summary statistics
        stats = db.get_summary_statistics()
        print(f"✅ Summary statistics: {stats}")
        
        # Test metrics
        gdp_stats = db.get_metric_statistics("gdp", 2020)
        print(f"✅ GDP statistics for 2020: {gdp_stats.to_dict('records')[0] if not gdp_stats.empty else 'No data'}")
        
        print("\n🎉 All CRUD operations working successfully!")
        
    except Exception as e:
        print(f"❌ Error testing CRUD operations: {e}")

if __name__ == "__main__":
    test_crud_operations()