"""
Data input/output utilities for GeneTropica.
Handles loading, saving, and managing data files.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Optional, Union, Dict, Any


def load_csv(filepath: Union[str, Path], **kwargs) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    
    Args:
        filepath: Path to the CSV file
        **kwargs: Additional arguments passed to pd.read_csv
    
    Returns:
        pd.DataFrame: Loaded data
    """
    return pd.read_csv(filepath, **kwargs)


def save_csv(df: pd.DataFrame, filepath: Union[str, Path], **kwargs) -> None:
    """
    Save a DataFrame to a CSV file.
    
    Args:
        df: DataFrame to save
        filepath: Path where to save the CSV
        **kwargs: Additional arguments passed to df.to_csv
    """
    df.to_csv(filepath, index=False, **kwargs)


def load_json(filepath: Union[str, Path]) -> Dict[Any, Any]:
    """
    Load a JSON file.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        Dict: Loaded JSON data
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: Dict[Any, Any], filepath: Union[str, Path], indent: int = 2) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filepath: Path where to save the JSON
        indent: JSON indentation level
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)


def get_data_path(subpath: str = "") -> Path:
    """
    Get the path to the data directory.
    
    Args:
        subpath: Subdirectory within data folder
    
    Returns:
        Path: Path to data directory or subdirectory
    """
    base_path = Path(__file__).parent.parent / "data"
    if subpath:
        return base_path / subpath
    return base_path