"""
Forecasting utilities for GeneTropica.
Implements time series forecasting models.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error


def decompose_time_series(series: pd.Series,
                         model: str = 'additive',
                         period: Optional[int] = None) -> Dict[str, pd.Series]:
    """
    Decompose a time series into trend, seasonal, and residual components.
    
    Args:
        series: Time series data
        model: 'additive' or 'multiplicative'
        period: Seasonal period (None for automatic detection)
    
    Returns:
        Dict: Dictionary with 'trend', 'seasonal', 'resid' components
    """
    result = seasonal_decompose(series, model=model, period=period)
    
    return {
        'trend': result.trend,
        'seasonal': result.seasonal,
        'resid': result.resid
    }


def fit_arima(series: pd.Series,
              order: Tuple[int, int, int] = (1, 1, 1),
              seasonal_order: Optional[Tuple[int, int, int, int]] = None) -> Any:
    """
    Fit an ARIMA model to a time series.
    
    Args:
        series: Time series data
        order: ARIMA order (p, d, q)
        seasonal_order: Seasonal ARIMA order (P, D, Q, s)
    
    Returns:
        Fitted ARIMA model
    """
    model = ARIMA(series, order=order, seasonal_order=seasonal_order)
    fitted_model = model.fit()
    return fitted_model


def forecast_arima(model: Any,
                  steps: int = 30,
                  alpha: float = 0.05) -> pd.DataFrame:
    """
    Generate forecasts from an ARIMA model.
    
    Args:
        model: Fitted ARIMA model
        steps: Number of steps to forecast
        alpha: Significance level for confidence intervals
    
    Returns:
        pd.DataFrame: Forecast with confidence intervals
    """
    forecast = model.forecast(steps=steps)
    forecast_summary = model.get_forecast(steps=steps)
    confidence_int = forecast_summary.conf_int(alpha=alpha)
    
    result = pd.DataFrame({
        'forecast': forecast,
        'lower_bound': confidence_int.iloc[:, 0],
        'upper_bound': confidence_int.iloc[:, 1]
    })
    
    return result


def calculate_forecast_metrics(y_true: pd.Series,
                              y_pred: pd.Series) -> Dict[str, float]:
    """
    Calculate forecast accuracy metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Dict: Dictionary of metrics
    """
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    return {
        'MSE': mse,
        'RMSE': rmse,
        'MAE': mae,
        'MAPE': mape
    }


def simple_moving_average(series: pd.Series,
                         window: int = 7,
                         forecast_periods: int = 7) -> pd.Series:
    """
    Simple moving average forecast.
    
    Args:
        series: Time series data
        window: Window size for moving average
        forecast_periods: Number of periods to forecast
    
    Returns:
        pd.Series: Forecast values
    """
    # Calculate the moving average for the last window
    last_average = series.iloc[-window:].mean()
    
    # Create forecast (simple: use last average for all periods)
    forecast_index = pd.date_range(
        start=series.index[-1] + pd.Timedelta(days=1),
        periods=forecast_periods,
        freq='D'
    )
    
    forecast = pd.Series([last_average] * forecast_periods, index=forecast_index)
    
    return forecast