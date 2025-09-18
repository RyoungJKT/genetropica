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
import statsmodels.api as sm
from scipy import stats as scipy_stats


def make_forecast(df: pd.DataFrame, 
                  horizon_months: int = 2,
                  rainfall_lag: int = 1,
                  confidence_level: float = 0.95) -> pd.DataFrame:
    """
    Create a simple seasonal naive + rainfall regression forecast.
    
    Model: y_t = season_mean(month_t) + beta * rainfall_{t-lag} + error
    
    Args:
        df: DataFrame with date index and columns: cases, rainfall_mm, temperature_c
        horizon_months: Number of months to forecast ahead
        rainfall_lag: Lag months for rainfall effect (1 or 2)
        confidence_level: Confidence level for prediction intervals
        
    Returns:
        DataFrame with columns: date, yhat, yhat_lower, yhat_upper, model_notes
    """
    # Ensure we have a datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame must have a DateTimeIndex")
    
    # Aggregate to monthly if needed (sum cases, average climate)
    monthly = df.groupby(pd.Grouper(freq='MS')).agg({
        'cases': 'sum',
        'rainfall_mm': 'mean',
        'temperature_c': 'mean'
    }).dropna()
    
    if len(monthly) < 12:
        # Not enough data for seasonal model
        return _make_simple_forecast(monthly, horizon_months)
    
    # Extract seasonal pattern (average by month)
    monthly['month'] = monthly.index.month
    seasonal_pattern = monthly.groupby('month')['cases'].mean()
    
    # Create lagged rainfall feature
    monthly[f'rainfall_lag{rainfall_lag}'] = monthly['rainfall_mm'].shift(rainfall_lag)
    
    # Prepare training data (remove NaN from lag)
    train_data = monthly.dropna().copy()  # Use .copy() to avoid SettingWithCopyWarning
    
    if len(train_data) < 6:
        # Not enough data after lag
        return _make_simple_forecast(monthly, horizon_months)
    
    # Calculate seasonal baseline for each observation
    train_data.loc[:, 'seasonal_baseline'] = train_data['month'].map(seasonal_pattern)
    
    # Calculate deseasonalized cases
    train_data.loc[:, 'cases_deseasonalized'] = train_data['cases'] - train_data['seasonal_baseline']
    
    # Fit linear regression on deseasonalized cases vs lagged rainfall
    X = sm.add_constant(train_data[f'rainfall_lag{rainfall_lag}'])
    y = train_data['cases_deseasonalized']
    
    try:
        model = sm.OLS(y, X).fit()
        
        # Get model parameters using iloc for position-based indexing
        intercept = model.params.iloc[0] if len(model.params) > 0 else 0
        beta_rainfall = model.params.iloc[1] if len(model.params) > 1 else 0
        
        # Calculate residual standard error for prediction intervals
        residual_std = np.sqrt(model.mse_resid)
        
    except:
        # Fallback if regression fails
        intercept = 0
        beta_rainfall = 0
        residual_std = train_data['cases'].std()
    
    # Generate future dates
    last_date = monthly.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=horizon_months,
        freq='MS'
    )
    
    # Make predictions
    predictions = []
    
    for date in future_dates:
        # Get seasonal component
        month = date.month
        seasonal_component = seasonal_pattern.get(month, seasonal_pattern.mean())
        
        # Use recent rainfall average for future (simplified assumption)
        recent_rainfall = monthly['rainfall_mm'].tail(3).mean()
        
        # Calculate prediction
        yhat = seasonal_component + intercept + beta_rainfall * recent_rainfall
        yhat = max(0, yhat)  # Ensure non-negative
        
        # Calculate prediction intervals
        z_score = scipy_stats.norm.ppf((1 + confidence_level) / 2)
        margin = z_score * residual_std
        
        yhat_lower = max(0, yhat - margin)
        yhat_upper = yhat + margin
        
        predictions.append({
            'date': date,
            'yhat': yhat,
            'yhat_lower': yhat_lower,
            'yhat_upper': yhat_upper,
            'model_notes': f'Seasonal naive + rainfall (lag={rainfall_lag}mo)'
        })
    
    return pd.DataFrame(predictions)


def _make_simple_forecast(monthly: pd.DataFrame, horizon_months: int) -> pd.DataFrame:
    """
    Fallback simple forecast when not enough data for seasonal model.
    """
    # Use simple moving average
    recent_avg = monthly['cases'].tail(3).mean() if len(monthly) >= 3 else monthly['cases'].mean()
    recent_std = monthly['cases'].tail(6).std() if len(monthly) >= 6 else monthly['cases'].std()
    
    if pd.isna(recent_avg):
        recent_avg = 100  # Default fallback
    if pd.isna(recent_std):
        recent_std = 50
    
    last_date = monthly.index[-1] if len(monthly) > 0 else pd.Timestamp.now().floor('MS')
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=horizon_months,
        freq='MS'
    )
    
    predictions = []
    z_score = 1.96  # 95% confidence
    
    for date in future_dates:
        predictions.append({
            'date': date,
            'yhat': recent_avg,
            'yhat_lower': max(0, recent_avg - z_score * recent_std),
            'yhat_upper': recent_avg + z_score * recent_std,
            'model_notes': 'Simple moving average (insufficient data for seasonal)'
        })
    
    return pd.DataFrame(predictions)


def backtest_forecast(df: pd.DataFrame, 
                      test_months: int = 12,
                      rainfall_lag: int = 1) -> Dict[str, float]:
    """
    Perform rolling backtest to calculate MAE and RMSE.
    
    Args:
        df: Historical data
        test_months: Number of months to use for backtesting
        rainfall_lag: Lag to use in the model
        
    Returns:
        Dict with 'mae' and 'rmse' values
    """
    # Ensure we have enough data
    monthly = df.groupby(pd.Grouper(freq='MS')).agg({
        'cases': 'sum',
        'rainfall_mm': 'mean',
        'temperature_c': 'mean'
    }).dropna()
    
    if len(monthly) < test_months + 12:
        # Not enough data for meaningful backtest
        return {'mae': np.nan, 'rmse': np.nan, 'n_tests': 0}
    
    actuals = []
    predictions = []
    
    # Rolling one-step-ahead predictions
    for i in range(test_months):
        # Split data
        test_idx = len(monthly) - test_months + i
        train_df = monthly.iloc[:test_idx]
        actual = monthly.iloc[test_idx]['cases']
        
        # Make one-month forecast
        try:
            forecast_df = make_forecast(train_df, horizon_months=1, rainfall_lag=rainfall_lag)
            if len(forecast_df) > 0:
                pred = forecast_df.iloc[0]['yhat']
                actuals.append(actual)
                predictions.append(pred)
        except:
            continue
    
    if len(actuals) > 0:
        actuals = np.array(actuals)
        predictions = np.array(predictions)
        
        mae = mean_absolute_error(actuals, predictions)
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        
        return {
            'mae': mae,
            'rmse': rmse,
            'n_tests': len(actuals)
        }
    
    return {'mae': np.nan, 'rmse': np.nan, 'n_tests': 0}


# Keep original functions for compatibility

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
    result = seasonal_decompose(series, model=model, period=period, extrapolate_trend='freq')
    
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
    
    # Avoid division by zero for MAPE
    mask = y_true != 0
    if mask.any():
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    else:
        mape = np.nan
    
    return {
        'MSE': mse,
        'RMSE': rmse,
        'MAE': mae,
        'MAPE': mape
    }