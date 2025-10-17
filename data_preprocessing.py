"""
Data Preprocessing Module for GDP Analytics
===========================================

This module provides comprehensive data preprocessing utilities including:
- Data cleaning and validation
- Normalization and scaling
- Outlier detection and handling
- Missing value treatment
- Feature engineering
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer, KNNImputer
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    """
    Comprehensive data preprocessing class for GDP analytics.
    """
    
    def __init__(self):
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler()
        }
        self.imputers = {
            'mean': SimpleImputer(strategy='mean'),
            'median': SimpleImputer(strategy='median'),
            'mode': SimpleImputer(strategy='most_frequent'),
            'knn': KNNImputer(n_neighbors=5)
        }
    
    # ================================
    # DATA CLEANING & VALIDATION
    # ================================
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        General data cleaning operations.
        """
        df_clean = df.copy()
        
        # Remove duplicate rows
        initial_rows = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        duplicates_removed = initial_rows - len(df_clean)
        
        # Convert data types
        df_clean = self._convert_data_types(df_clean)
        
        # Remove rows with all NaN values
        df_clean = df_clean.dropna(how='all')
        
        print(f"Data cleaning completed:")
        print(f"  - Duplicates removed: {duplicates_removed}")
        print(f"  - Final shape: {df_clean.shape}")
        
        return df_clean
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate data types."""
        df_converted = df.copy()
        
        # Numeric columns that should be float
        numeric_columns = ['gdp', 'population', 'female', 'male', 'life_expectancy',
                          'migration', 'infant_mortality', 'internet', 'hci',
                          'enrollment', 'urban_pop', 'lat', 'lng']
        
        for col in numeric_columns:
            if col in df_converted.columns:
                df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce')
        
        # Integer columns
        integer_columns = ['year', 'population', 'migration']
        for col in integer_columns:
            if col in df_converted.columns:
                # Convert to float first to handle NaN, then to Int64 (nullable integer)
                df_converted[col] = df_converted[col].astype('Int64')
        
        return df_converted
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive data quality assessment.
        """
        quality_report = {
            'shape': df.shape,
            'missing_values': {},
            'outliers': {},
            'data_types': df.dtypes.to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2  # MB
        }
        
        # Missing values analysis
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_percent = (missing_count / len(df)) * 100
            quality_report['missing_values'][col] = {
                'count': missing_count,
                'percentage': round(missing_percent, 2)
            }
        
        # Outlier detection for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            outliers = self.detect_outliers_iqr(df[col])
            quality_report['outliers'][col] = len(outliers)
        
        return quality_report
    
    # ================================
    # MISSING VALUE HANDLING
    # ================================
    
    def handle_missing_values(self, df: pd.DataFrame, 
                            strategy: str = 'mean',
                            columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Handle missing values using various strategies.
        """
        df_filled = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if strategy in self.imputers:
            imputer = self.imputers[strategy]
            df_filled[columns] = imputer.fit_transform(df_filled[columns])
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return df_filled
    
    def forward_fill_by_country(self, df: pd.DataFrame, 
                               columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Forward fill missing values by country (useful for time series data).
        """
        df_filled = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if 'country_code' in df.columns:
            df_filled = df_filled.sort_values(['country_code', 'year'])
            df_filled[columns] = df_filled.groupby('country_code')[columns].fillna(method='ffill')
        
        return df_filled
    
    # ================================
    # OUTLIER DETECTION & HANDLING
    # ================================
    
    def detect_outliers_iqr(self, series: pd.Series, 
                           multiplier: float = 1.5) -> pd.Index:
        """
        Detect outliers using Interquartile Range (IQR) method.
        """
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)].index
        return outliers
    
    def detect_outliers_zscore(self, series: pd.Series, 
                              threshold: float = 3.0) -> pd.Index:
        """
        Detect outliers using Z-score method.
        """
        z_scores = np.abs((series - series.mean()) / series.std())
        outliers = series[z_scores > threshold].index
        return outliers
    
    def handle_outliers(self, df: pd.DataFrame, 
                       method: str = 'cap',
                       columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Handle outliers using various methods.
        """
        df_handled = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if method == 'cap':
                # Cap outliers at 95th and 5th percentiles
                lower_cap = df[col].quantile(0.05)
                upper_cap = df[col].quantile(0.95)
                df_handled[col] = np.clip(df_handled[col], lower_cap, upper_cap)
            
            elif method == 'remove':
                # Remove outliers using IQR
                outliers = self.detect_outliers_iqr(df[col])
                df_handled = df_handled.drop(outliers)
            
            elif method == 'transform':
                # Log transformation for positive skewed data
                if (df[col] > 0).all():
                    df_handled[col] = np.log1p(df[col])
        
        return df_handled
    
    # ================================
    # DATA NORMALIZATION & SCALING
    # ================================
    
    def normalize_data(self, df: pd.DataFrame, 
                      method: str = 'standard',
                      columns: Optional[List[str]] = None) -> Tuple[pd.DataFrame, object]:
        """
        Normalize data using various scaling methods.
        """
        df_normalized = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
            # Exclude categorical-like columns
            exclude_cols = ['year', 'country_code']
            columns = [col for col in columns if col not in exclude_cols]
        
        if method in self.scalers:
            scaler = self.scalers[method]
            df_normalized[columns] = scaler.fit_transform(df_normalized[columns])
            return df_normalized, scaler
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    def denormalize_data(self, df: pd.DataFrame, scaler: object, 
                        columns: List[str]) -> pd.DataFrame:
        """
        Reverse normalization using fitted scaler.
        """
        df_denormalized = df.copy()
        df_denormalized[columns] = scaler.inverse_transform(df_denormalized[columns])
        return df_denormalized
    
    # ================================
    # FEATURE ENGINEERING
    # ================================
    
    def create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived features for better analysis.
        """
        df_enhanced = df.copy()
        
        # GDP per capita (if population data exists)
        if 'gdp' in df.columns and 'population' in df.columns:
            df_enhanced['gdp_per_capita'] = df_enhanced['gdp'] / df_enhanced['population'] * 1000
        
        # Population density proxy (if urban population exists)
        if 'population' in df.columns and 'urban_pop' in df.columns:
            df_enhanced['urban_population'] = (df_enhanced['population'] * 
                                             df_enhanced['urban_pop'] / 100)
        
        # Gender ratio
        if 'female' in df.columns and 'male' in df.columns:
            df_enhanced['gender_ratio'] = df_enhanced['female'] / df_enhanced['male']
        
        # Internet penetration rate (already in percentage)
        if 'internet' in df.columns:
            df_enhanced['internet_category'] = pd.cut(
                df_enhanced['internet'], 
                bins=[0, 25, 50, 75, 100], 
                labels=['Low', 'Medium', 'High', 'Very High']
            )
        
        # Economic development category based on GDP per capita
        if 'gdp_per_capita' in df_enhanced.columns:
            df_enhanced['development_category'] = pd.cut(
                df_enhanced['gdp_per_capita'],
                bins=[0, 5000, 15000, 30000, float('inf')],
                labels=['Low Income', 'Lower Middle', 'Upper Middle', 'High Income']
            )
        
        # Year-over-year growth rates (requires grouped data)
        if 'year' in df.columns and 'country_code' in df.columns:
            df_enhanced = self._calculate_growth_rates(df_enhanced)
        
        return df_enhanced
    
    def _calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate year-over-year growth rates for numeric columns.
        """
        df_growth = df.copy()
        df_growth = df_growth.sort_values(['country_code', 'year'])
        
        growth_columns = ['gdp', 'population', 'life_expectancy', 'internet']
        
        for col in growth_columns:
            if col in df.columns:
                df_growth[f'{col}_growth'] = (
                    df_growth.groupby('country_code')[col]
                    .pct_change() * 100
                )
        
        return df_growth
    
    # ================================
    # DATA PREPARATION FOR ML
    # ================================
    
    def prepare_for_ml(self, df: pd.DataFrame, 
                      target_column: str,
                      feature_columns: Optional[List[str]] = None,
                      test_size: float = 0.2,
                      normalize: bool = True) -> Dict:
        """
        Prepare data for machine learning.
        """
        from sklearn.model_selection import train_test_split
        
        # Select features
        if feature_columns is None:
            feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_columns = [col for col in feature_columns 
                             if col != target_column and col not in ['year', 'country_code']]
        
        # Remove rows with missing target values
        df_ml = df.dropna(subset=[target_column])
        
        # Handle missing values in features
        df_ml = self.handle_missing_values(df_ml, strategy='mean', columns=feature_columns)
        
        # Prepare X and y
        X = df_ml[feature_columns]
        y = df_ml[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Normalize if requested
        scaler = None
        if normalize:
            scaler = StandardScaler()
            X_train = pd.DataFrame(
                scaler.fit_transform(X_train),
                columns=X_train.columns,
                index=X_train.index
            )
            X_test = pd.DataFrame(
                scaler.transform(X_test),
                columns=X_test.columns,
                index=X_test.index
            )
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'original_data': df_ml
        }
    
    # ================================
    # UTILITY FUNCTIONS
    # ================================
    
    def get_preprocessing_summary(self, df_original: pd.DataFrame, 
                                df_processed: pd.DataFrame) -> Dict:
        """
        Generate summary of preprocessing operations.
        """
        summary = {
            'original_shape': df_original.shape,
            'processed_shape': df_processed.shape,
            'rows_removed': df_original.shape[0] - df_processed.shape[0],
            'columns_added': df_processed.shape[1] - df_original.shape[1],
            'missing_values_before': df_original.isnull().sum().sum(),
            'missing_values_after': df_processed.isnull().sum().sum(),
            'memory_usage_mb': df_processed.memory_usage(deep=True).sum() / 1024**2
        }
        
        return summary


# ================================
# HELPER FUNCTIONS
# ================================

def quick_preprocess(df: pd.DataFrame, 
                    normalize: bool = True,
                    handle_outliers: bool = True,
                    create_features: bool = True) -> pd.DataFrame:
    """
    Quick preprocessing pipeline for common operations.
    """
    preprocessor = DataPreprocessor()
    
    # Clean data
    df_processed = preprocessor.clean_data(df)
    
    # Handle missing values
    df_processed = preprocessor.handle_missing_values(df_processed)
    
    # Handle outliers
    if handle_outliers:
        df_processed = preprocessor.handle_outliers(df_processed, method='cap')
    
    # Create derived features
    if create_features:
        df_processed = preprocessor.create_derived_features(df_processed)
    
    # Normalize data
    if normalize:
        numeric_cols = df_processed.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['year', 'country_code']
        cols_to_normalize = [col for col in numeric_cols if col not in exclude_cols]
        df_processed, _ = preprocessor.normalize_data(df_processed, columns=cols_to_normalize)
    
    return df_processed


def test_preprocessing():
    """Test preprocessing functions."""
    print("Testing Data Preprocessing Module")
    print("=" * 40)
    
    try:
        # Import database CRUD for testing
        from database_crud import get_db_instance
        
        db = get_db_instance()
        
        # Get sample data
        df = db.get_data_range(2015, 2020, ['US', 'CN', 'DE', 'IN', 'BR'])
        print(f"✅ Retrieved sample data: {df.shape}")
        
        # Initialize preprocessor
        preprocessor = DataPreprocessor()
        
        # Test data quality assessment
        quality_report = preprocessor.validate_data_quality(df)
        print(f"✅ Data quality assessment completed")
        
        # Test cleaning
        df_clean = preprocessor.clean_data(df)
        print(f"✅ Data cleaning completed: {df_clean.shape}")
        
        # Test feature engineering
        df_enhanced = preprocessor.create_derived_features(df_clean)
        print(f"✅ Feature engineering completed: {df_enhanced.shape}")
        
        # Test normalization
        df_normalized, scaler = preprocessor.normalize_data(df_enhanced)
        print(f"✅ Data normalization completed")
        
        # Test ML preparation
        if 'gdp' in df_enhanced.columns:
            ml_data = preprocessor.prepare_for_ml(df_enhanced, 'gdp')
            print(f"✅ ML data preparation completed")
            print(f"  - Training set: {ml_data['X_train'].shape}")
            print(f"  - Test set: {ml_data['X_test'].shape}")
        
        print("\n🎉 All preprocessing functions working successfully!")
        
    except Exception as e:
        print(f"❌ Error testing preprocessing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_preprocessing()