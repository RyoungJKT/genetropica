"""
Data transformation utilities for GeneTropica.
Handles data preprocessing, cleaning, and feature engineering.
Includes cached data loaders and filtering functions.
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, List, Union, Dict, Tuple
from pathlib import Path
import json

# Handle optional geopandas import for cloud deployment
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    print("GeoPandas not available - using simplified features")


# Color palette for serotypes
SEROTYPE_PALETTE = {
    'DENV1': '#FF6B6B',  # Red
    'DENV2': '#4ECDC4',  # Teal  
    'DENV3': '#45B7D1',  # Blue
    'DENV4': '#96CEB4'   # Green
}


@st.cache_data(ttl=3600)
def load_geo():
    """
    Load provinces GeoJSON. Falls back to simplified data if GeoPandas unavailable.
    Cached for 1 hour.
    
    Returns:
        DataFrame or GeoDataFrame: Provinces with geometry and metadata
    """
    # Get path to mock data
    data_path = Path(__file__).parent.parent / "data" / "mock" / "provinces.geojson"
    
    if GEOPANDAS_AVAILABLE:
        # Load as GeoDataFrame when geopandas is available
        gdf = gpd.read_file(str(data_path))
        
        # Ensure correct dtypes
        gdf['province_id'] = gdf['province_id'].astype(str)
        gdf['province_name'] = gdf['province_name'].astype(str)
        gdf['lon'] = gdf['lon'].astype(float)
        gdf['lat'] = gdf['lat'].astype(float)
        
        # Quick checks
        assert len(gdf) > 0, "No provinces loaded"
        assert gdf['province_id'].notna().all(), "Missing province_id values"
        assert gdf['province_name'].notna().all(), "Missing province_name values"
        
        return gdf
    else:
        # Fallback: Create a simple DataFrame with province data
        provinces_data = {
            'province_id': ['DKI', 'JABAR', 'JATENG', 'JATIM', 'BANTEN', 'DIY'],
            'province_name': ['DKI Jakarta', 'West Java', 'Central Java', 'East Java', 'Banten', 'Yogyakarta'],
            'lon': [106.8456, 107.6098, 110.4203, 112.6349, 106.0640, 110.3695],
            'lat': [-6.2088, -6.9147, -7.1506, -7.5361, -6.4058, -7.7956],
            'geometry': [None] * 6  # Simplified - no actual geometry
        }
        
        df = pd.DataFrame(provinces_data)
        df['province_id'] = df['province_id'].astype(str)
        df['province_name'] = df['province_name'].astype(str)
        df['lon'] = df['lon'].astype(float)
        df['lat'] = df['lat'].astype(float)
        
        return df


@st.cache_data(ttl=3600)
def load_features() -> pd.DataFrame:
    """
    Load features.csv with correct dtypes and monthly DateTimeIndex.
    Cached for 1 hour.
    
    Returns:
        pd.DataFrame: Features dataset with DateTimeIndex
    """
    # Get path to mock data
    data_path = Path(__file__).parent.parent / "data" / "mock" / "features.csv"
    
    # Load CSV
    df = pd.read_csv(str(data_path))
    
    # Convert date to datetime and set as index
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    
    # Don't force freq='MS' as it may not match the actual data spacing
    # Just ensure it's a DatetimeIndex
    df.index = pd.DatetimeIndex(df.index)
    
    # Ensure correct dtypes
    df['province_id'] = df['province_id'].astype(str)
    df['cases'] = df['cases'].astype(int)
    df['rainfall_mm'] = df['rainfall_mm'].astype(float)
    df['temperature_c'] = df['temperature_c'].astype(float)
    df['dominant_serotype'] = df['dominant_serotype'].astype(str)
    
    # Serotype shares as float
    for col in ['denv1_share', 'denv2_share', 'denv3_share', 'denv4_share']:
        df[col] = df[col].astype(float)
    
    # Quick checks
    assert len(df) > 0, "No data loaded"
    assert df['province_id'].notna().all(), "Missing province_id values"
    assert df['cases'].notna().all(), "Missing case values"
    assert df['rainfall_mm'].notna().all(), "Missing rainfall values"
    assert df['temperature_c'].notna().all(), "Missing temperature values"
    # Check: row count > 0, no NaNs in required columns
    
    # Verify serotype shares sum to ~1.0
    serotype_cols = ['denv1_share', 'denv2_share', 'denv3_share', 'denv4_share']
    share_sums = df[serotype_cols].sum(axis=1)
    assert np.allclose(share_sums, 1.0, rtol=0.01), "Serotype shares don't sum to 1.0"
    
    return df


def compute_dominant_serotype(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Add dominant_serotype column and return palette mapping.
    
    Args:
        df: DataFrame with denv1_share..denv4_share columns
        
    Returns:
        Tuple of (DataFrame with dominant_serotype, palette dict)
    """
    df = df.copy()
    
    # Get serotype share columns
    serotype_cols = ['denv1_share', 'denv2_share', 'denv3_share', 'denv4_share']
    
    # Check if columns exist
    if not all(col in df.columns for col in serotype_cols):
        raise ValueError(f"Missing serotype columns. Expected: {serotype_cols}")
    
    # Find dominant serotype (argmax)
    dominant_idx = df[serotype_cols].values.argmax(axis=1)
    df['dominant_serotype'] = ['DENV' + str(i+1) for i in dominant_idx]
    
    # Return dataframe and palette
    return df, SEROTYPE_PALETTE


