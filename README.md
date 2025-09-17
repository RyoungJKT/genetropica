# GeneTropica

**GeneTropica** — Dengue · Climate · Forecast (MVP)

A Streamlit application for analyzing dengue data with climate correlations and forecasting capabilities.

## Installation

### Prerequisites
- Conda or Miniconda installed
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/darwins3/genetropica.git
cd genetropica
```

2. Create and activate the conda environment:
```bash
conda env create -f env.yaml
conda activate genetropica
```

3. Run the application:
```bash
streamlit run app/app.py
```

The app will open in your default browser at `http://localhost:8501`

## Project Structure

```
genetropica/
├── README.md           # This file
├── env.yaml           # Conda environment specification
├── .gitignore         # Git ignore rules
├── app/
│   ├── app.py         # Main Streamlit application
│   └── components/    # UI components
├── data/
│   └── mock/          # Mock data for development
├── src/
│   ├── __init__.py    # Package initialization
│   ├── data_io.py     # Data input/output utilities
│   ├── transforms.py  # Data transformations
│   ├── charts.py      # Visualization functions
│   └── forecast.py    # Forecasting models
├── assets/
│   └── phylo_placeholder.png  # Placeholder images
└── docs/
    └── methods.md     # Methodology documentation
```

## Mock Data

The application includes a mock data generator for demonstration purposes. To generate sample data for 6 Indonesian provinces:

```bash
# Make sure environment is activated
conda activate genetropica

# Generate mock datasets
python -m src.data_io --make-mock
```

This creates the following files in `data/mock/`:
- `provinces.geojson` - Geographic boundaries for 6 provinces
- `dengue_cases.csv` - Monthly dengue case counts (2017-present)
- `serotype_share.csv` - Distribution of dengue serotypes (DENV1-4)
- `climate.csv` - Monthly rainfall and temperature data
- `features.csv` - Combined dataset with all features

The mock data includes:
- Realistic seasonal patterns (monsoon season Nov-Mar)
- Temperature variations (26-30°C)
- Province-specific dengue serotype distributions
- Temporal trends and random variations

## Development

To contribute to this project:
1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

[Your License Here]

## Contact

[Your Contact Information]