"""
Data input/output utilities for GeneTropica.
Handles loading, saving, and managing data files.
Includes mock data generation for demo purposes.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from datetime import datetime, timedelta
import argparse


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


def create_mock_provinces_geojson() -> Dict:
    """
    Create simplified GeoJSON for 6 Indonesian provinces.
    Using rectangular polygons centered on actual coordinates.
    """
    provinces = [
        {"id": "DKI", "name": "DKI Jakarta", "lon": 106.8456, "lat": -6.2088},
        {"id": "JABAR", "name": "West Java", "lon": 107.6098, "lat": -6.9147},
        {"id": "JATENG", "name": "Central Java", "lon": 110.4203, "lat": -7.1506},
        {"id": "JATIM", "name": "East Java", "lon": 112.6349, "lat": -7.5361},
        {"id": "BANTEN", "name": "Banten", "lon": 106.0640, "lat": -6.4058},
        {"id": "DIY", "name": "Yogyakarta", "lon": 110.3695, "lat": -7.7956}
    ]
    
    features = []
    for prov in provinces:
        # Create a simple rectangular polygon around the center point
        # Roughly 0.5 degrees wide/tall for simplicity
        lon, lat = prov["lon"], prov["lat"]
        coordinates = [[
            [lon - 0.25, lat - 0.25],
            [lon + 0.25, lat - 0.25],
            [lon + 0.25, lat + 0.25],
            [lon - 0.25, lat + 0.25],
            [lon - 0.25, lat - 0.25]  # Close the polygon
        ]]
        
        feature = {
            "type": "Feature",
            "properties": {
                "province_id": prov["id"],
                "province_name": prov["name"],
                "lon": lon,
                "lat": lat
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def create_mock_dengue_cases(start_year: int = 2017) -> pd.DataFrame:
    """
    Generate monthly dengue case data with seasonal patterns.
    Peak cases during rainy season (Nov-Mar).
    """
    provinces = ["DKI", "JABAR", "JATENG", "JATIM", "BANTEN", "DIY"]
    
    # Base cases per province (different baseline rates)
    base_cases = {
        "DKI": 800,      # Dense urban area
        "JABAR": 1200,   # Large population
        "JATENG": 900,   
        "JATIM": 1000,   
        "BANTEN": 600,   
        "DIY": 300       # Smaller population
    }
    
    # Generate monthly dates from start_year to present
    start_date = pd.Timestamp(f"{start_year}-01-01")
    end_date = pd.Timestamp.now()
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')  # Month Start
    
    data = []
    for date in dates:
        month = date.month
        year = date.year
        
        # Seasonal multiplier (higher in rainy season Nov-Mar)
        if month in [11, 12, 1, 2, 3]:
            seasonal_mult = 1.5 + 0.3 * np.sin((month - 1) * np.pi / 5)
        else:
            seasonal_mult = 0.7 + 0.2 * np.sin((month - 4) * np.pi / 7)
        
        # Year trend (slight increase over years)
        year_trend = 1.0 + 0.02 * (year - start_year)
        
        for province in provinces:
            # Calculate cases with randomness
            base = base_cases[province]
            cases = int(base * seasonal_mult * year_trend * np.random.uniform(0.7, 1.3))
            cases = max(10, cases)  # Minimum 10 cases
            
            data.append({
                'date': date.strftime('%Y-%m-01'),
                'province_id': province,
                'cases': cases
            })
    
    return pd.DataFrame(data)


def create_mock_serotype_share() -> pd.DataFrame:
    """
    Generate monthly serotype distribution data (DENV1-4).
    Shares sum to 1.0 for each province-month.
    """
    provinces = ["DKI", "JABAR", "JATENG", "JATIM", "BANTEN", "DIY"]
    
    # Regional serotype patterns (some provinces have dominant serotypes)
    serotype_patterns = {
        "DKI": [0.35, 0.30, 0.20, 0.15],      # DENV1 dominant
        "JABAR": [0.25, 0.35, 0.25, 0.15],    # DENV2 dominant
        "JATENG": [0.20, 0.25, 0.35, 0.20],   # DENV3 dominant
        "JATIM": [0.25, 0.25, 0.30, 0.20],    # Mixed
        "BANTEN": [0.40, 0.25, 0.20, 0.15],   # DENV1 dominant
        "DIY": [0.20, 0.20, 0.25, 0.35]       # DENV4 dominant
    }
    
    start_date = pd.Timestamp("2017-01-01")
    end_date = pd.Timestamp.now()
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    data = []
    for date in dates:
        for province in provinces:
            # Get base pattern and add random variation
            base_shares = np.array(serotype_patterns[province])
            noise = np.random.dirichlet(np.ones(4) * 10)  # Add noise
            shares = 0.7 * base_shares + 0.3 * noise
            shares = shares / shares.sum()  # Ensure sum = 1.0
            
            data.append({
                'date': date.strftime('%Y-%m-01'),
                'province_id': province,
                'denv1_share': round(shares[0], 3),
                'denv2_share': round(shares[1], 3),
                'denv3_share': round(shares[2], 3),
                'denv4_share': round(shares[3], 3)
            })
    
    return pd.DataFrame(data)


def create_mock_climate() -> pd.DataFrame:
    """
    Generate monthly climate data with monsoon patterns.
    Higher rainfall Nov-Mar, temperature 26-30°C with mild variation.
    """
    provinces = ["DKI", "JABAR", "JATENG", "JATIM", "BANTEN", "DIY"]
    
    # Base climate characteristics per province
    climate_base = {
        "DKI": {"temp": 28.5, "rainfall": 150},
        "JABAR": {"temp": 27.5, "rainfall": 180},
        "JATENG": {"temp": 28.0, "rainfall": 160},
        "JATIM": {"temp": 29.0, "rainfall": 120},
        "BANTEN": {"temp": 28.5, "rainfall": 170},
        "DIY": {"temp": 27.0, "rainfall": 140}
    }
    
    start_date = pd.Timestamp("2017-01-01")
    end_date = pd.Timestamp.now()
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    data = []
    for date in dates:
        month = date.month
        
        # Monsoon pattern for rainfall
        if month in [11, 12, 1, 2, 3]:
            rainfall_mult = 1.5 + 0.5 * np.sin((month - 1) * np.pi / 5)
        else:
            rainfall_mult = 0.4 + 0.2 * np.sin((month - 4) * np.pi / 7)
        
        # Temperature variation (slightly cooler during rainy season)
        if month in [11, 12, 1, 2, 3]:
            temp_adjust = -1.0
        else:
            temp_adjust = 0.5
        
        for province in provinces:
            base = climate_base[province]
            
            # Calculate rainfall with seasonality and noise
            rainfall = base["rainfall"] * rainfall_mult * np.random.uniform(0.8, 1.2)
            rainfall = max(10, round(rainfall, 1))
            
            # Calculate temperature with mild variation
            temp = base["temp"] + temp_adjust + np.random.uniform(-1.0, 1.0)
            temp = round(np.clip(temp, 26.0, 30.0), 1)
            
            data.append({
                'date': date.strftime('%Y-%m-01'),
                'province_id': province,
                'rainfall_mm': rainfall,
                'temperature_c': temp
            })
    
    return pd.DataFrame(data)


def create_features_dataset() -> pd.DataFrame:
    """
    Create a joined features dataset combining all mock data.
    """
    # Generate all component datasets
    dengue_df = create_mock_dengue_cases()
    serotype_df = create_mock_serotype_share()
    climate_df = create_mock_climate()
    
    # Merge all datasets on date and province_id
    features_df = dengue_df.merge(
        climate_df, 
        on=['date', 'province_id'], 
        how='left'
    ).merge(
        serotype_df,
        on=['date', 'province_id'],
        how='left'
    )
    
    # Add dominant serotype column
    serotype_cols = ['denv1_share', 'denv2_share', 'denv3_share', 'denv4_share']
    dominant_idx = features_df[serotype_cols].values.argmax(axis=1)
    features_df['dominant_serotype'] = ['DENV' + str(i+1) for i in dominant_idx]
    
    # Reorder columns
    column_order = [
        'date', 'province_id', 'cases', 'rainfall_mm', 'temperature_c',
        'dominant_serotype', 'denv1_share', 'denv2_share', 'denv3_share', 'denv4_share'
    ]
    features_df = features_df[column_order]
    
    return features_df


def generate_mock_data(output_dir: Optional[Path] = None) -> None:
    """
    Generate all mock datasets and save to data/mock/.
    """
    if output_dir is None:
        output_dir = get_data_path("mock")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating mock datasets...")
    
    # 1. Generate provinces GeoJSON
    print("  - Creating provinces.geojson...")
    provinces_geojson = create_mock_provinces_geojson()
    with open(output_dir / "provinces.geojson", 'w') as f:
        json.dump(provinces_geojson, f, indent=2)
    
    # 2. Generate dengue cases
    print("  - Creating dengue_cases.csv...")
    dengue_df = create_mock_dengue_cases()
    save_csv(dengue_df, output_dir / "dengue_cases.csv")
    
    # 3. Generate serotype shares
    print("  - Creating serotype_share.csv...")
    serotype_df = create_mock_serotype_share()
    save_csv(serotype_df, output_dir / "serotype_share.csv")
    
    # 4. Generate climate data
    print("  - Creating climate.csv...")
    climate_df = create_mock_climate()
    save_csv(climate_df, output_dir / "climate.csv")
    
    # 5. Generate features dataset
    print("  - Creating features.csv...")
    features_df = create_features_dataset()
    save_csv(features_df, output_dir / "features.csv")
    
    # Print summary
    print(f"\nMock data generated successfully in {output_dir}")
    print(f"  - provinces.geojson: 6 provinces")
    print(f"  - dengue_cases.csv: {len(dengue_df)} rows")
    print(f"  - serotype_share.csv: {len(serotype_df)} rows")
    print(f"  - climate.csv: {len(climate_df)} rows")
    print(f"  - features.csv: {len(features_df)} rows")
    
    # Print date range
    print(f"\nDate range: {dengue_df['date'].min()} to {dengue_df['date'].max()}")
    print(f"Provinces: {', '.join(dengue_df['province_id'].unique())}")


def main():
    """CLI entrypoint for data operations."""
    parser = argparse.ArgumentParser(description='GeneTropica data utilities')
    parser.add_argument(
        '--make-mock',
        action='store_true',
        help='Generate mock datasets for demo'
    )
    
    args = parser.parse_args()
    
    if args.make_mock:
        generate_mock_data()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()