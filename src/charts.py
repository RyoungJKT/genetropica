"""
Visualization utilities for GeneTropica.
Creates interactive charts using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from scipy import stats


def create_serotype_stacked_area(df: pd.DataFrame,
                                 serotype_palette: Dict[str, str],
                                 smooth: bool = False,
                                 window: int = 3) -> go.Figure:
    """
    Create a stacked area chart showing serotype composition over time.
    
    Args:
        df: DataFrame with date index and denv1_share..denv4_share columns
        serotype_palette: Color mapping for serotypes
        smooth: Whether to apply smoothing
        window: Window size for smoothing
        
    Returns:
        go.Figure: Plotly stacked area chart
    """
    # Aggregate by month (sum cases, average shares)
    monthly = df.groupby(df.index).agg({
        'denv1_share': 'mean',
        'denv2_share': 'mean',
        'denv3_share': 'mean',
        'denv4_share': 'mean'
    })
    
    # Normalize to ensure sum = 1
    share_cols = ['denv1_share', 'denv2_share', 'denv3_share', 'denv4_share']
    monthly[share_cols] = monthly[share_cols].div(monthly[share_cols].sum(axis=1), axis=0)
    
    # Apply smoothing if requested
    if smooth and len(monthly) > window:
        for col in share_cols:
            monthly[col] = monthly[col].rolling(window=window, center=True).mean()
        # Re-normalize after smoothing
        monthly[share_cols] = monthly[share_cols].div(monthly[share_cols].sum(axis=1), axis=0)
        monthly = monthly.dropna()
    
    # Create stacked area chart
    fig = go.Figure()
    
    # Add traces for each serotype
    for i, (serotype_num, color) in enumerate([
        ('1', serotype_palette.get('DENV1', '#FF6B6B')),
        ('2', serotype_palette.get('DENV2', '#4ECDC4')),
        ('3', serotype_palette.get('DENV3', '#45B7D1')),
        ('4', serotype_palette.get('DENV4', '#96CEB4'))
    ]):
        fig.add_trace(go.Scatter(
            x=monthly.index,
            y=monthly[f'denv{serotype_num}_share'],
            mode='lines',
            name=f'DENV{serotype_num}',
            stackgroup='one',
            fillcolor=color,
            line=dict(width=0.5, color=color),
            hovertemplate='%{y:.1%}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Serotype Composition Over Time",
        xaxis_title="Date",
        yaxis_title="Proportion",
        yaxis=dict(
            tickformat='.0%',
            range=[0, 1]
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400,
        margin=dict(l=50, r=20, t=70, b=50)
    )
    
    return fig


def create_cases_climate_dual_axis(df: pd.DataFrame,
                                   lag_months: int = 0) -> tuple[go.Figure, float, float]:
    """
    Create a dual-axis chart with cases (bars) and climate variables (lines).
    
    Args:
        df: DataFrame with date index, cases, rainfall_mm, temperature_c
        lag_months: Number of months to lag rainfall for correlation
        
    Returns:
        Tuple of (figure, rainfall_correlation, temperature_correlation)
    """
    # Aggregate by month
    monthly = df.groupby(df.index).agg({
        'cases': 'sum',
        'rainfall_mm': 'mean',
        'temperature_c': 'mean'
    })
    
    # Apply lag to rainfall
    rainfall_lagged = monthly['rainfall_mm'].shift(lag_months)
    
    # Calculate correlations
    rainfall_corr = 0.0
    temp_corr = 0.0
    
    if len(monthly) > 1:
        # Only calculate where we have non-null values after lag
        valid_mask = rainfall_lagged.notna() & monthly['cases'].notna()
        if valid_mask.sum() > 1:
            rainfall_corr = monthly['cases'][valid_mask].corr(rainfall_lagged[valid_mask])
        
        temp_mask = monthly['temperature_c'].notna() & monthly['cases'].notna()
        if temp_mask.sum() > 1:
            temp_corr = monthly['cases'][temp_mask].corr(monthly['temperature_c'])
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add cases as bars (primary y-axis)
    fig.add_trace(go.Bar(
        x=monthly.index,
        y=monthly['cases'],
        name='Cases',
        marker_color='rgba(99, 110, 250, 0.6)',
        yaxis='y',
        hovertemplate='Cases: %{y:,.0f}<extra></extra>'
    ))
    
    # Add rainfall line (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=monthly.index,
        y=rainfall_lagged if lag_months > 0 else monthly['rainfall_mm'],
        mode='lines+markers',
        name=f'Rainfall{f" (lag {lag_months}mo)" if lag_months > 0 else ""}',
        line=dict(color='#00CED1', width=2),
        marker=dict(size=6),
        yaxis='y2',
        hovertemplate='Rainfall: %{y:.1f} mm<extra></extra>'
    ))
    
    # Add temperature line (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=monthly.index,
        y=monthly['temperature_c'],
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#FF6347', width=2),
        marker=dict(size=6),
        yaxis='y2',
        hovertemplate='Temperature: %{y:.1f} °C<extra></extra>'
    ))
    
    # Update layout with dual axes
    fig.update_layout(
        title="Dengue Cases vs Climate Variables",
        xaxis_title="Date",
        yaxis=dict(
            title="Cases",
            title_font=dict(color='#636EFA'),
            tickfont=dict(color='#636EFA'),
            side='left'
        ),
        yaxis2=dict(
            title="Climate (mm / °C)",
            title_font=dict(color='#00CED1'),
            tickfont=dict(color='#00CED1'),
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400,
        margin=dict(l=50, r=50, t=70, b=50)
    )
    
    return fig, rainfall_corr, temp_corr


# Keep original functions for compatibility

def create_time_series(df: pd.DataFrame,
                      x_col: str,
                      y_col: str,
                      title: str = "Time Series",
                      height: int = 400) -> go.Figure:
    """
    Create an interactive time series plot.
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis (typically date)
        y_col: Column for y-axis
        title: Chart title
        height: Chart height in pixels
    
    Returns:
        go.Figure: Plotly figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines+markers',
        name=y_col,
        line=dict(width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
        height=height,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig


def create_heatmap(df: pd.DataFrame,
                  title: str = "Heatmap",
                  height: int = 500,
                  colorscale: str = "Viridis") -> go.Figure:
    """
    Create a heatmap visualization.
    
    Args:
        df: Input DataFrame (should be pivot table format)
        title: Chart title
        height: Chart height in pixels
        colorscale: Plotly colorscale name
    
    Returns:
        go.Figure: Plotly figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=colorscale,
        colorbar=dict(title="Value")
    ))
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="",
        yaxis_title=""
    )
    
    return fig


def create_correlation_matrix(df: pd.DataFrame,
                             columns: Optional[List[str]] = None,
                             title: str = "Correlation Matrix",
                             height: int = 600) -> go.Figure:
    """
    Create a correlation matrix heatmap.
    
    Args:
        df: Input DataFrame
        columns: Columns to include (None for all numeric)
        title: Chart title
        height: Chart height in pixels
    
    Returns:
        go.Figure: Plotly figure
    """
    if columns is None:
        columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    corr_matrix = df[columns].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="",
        yaxis_title=""
    )
    
    return fig


def create_bar_chart(df: pd.DataFrame,
                    x_col: str,
                    y_col: str,
                    title: str = "Bar Chart",
                    orientation: str = 'v',
                    height: int = 400) -> go.Figure:
    """
    Create a bar chart.
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis
        y_col: Column for y-axis
        title: Chart title
        orientation: 'v' for vertical, 'h' for horizontal
        height: Chart height in pixels
    
    Returns:
        go.Figure: Plotly figure
    """
    fig = px.bar(df, x=x_col, y=y_col, orientation=orientation, title=title)
    
    fig.update_layout(
        height=height,
        showlegend=False,
        hovermode='x' if orientation == 'v' else 'y'
    )
    
    return fig