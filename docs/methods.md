# GeneTropica Methods Documentation

## Overview

GeneTropica is a comprehensive platform for analyzing dengue fever patterns in relation to climate data, with integrated forecasting capabilities.

## Data Processing

### Input Data
- **Dengue Cases**: Time series data of dengue cases by region
- **Climate Variables**: Temperature, precipitation, humidity, and other meteorological data
- **Geographic Data**: Spatial information for regional analysis

### Data Transformation Pipeline
1. **Data Cleaning**: Removal of outliers and handling of missing values
2. **Temporal Aggregation**: Weekly/monthly aggregation of daily data
3. **Normalization**: Min-max or z-score normalization for comparative analysis
4. **Feature Engineering**: Creation of lagged variables and rolling statistics

## Analysis Methods

### Correlation Analysis
- Pearson correlation between climate variables and dengue incidence
- Lag correlation to identify delayed effects
- Spatial correlation for geographic patterns

### Time Series Decomposition
- Separation of trend, seasonal, and residual components
- Identification of cyclical patterns in dengue outbreaks

## Forecasting Models

### ARIMA Models
- Autoregressive Integrated Moving Average models for univariate forecasting
- Seasonal ARIMA (SARIMA) for capturing seasonal patterns

### Machine Learning Approaches
- Random Forest regression for multivariate prediction
- Support Vector Regression (SVR) for non-linear relationships

### Model Evaluation
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Error (MAE)
- Mean Absolute Percentage Error (MAPE)

## Visualization

### Interactive Charts
- Time series plots with zoom and pan capabilities
- Heatmaps for correlation matrices
- Geographic maps for spatial distribution

### Dashboard Components
- Real-time data updates
- Customizable date ranges
- Multi-variable comparisons

## References

1. World Health Organization. (2023). Dengue and severe dengue.
2. Brady, O. J., & Hay, S. I. (2020). The global expansion of dengue.
3. Hyndman, R. J., & Athanasopoulos, G. (2021). Forecasting: principles and practice.

## Version History

- **v0.1.0** (Initial Release): Basic scaffold and structure
- Future versions will include enhanced forecasting and real-time data integration