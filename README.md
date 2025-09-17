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

## Development

To contribute to this project:
1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

Russell Young

## Contact

ryoung.jkt@gmail.com