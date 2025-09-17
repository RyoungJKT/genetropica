"""
Data transformation utilities for GeneTropica.
Handles data preprocessing, cleaning, and feature engineering.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Union


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
        return (df[column] - min_val) / (max_val - min_val)
    elif method == 'zscore':
        mean_val = df[column].mean()
        std_val = df[column].std()
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
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.set_index(date_column)
    
    return df[value_columns].resample(freq).agg({
        col: 'sum' if 'count' in col.lower() else 'mean'
        for col in value_columns
    })


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