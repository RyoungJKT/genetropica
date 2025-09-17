"""
Visualization utilities for GeneTropica.
Creates interactive charts using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, List, Dict, Any


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