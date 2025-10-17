"""
GDP Database Analysis Examples

This script demonstrates how to work with your GDP database
using the advanced database access methods.
"""

from advanced_db_access import DatabaseCLIAccess
import pandas as pd

def analyze_gdp_trends():
    """Analyze GDP trends over time."""
    print("📈 GDP Trends Analysis")
    print("=" * 30)
    
    db = DatabaseCLIAccess()
    
    # Get average GDP by year
    query = """
    SELECT year, AVG(gdp) as avg_gdp, COUNT(*) as countries_count
    FROM data 
    WHERE gdp > 0
    GROUP BY year 
    ORDER BY year;
    """
    
    df = db.query_to_dataframe(query)
    if not df.empty:
        print("Average GDP by Year (last 10 years):")
        print(df.tail(10).to_string(index=False))
    
    return df

def top_countries_by_gdp(year=2023, limit=10):
    """Get top countries by GDP for a specific year."""
    print(f"\n🏆 Top {limit} Countries by GDP in {year}")
    print("=" * 40)
    
    db = DatabaseCLIAccess()
    
    query = f"""
    SELECT c.name, d.country_code, d.gdp, d.population
    FROM data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.year = {year} AND d.gdp > 0
    ORDER BY d.gdp DESC
    LIMIT {limit};
    """
    
    df = db.query_to_dataframe(query)
    if not df.empty:
        print(df.to_string(index=False))
    else:
        print(f"No data found for year {year}")
    
    return df

def life_expectancy_analysis():
    """Analyze life expectancy trends."""
    print("\n🏥 Life Expectancy Analysis")
    print("=" * 35)
    
    db = DatabaseCLIAccess()
    
    # Countries with highest life expectancy in latest year
    query = """
    SELECT c.name, d.country_code, d.year, d.life_expectancy
    FROM data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.year = (SELECT MAX(year) FROM data WHERE life_expectancy > 0)
      AND d.life_expectancy > 0
    ORDER BY d.life_expectancy DESC
    LIMIT 10;
    """
    
    df = db.query_to_dataframe(query)
    if not df.empty:
        print("Top 10 Countries by Life Expectancy (Latest Year):")
        print(df.to_string(index=False))
    
    return df

def country_profile(country_code):
    """Get complete profile for a specific country."""
    print(f"\n🌍 Country Profile: {country_code}")
    print("=" * 40)
    
    db = DatabaseCLIAccess()
    
    # Basic country info
    country_query = f"""
    SELECT name, lat, lng
    FROM countries 
    WHERE country_code = '{country_code}';
    """
    
    country_df = db.query_to_dataframe(country_query)
    if not country_df.empty:
        country_info = country_df.iloc[0]
        print(f"Name: {country_info['name']}")
        print(f"Coordinates: {country_info['lat']}, {country_info['lng']}")
    
    # Latest data
    data_query = f"""
    SELECT year, gdp, population, life_expectancy, internet, urban_pop
    FROM data 
    WHERE country_code = '{country_code}'
    ORDER BY year DESC
    LIMIT 5;
    """
    
    data_df = db.query_to_dataframe(data_query)
    if not data_df.empty:
        print("\nLatest 5 Years Data:")
        print(data_df.to_string(index=False))
    
    return country_df, data_df

def internet_penetration_analysis():
    """Analyze internet penetration rates."""
    print("\n🌐 Internet Penetration Analysis")
    print("=" * 40)
    
    db = DatabaseCLIAccess()
    
    query = """
    SELECT c.name, d.country_code, d.year, d.internet
    FROM data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.year = (SELECT MAX(year) FROM data WHERE internet > 0)
      AND d.internet > 0
    ORDER BY d.internet DESC
    LIMIT 15;
    """
    
    df = db.query_to_dataframe(query)
    if not df.empty:
        print("Top 15 Countries by Internet Penetration (Latest Year):")
        print(df.to_string(index=False))
    
    return df

def custom_analysis_examples():
    """Show examples of custom analysis queries."""
    print("\n🔍 Custom Analysis Examples")
    print("=" * 35)
    
    db = DatabaseCLIAccess()
    
    # Example 1: Countries with declining population
    print("1. Countries with Population Decline (2020-2023):")
    query1 = """
    SELECT c.name, 
           d1.population as pop_2020,
           d2.population as pop_2023,
           (d2.population - d1.population) as change
    FROM data d1
    JOIN data d2 ON d1.country_code = d2.country_code
    JOIN countries c ON d1.country_code = c.country_code
    WHERE d1.year = 2020 AND d2.year = 2023
      AND d1.population > 0 AND d2.population > 0
      AND d2.population < d1.population
    ORDER BY change
    LIMIT 10;
    """
    
    df1 = db.query_to_dataframe(query1)
    if not df1.empty:
        print(df1.to_string(index=False))
    
    # Example 2: Countries with high GDP but low internet
    print("\n2. High GDP, Low Internet Countries (Latest Year):")
    query2 = """
    SELECT c.name, d.gdp, d.internet
    FROM data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.year = (SELECT MAX(year) FROM data WHERE gdp > 0 AND internet >= 0)
      AND d.gdp > 10000  -- High GDP threshold
      AND d.internet < 50  -- Low internet threshold
    ORDER BY d.gdp DESC;
    """
    
    df2 = db.query_to_dataframe(query2)
    if not df2.empty:
        print(df2.to_string(index=False))
    else:
        print("No countries match the criteria")

def main():
    """Run all analysis examples."""
    print("🗄️ GDP Database Analysis Suite")
    print("=" * 50)
    
    # Run various analyses
    analyze_gdp_trends()
    top_countries_by_gdp()
    life_expectancy_analysis()
    internet_penetration_analysis()
    
    # Example country profiles
    country_profile("US")  # United States
    country_profile("CN")  # China
    
    # Custom analyses
    custom_analysis_examples()
    
    print("\n" + "=" * 50)
    print("💡 Analysis Complete!")
    print("You can modify these functions or create new ones for your specific needs.")
    print("\nTo use these functions in your own code:")
    print("  from gdp_analysis import top_countries_by_gdp, country_profile")
    print("  top_countries_by_gdp(2022, 15)")
    print("  country_profile('DE')")

if __name__ == "__main__":
    main()