@st.cache_data(ttl=3600)
def build_province_month_df(
    province: Optional[Union[str, List[str]]] = None,
    year_range: Optional[Tuple[int, int]] = None,
    serotypes: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Build a filtered tidy dataframe based on province, year range, and serotypes.
    Cached for 1 hour.
    
    Args:
        province: Single province ID, list of IDs, or None for all
        year_range: Tuple of (start_year, end_year) or None for all
        serotypes: List of serotypes to filter dominant_serotype, or None for all
        
    Returns:
        pd.DataFrame: Filtered dataset
    """
    # Load base features
    df = load_features()
    
    # Filter by province
    if province is not None:
        if isinstance(province, str):
            province = [province]
        df = df[df['province_id'].isin(province)]
        # Check: filtered provinces exist
        assert len(df) > 0, f"No data for provinces: {province}"
    
    # Filter by year range
    if year_range is not None:
        start_year, end_year = year_range
        df = df[(df.index.year >= start_year) & (df.index.year <= end_year)]
        # Check: filtered years exist
        assert len(df) > 0, f"No data for years {start_year}-{end_year}"
    
    # Filter by dominant serotype
    if serotypes is not None:
        df = df[df['dominant_serotype'].isin(serotypes)]
        # Check: filtered serotypes exist
        assert len(df) > 0, f"No data for serotypes: {serotypes}"
    
    # Quick validation
    assert len(df) > 0, "Filtered dataframe is empty"
    
    return df


# Helper functions from original file

def normalize_column(df: pd.DataFrame, column: str, method: str = 'minmax') -> pd.Series:
    """
    Normalize a column in a DataFrame.
    
    Args:
        df: Input DataFrame
        column: Column name to normalize
        method: Normalization method ('minmax' or 'zscore')
    
    Returns:
        pd.Series: Normalized column
    """
    if method == 'minmax':
        min_val = df[column].min()
        max_val = df[column].max()
        if max_val == min_val:
            return pd.Series(0.5, index=df.index)
        return (df[column] - min_val) / (max_val - min_val)
    elif method == 'zscore':
        mean_val = df[column].mean()
        std_val = df[column].std()
        if std_val == 0:
            return pd.Series(0, index=df.index)
        return (df[column] - mean_val) / std_val
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def aggregate_temporal(df: pd.DataFrame, 
                      date_column: str,
                      value_columns: List[str],
                      freq: str = 'W') -> pd.DataFrame:
    """
    Aggregate data by temporal frequency.
    
    Args:
        df: Input DataFrame
        date_column: Name of the date column
        value_columns: Columns to aggregate
        freq: Frequency for aggregation ('D', 'W', 'M', etc.)
    
    Returns:
        pd.DataFrame: Aggregated DataFrame
    """
    df = df.copy()
    
    # If date_column is not the index, set it
    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.set_index(date_column)
    
    # Aggregate based on column types
    agg_dict = {}
    for col in value_columns:
        if col in df.columns:
            if 'count' in col.lower() or 'cases' in col.lower():
                agg_dict[col] = 'sum'
            else:
                agg_dict[col] = 'mean'
    
    return df[value_columns].resample(freq).agg(agg_dict)


def calculate_rolling_average(df: pd.DataFrame,
                             column: str,
                             window: int = 7,
                             min_periods: int = 1) -> pd.Series:
    """
    Calculate rolling average for a column.
    
    Args:
        df: Input DataFrame
        column: Column name
        window: Window size for rolling average
        min_periods: Minimum number of observations required
    
    Returns:
        pd.Series: Rolling average
    """
    return df[column].rolling(window=window, min_periods=min_periods).mean()


def handle_missing_values(df: pd.DataFrame,
                         strategy: str = 'forward_fill',
                         columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Handle missing values in DataFrame.
    
    Args:
        df: Input DataFrame
        strategy: Strategy for handling missing values
        columns: Specific columns to process (None for all)
    
    Returns:
        pd.DataFrame: DataFrame with handled missing values
    """
    df = df.copy()
    
    if columns is None:
        columns = df.columns.tolist()
    
    if strategy == 'forward_fill':
        df[columns] = df[columns].fillna(method='ffill')
    elif strategy == 'backward_fill':
        df[columns] = df[columns].fillna(method='bfill')
    elif strategy == 'interpolate':
        df[columns] = df[columns].interpolate(method='linear')
    elif strategy == 'drop':
        df = df.dropna(subset=columns)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    return df


# Quick test function for development
def test_transforms():
    """Quick test of transform functions."""
    print("Testing transforms...")
    
    # Test load_geo
    gdf = load_geo()
    print(f"✓ Loaded {len(gdf)} provinces")
    
    # Test load_features  
    df = load_features()
    print(f"✓ Loaded {len(df)} feature rows")
    
    # Test compute_dominant_serotype
    df_with_dominant, palette = compute_dominant_serotype(df.head())
    print(f"✓ Computed dominant serotypes, palette has {len(palette)} colors")
    
    # Test build_province_month_df
    df_filtered = build_province_month_df(
        province=['DKI', 'JABAR'],
        year_range=(2020, 2023)
    )
    print(f"✓ Filtered to {len(df_filtered)} rows")
    
    print("All transforms working!")


if __name__ == "__main__":
    test_transforms()