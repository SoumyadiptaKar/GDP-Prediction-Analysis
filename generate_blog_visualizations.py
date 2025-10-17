#!/usr/bin/env python3
"""
Blog Visualization Generator
Creates static visualizations for the research blog using geopandas and matplotlib.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import numpy as np
from database_crud import get_db_instance
import os
from pathlib import Path

def setup_plot_style():
    """Set up consistent plot styling."""
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12

def create_correlation_heatmap(db, output_dir):
    """Create correlation heatmap for social indicators."""
    # Get correlation data
    query = """
    SELECT gdp, population, life_expectancy, internet, 
           hci, enrollment, urban_pop, infant_mortality
    FROM data 
    WHERE year >= 2020 
    AND gdp IS NOT NULL 
    AND life_expectancy IS NOT NULL
    LIMIT 1000;
    """
    
    df = db._query_to_dataframe(query)
    
    # Calculate correlation matrix
    correlation_matrix = df.corr()
    
    # Create heatmap
    plt.figure(figsize=(10, 8))
    mask = np.triu(correlation_matrix)
    sns.heatmap(correlation_matrix, 
                annot=True, 
                cmap='RdBu_r', 
                center=0,
                mask=mask,
                square=True,
                fmt='.2f')
    plt.title('Social Indicators Correlation Matrix\n(Data from 2020 onwards)', 
              fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save plot
    output_path = output_dir / 'correlation_heatmap.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Correlation heatmap saved: {output_path}")
    return output_path

def create_gdp_development_scatter(db, output_dir):
    """Create GDP vs Development indicators scatter plot."""
    query = """
    SELECT c.name, d.gdp, d.life_expectancy, d.internet, 
           d.enrollment, d.urban_pop, d.year
    FROM data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.year >= 2020
    AND d.gdp IS NOT NULL
    AND d.life_expectancy IS NOT NULL
    ORDER BY d.gdp DESC
    LIMIT 200;
    """
    
    df = db._query_to_dataframe(query)
    
    # Create subplot figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('GDP vs Social Development Indicators', fontsize=16, fontweight='bold')
    
    # GDP vs Life Expectancy
    axes[0,0].scatter(df['life_expectancy'], df['gdp'], 
                     alpha=0.7, s=60, color='steelblue')
    axes[0,0].set_xlabel('Life Expectancy (years)')
    axes[0,0].set_ylabel('GDP per Capita ($)')
    axes[0,0].set_title('Life Expectancy vs GDP')
    
    # GDP vs Internet Penetration
    axes[0,1].scatter(df['internet'], df['gdp'], 
                     alpha=0.7, s=60, color='forestgreen')
    axes[0,1].set_xlabel('Internet Penetration (%)')
    axes[0,1].set_ylabel('GDP per Capita ($)')
    axes[0,1].set_title('Internet Access vs GDP')
    
    # GDP vs School Enrollment
    axes[1,0].scatter(df['enrollment'], df['gdp'], 
                     alpha=0.7, s=60, color='orangered')
    axes[1,0].set_xlabel('School Enrollment Rate (%)')
    axes[1,0].set_ylabel('GDP per Capita ($)')
    axes[1,0].set_title('Education vs GDP')
    
    # GDP vs Urbanization
    axes[1,1].scatter(df['urban_pop'], df['gdp'], 
                     alpha=0.7, s=60, color='purple')
    axes[1,1].set_xlabel('Urban Population (%)')
    axes[1,1].set_ylabel('GDP per Capita ($)')
    axes[1,1].set_title('Urbanization vs GDP')
    
    plt.tight_layout()
    
    # Save plot
    output_path = output_dir / 'gdp_development_scatter.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ GDP development scatter saved: {output_path}")
    return output_path

def create_regional_analysis(db, output_dir):
    """Create regional analysis visualization."""
    query = """
    SELECT 
        c.name,
        c.lat,
        c.lng,
        d.gdp,
        d.life_expectancy,
        d.internet,
        CASE 
            WHEN c.lat >= 35 THEN 'Northern'
            WHEN c.lat <= -35 THEN 'Southern' 
            ELSE 'Tropical'
        END as region
    FROM countries c
    JOIN data d ON c.country_code = d.country_code
    WHERE d.year >= 2020
    AND d.gdp IS NOT NULL
    ORDER BY d.gdp DESC;
    """
    
    df = db._query_to_dataframe(query)
    
    # Create regional comparison
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Regional Analysis: Economic and Social Indicators', fontsize=16, fontweight='bold')
    
    # GDP by Region
    sns.boxplot(data=df, x='region', y='gdp', ax=axes[0])
    axes[0].set_title('GDP Distribution by Region')
    axes[0].set_ylabel('GDP per Capita ($)')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Life Expectancy by Region
    sns.boxplot(data=df, x='region', y='life_expectancy', ax=axes[1])
    axes[1].set_title('Life Expectancy by Region')
    axes[1].set_ylabel('Life Expectancy (years)')
    axes[1].tick_params(axis='x', rotation=45)
    
    # Internet by Region
    sns.boxplot(data=df, x='region', y='internet', ax=axes[2])
    axes[2].set_title('Internet Penetration by Region')
    axes[2].set_ylabel('Internet Penetration (%)')
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Save plot
    output_path = output_dir / 'regional_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Regional analysis saved: {output_path}")
    return output_path

def create_temporal_trends(db, output_dir):
    """Create temporal trends visualization."""
    query = """
    SELECT 
        d.year,
        AVG(d.gdp) as avg_gdp,
        AVG(d.life_expectancy) as avg_life_expectancy,
        AVG(d.internet) as avg_internet,
        AVG(d.enrollment) as avg_enrollment
    FROM data d
    WHERE d.year >= 2000
    AND d.gdp IS NOT NULL
    GROUP BY d.year
    ORDER BY d.year;
    """
    
    df = db._query_to_dataframe(query)
    
    # Create temporal trends plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Global Trends: 20-Year Development Indicators', fontsize=16, fontweight='bold')
    
    # GDP Trend
    axes[0,0].plot(df['year'], df['avg_gdp'], marker='o', linewidth=2, color='steelblue')
    axes[0,0].set_title('Average GDP per Capita Trend')
    axes[0,0].set_ylabel('GDP ($)')
    axes[0,0].grid(True, alpha=0.3)
    
    # Life Expectancy Trend
    axes[0,1].plot(df['year'], df['avg_life_expectancy'], marker='o', linewidth=2, color='forestgreen')
    axes[0,1].set_title('Average Life Expectancy Trend')
    axes[0,1].set_ylabel('Life Expectancy (years)')
    axes[0,1].grid(True, alpha=0.3)
    
    # Internet Trend
    axes[1,0].plot(df['year'], df['avg_internet'], marker='o', linewidth=2, color='orangered')
    axes[1,0].set_title('Average Internet Penetration Trend')
    axes[1,0].set_ylabel('Internet Penetration (%)')
    axes[1,0].set_xlabel('Year')
    axes[1,0].grid(True, alpha=0.3)
    
    # Education Trend
    axes[1,1].plot(df['year'], df['avg_enrollment'], marker='o', linewidth=2, color='purple')
    axes[1,1].set_title('Average School Enrollment Trend')
    axes[1,1].set_ylabel('Enrollment Rate (%)')
    axes[1,1].set_xlabel('Year')
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    output_path = output_dir / 'temporal_trends.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Temporal trends saved: {output_path}")
    return output_path

def main():
    """Generate all blog visualizations."""
    print("🎨 Starting Blog Visualization Generation")
    print("=" * 50)
    
    # Setup
    setup_plot_style()
    
    # Create output directory
    output_dir = Path("static/images/blog")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    try:
        db = get_db_instance()
        print(f"✅ Database connected successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    try:
        # Generate visualizations
        print("\n📊 Generating correlation heatmap...")
        create_correlation_heatmap(db, output_dir)
        
        print("\n📈 Generating GDP development scatter plots...")
        create_gdp_development_scatter(db, output_dir)
        
        print("\n🌍 Generating regional analysis...")
        create_regional_analysis(db, output_dir)
        
        print("\n⏰ Generating temporal trends...")
        create_temporal_trends(db, output_dir)
        
        print("\n🎉 All visualizations generated successfully!")
        print(f"📁 Saved to: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()