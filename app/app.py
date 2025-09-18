"""
GeneTropica - Main Streamlit Application
Dengue · Climate · Forecast (MVP)
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import io

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.transforms import (
    load_geo, 
    load_features, 
    build_province_month_df,
    compute_dominant_serotype,
    SEROTYPE_PALETTE
)
from src.charts import (
    create_serotype_stacked_area,
    create_cases_climate_dual_axis
)
from src.forecast import (
    make_forecast,
    backtest_forecast
)


@st.cache_resource
def get_fitted_model_params(df: pd.DataFrame):
    """Cache expensive model fitting operations."""
    # This would cache any expensive model parameters
    # Currently placeholder for future optimization
    return {"cached": True, "timestamp": datetime.now()}


def create_choropleth_map(df_month, gdf, selected_provinces):
    """
    Create a Plotly choropleth map colored by dominant serotype.
    Falls back to scatter map if GeoJSON not available.
    
    Args:
        df_month: DataFrame for a specific month
        gdf: GeoDataFrame with province geometries
        selected_provinces: List of selected province IDs
    
    Returns:
        Plotly figure
    """
    # Check if we have geometry data
    has_geometry = 'geometry' in gdf.columns and gdf['geometry'].notna().any()
    
    if not has_geometry:
        # Fallback to scatter map if no geometry available
        return create_simple_scatter_map(df_month, gdf, selected_provinces)
    
    # Filter GeoDataFrame to selected provinces
    gdf_filtered = gdf[gdf['province_id'].isin(selected_provinces)].copy()
    
    # Merge data with geometries
    if len(df_month) > 0:
        # Ensure df_month has province_id for merging
        df_month = df_month.reset_index()
        merged = gdf_filtered.merge(
            df_month[['province_id', 'cases', 'rainfall_mm', 'temperature_c', 
                     'dominant_serotype', 'denv1_share', 'denv2_share', 
                     'denv3_share', 'denv4_share']],
            on='province_id',
            how='left'
        )
    else:
        merged = gdf_filtered.copy()
        merged['dominant_serotype'] = 'No Data'
        merged['cases'] = 0
        merged['rainfall_mm'] = 0
        merged['temperature_c'] = 0
        for i in range(1, 5):
            merged[f'denv{i}_share'] = 0
    
    # Convert GeoDataFrame to GeoJSON for Plotly
    try:
        geojson_dict = json.loads(gdf_filtered.to_json())
    except:
        # If conversion fails, use scatter map
        return create_simple_scatter_map(df_month, gdf, selected_provinces)
    
    # Create hover text
    merged['hover_text'] = merged.apply(
        lambda row: (
            f"<b>{row['province_name']}</b><br>"
            f"Cases: {row['cases']:,}<br>"
            f"Rainfall: {row['rainfall_mm']:.1f} mm<br>"
            f"Temperature: {row['temperature_c']:.1f} °C<br>"
            f"<br><b>Serotype Shares:</b><br>"
            f"DENV1: {row['denv1_share']:.1%}<br>"
            f"DENV2: {row['denv2_share']:.1%}<br>"
            f"DENV3: {row['denv3_share']:.1%}<br>"
            f"DENV4: {row['denv4_share']:.1%}"
        ) if pd.notna(row['cases']) else f"<b>{row['province_name']}</b><br>No data",
        axis=1
    )
    
    # Create color mapping
    color_discrete_map = SEROTYPE_PALETTE.copy()
    color_discrete_map['No Data'] = '#E0E0E0'
    
    # Create the choropleth
    fig = px.choropleth(
        merged,
        geojson=geojson_dict,
        locations='province_id',
        color='dominant_serotype',
        color_discrete_map=color_discrete_map,
        featureidkey="properties.province_id",
        hover_name='province_name',
        hover_data={
            'province_id': False,
            'dominant_serotype': False
        },
        labels={'dominant_serotype': 'Dominant Serotype'},
    )
    
    # Update traces to use custom hover text
    fig.update_traces(
        customdata=merged[['hover_text']].values,
        hovertemplate='%{customdata[0]}<extra></extra>'
    )
    
    # Update layout for Indonesia focus with better zoom
    fig.update_geos(
        center={"lat": -7.0, "lon": 110.0},
        projection_scale=8,  # Reduced from 25 for better view
        showcountries=True,
        countrycolor="#CCCCCC",
        showcoastlines=True,
        coastlinecolor="#999999",
        showland=True,
        landcolor="#FAFAFA",
        showocean=True,
        oceancolor="#E8F4F8",
        fitbounds="locations",
        visible=True,
        resolution=50,  # Higher resolution
        scope="asia"    # Focus on Asia
    )
    
    fig.update_layout(
        title="Dengue Dominant Serotype by Province",
        height=600,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        legend=dict(
            title="Dominant Serotype",
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#CCCCCC",
            borderwidth=1
        ),
        geo=dict(
            showframe=True,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig


def create_simple_scatter_map(df_month, gdf, selected_provinces):
    """
    Create a simple scatter map as an alternative visualization.
    Uses circles at province centers colored by dominant serotype.
    """
    # Filter GeoDataFrame to selected provinces
    gdf_filtered = gdf[gdf['province_id'].isin(selected_provinces)].copy()
    
    # Merge data
    if len(df_month) > 0:
        df_month = df_month.reset_index()
        merged = gdf_filtered.merge(
            df_month[['province_id', 'cases', 'rainfall_mm', 'temperature_c', 
                     'dominant_serotype', 'denv1_share', 'denv2_share', 
                     'denv3_share', 'denv4_share']],
            on='province_id',
            how='left'
        )
    else:
        merged = gdf_filtered.copy()
        merged['dominant_serotype'] = 'No Data'
        merged['cases'] = 0
        merged['rainfall_mm'] = 0
        merged['temperature_c'] = 0
    
    # Create hover text
    merged['hover_text'] = merged.apply(
        lambda row: (
            f"<b>{row['province_name']}</b><br>"
            f"Cases: {row['cases']:,}<br>"
            f"Rainfall: {row['rainfall_mm']:.1f} mm<br>"
            f"Temperature: {row['temperature_c']:.1f} °C<br>"
            f"<br><b>Serotype Shares:</b><br>"
            f"DENV1: {row.get('denv1_share', 0):.1%}<br>"
            f"DENV2: {row.get('denv2_share', 0):.1%}<br>"
            f"DENV3: {row.get('denv3_share', 0):.1%}<br>"
            f"DENV4: {row.get('denv4_share', 0):.1%}"
        ) if pd.notna(row['cases']) else f"<b>{row['province_name']}</b><br>No data",
        axis=1
    )
    
    # Create scatter map
    fig = px.scatter_geo(
        merged,
        lat='lat',
        lon='lon',
        color='dominant_serotype',
        size='cases',
        hover_name='province_name',
        color_discrete_map=SEROTYPE_PALETTE,
        size_max=50,
        title="Dengue Cases by Province (Bubble Map)"
    )
    
    # Update hover template
    fig.update_traces(
        customdata=merged[['hover_text']].values,
        hovertemplate='%{customdata[0]}<extra></extra>',
        marker=dict(
            line=dict(width=1, color='white'),
            sizemin=10
        )
    )
    
    # Focus on Indonesia
    fig.update_geos(
        center={"lat": -6.5, "lon": 107.0},
        projection_scale=5,
        showcountries=True,
        countrycolor="#CCCCCC",
        showcoastlines=True,
        coastlinecolor="#999999",
        showland=True,
        landcolor="#FAFAFA",
        showocean=True,
        oceancolor="#E8F4F8",
        fitbounds="locations"
    )
    
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig


def main():
    """Main application entry point."""
    
    # Page configuration - MUST BE FIRST ST COMMAND
    st.set_page_config(
        page_title="GeneTropica",
        page_icon="🦟",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling and WCAG compliance
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .ksp-item {
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 500;
        text-align: center;
        display: block;
        white-space: nowrap;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .ksp-serotypes {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .ksp-climate {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
    }
    .ksp-forecast {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }
    .province-badge {
        background-color: #E8F4F8;
        color: #2C3E50;
        border: 1px solid #BDC3C7;
    }
    .month-badge {
        background-color: #FFF5E6;
        color: #8B4513;
        border: 1px solid #D2691E;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title with custom styling
    st.markdown('<h1 class="main-header">🦟 GeneTropica — Dengue · Climate · Forecast (MVP) by Russell Young</h1>', 
                unsafe_allow_html=True)
    
    # Key Selling Points (KSPs) using Streamlit columns for better alignment
    ksp_col1, ksp_col2, ksp_col3 = st.columns(3)
    
    with ksp_col1:
        st.markdown('<div class="ksp-item ksp-serotypes">🧬 Serotypes/Lineages</div>', unsafe_allow_html=True)
    
    with ksp_col2:
        st.markdown('<div class="ksp-item ksp-climate">🌡️ Climate Correlation</div>', unsafe_allow_html=True)
    
    with ksp_col3:
        st.markdown('<div class="ksp-item ksp-forecast">📈 Forecast Models</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing after KSPs
    
    # Load data with caching
    try:
        with st.spinner('Loading data...'):
            gdf = load_geo()
            df = load_features()
        
        # Get date range from data
        min_year = df.index.year.min()
        max_year = df.index.year.max()
        available_months = df.index.unique().sort_values()
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please run `python -m src.data_io --make-mock` to generate mock data.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Year range slider
        year_range = st.slider(
            "Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            help="Select the range of years to include"
        )
        
        # Province multiselect
        all_provinces = sorted(df['province_id'].unique())
        province_names = {
            'DKI': 'DKI Jakarta',
            'JABAR': 'West Java',
            'JATENG': 'Central Java',
            'JATIM': 'East Java',
            'BANTEN': 'Banten',
            'DIY': 'Yogyakarta'
        }
        
        selected_provinces = st.multiselect(
            "Provinces",
            options=all_provinces,
            default=all_provinces,
            format_func=lambda x: province_names.get(x, x),
            help="Select provinces to display"
        )
        
        # Serotype multiselect
        all_serotypes = ['DENV1', 'DENV2', 'DENV3', 'DENV4']
        selected_serotypes = st.multiselect(
            "Serotypes",
            options=all_serotypes,
            default=all_serotypes,
            help="Filter by dominant serotype"
        )
        
        st.divider()
        
        # Map type selector
        map_type = st.radio(
            "Map Type",
            options=["Bubble Map", "Choropleth"],
            index=0,  # Default to Bubble Map
            help="Bubble map recommended - shows all provinces clearly"
        )
        
        st.divider()
        
        # Sources & Ethics section
        with st.expander("📚 Sources & Ethics"):
            st.markdown("""
            ### Data Sources
            
            **⚠️ Mock Data Notice**
            
            This demo currently uses **synthetic mock data** for demonstration purposes. 
            The data is programmatically generated to show realistic patterns but does not 
            represent actual dengue cases or climate measurements.
            
            ### Future Data Plans
            
            We plan to integrate real public health data from:
            - **WHO**: Global dengue surveillance data
            - **BMKG**: Indonesian meteorological data
            - **Ministry of Health**: Provincial case reports
            - **GISAID/GenBank**: Genetic sequences
            
            ### Ethical Considerations
            
            - **Privacy**: No patient-identifiable information
            - **Transparency**: Clear labeling of data sources
            - **Accuracy**: Validation against published studies
            - **Access**: Open-source code and public data only
            
            ### Responsible Use
            
            This tool is for **educational and research purposes only**.
            Not intended for clinical decision-making.
            
            ### Contact
            
            For questions about data or methods:
            genetropica@example.com
            """)
        
        st.divider()
        st.caption("Data filters update visualizations in real-time")
    
    # Filter data based on selections
    if selected_provinces and selected_serotypes:
        df_filtered = build_province_month_df(
            province=selected_provinces,
            year_range=year_range,
            serotypes=selected_serotypes
        )
        
        if len(df_filtered) == 0:
            st.warning("No data matches the selected filters. Try adjusting your selection.")
            return
            
        # Get available months after filtering
        available_months_filtered = df_filtered.index.unique().sort_values()
        
        # Helper badges showing current selection
        badge_col1, badge_col2, badge_col3 = st.columns([2, 2, 6])
        with badge_col1:
            provinces_text = f"{len(selected_provinces)} province{'s' if len(selected_provinces) != 1 else ''}"
            st.markdown(f'<span class="status-badge province-badge">📍 {provinces_text} selected</span>', 
                       unsafe_allow_html=True)
        
        with badge_col2:
            year_text = f"{year_range[0]}–{year_range[1]}"
            st.markdown(f'<span class="status-badge month-badge">📅 Years: {year_text}</span>', 
                       unsafe_allow_html=True)
        
        # Main content area
        st.header("🗺️ Dengue Serotype Distribution Map")
        
        # Month selector (slider for animation)
        if len(available_months_filtered) > 0:
            # Format months for display
            month_options = {
                i: month.strftime('%B %Y') 
                for i, month in enumerate(available_months_filtered)
            }
            
            # Default to most recent month
            default_index = len(month_options) - 1
            
            selected_month_index = st.select_slider(
                "📅 Select Month",
                options=list(month_options.keys()),
                value=default_index,
                format_func=lambda x: month_options[x],
                help="Slide to animate through time"
            )
            
            selected_month = available_months_filtered[selected_month_index]
            
            # Display selected month prominently
            st.markdown(f"### Showing data for: **{selected_month.strftime('%B %Y')}**")
            
            # Get data for selected month
            df_month = df_filtered[df_filtered.index == selected_month]
            
            # Download button for filtered data
            col_map, col_download = st.columns([5, 1])
            
            with col_download:
                # Prepare CSV for download
                csv_buffer = io.StringIO()
                df_filtered.to_csv(csv_buffer, index=True)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Data",
                    data=csv_data,
                    file_name=f"genetropica_data_{selected_month.strftime('%Y%m')}.csv",
                    mime="text/csv",
                    help="Download the filtered dataset as CSV"
                )
            
            # Create two columns for map and stats
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create and display the map based on selection
                if map_type == "Bubble Map":
                    fig = create_simple_scatter_map(df_month, gdf, selected_provinces)
                else:
                    fig = create_choropleth_map(df_month, gdf, selected_provinces)
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Display statistics for selected month
                st.markdown("### 📊 Monthly Statistics")
                
                if len(df_month) > 0:
                    total_cases = df_month['cases'].sum()
                    avg_rainfall = df_month['rainfall_mm'].mean()
                    avg_temp = df_month['temperature_c'].mean()
                    
                    st.metric("Total Cases", f"{total_cases:,}")
                    st.metric("Avg Rainfall", f"{avg_rainfall:.1f} mm")
                    st.metric("Avg Temperature", f"{avg_temp:.1f} °C")
                    
                    # Serotype distribution
                    st.markdown("#### Serotype Distribution")
                    serotype_counts = df_month['dominant_serotype'].value_counts()
                    for serotype, count in serotype_counts.items():
                        color = SEROTYPE_PALETTE.get(serotype, '#888')
                        st.markdown(
                            f"<span style='color: {color}'>●</span> **{serotype}**: {count} provinces",
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No data for selected filters")
            
            # Legend for serotype colors with WCAG compliant colors
            st.markdown("---")
            st.markdown("### 🎨 Serotype Color Legend")
            legend_cols = st.columns(4)
            for i, (serotype, color) in enumerate(SEROTYPE_PALETTE.items()):
                with legend_cols[i]:
                    st.markdown(
                        f"<div style='text-align: center;'>"
                        f"<span style='color: {color}; font-size: 24px;'>●</span><br>"
                        f"<b>{serotype}</b>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
            
            # Trends and Climate Analysis Section
            st.markdown("---")
            st.header("📈 Trends & Climate Analysis")
            
            # Add smoothing option and lag slider in columns
            control_col1, control_col2, control_col3 = st.columns([1, 1, 2])
            
            with control_col1:
                smooth_data = st.checkbox("Smooth serotype data", value=False, 
                                         help="Apply 3-month rolling average to serotype composition")
            
            with control_col2:
                lag_months = st.slider("Rainfall lag (months)", 
                                      min_value=0, max_value=3, value=0,
                                      help="Shift rainfall data to find lagged correlations")
            
            # Two column layout for charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("Serotype Composition Over Time")
                
                # Create stacked area chart
                fig_serotype = create_serotype_stacked_area(
                    df_filtered,
                    SEROTYPE_PALETTE,
                    smooth=smooth_data,
                    window=3
                )
                st.plotly_chart(fig_serotype, use_container_width=True)
                
                # Validation note
                st.caption("📊 Stacked areas sum to 100% at each time point")
            
            with chart_col2:
                st.subheader("Cases vs Climate Variables")
                
                # Create dual-axis chart
                fig_climate, rainfall_corr, temp_corr = create_cases_climate_dual_axis(
                    df_filtered,
                    lag_months=lag_months
                )
                st.plotly_chart(fig_climate, use_container_width=True)
                
                # Display correlations
                st.caption(f"📊 Correlations with cases:")
                corr_col1, corr_col2 = st.columns(2)
                with corr_col1:
                    corr_text = f"Rainfall (lag {lag_months}mo): **{rainfall_corr:.3f}**" if not pd.isna(rainfall_corr) else "Rainfall: No data"
                    st.caption(f"💧 {corr_text}")
                with corr_col2:
                    temp_text = f"Temperature: **{temp_corr:.3f}**" if not pd.isna(temp_corr) else "Temperature: No data"
                    st.caption(f"🌡️ {temp_text}")
            
            # Forecast Section
            st.markdown("---")
            st.header("📊 Forecast (Prototype)")
            
            # Disclaimer
            st.warning("""
            ⚠️ **Educational Prototype Disclaimer**
            
            This forecast is a simple statistical model for educational purposes only. 
            It is NOT intended for clinical decision-making or public health planning.
            Always consult qualified health professionals for medical advice.
            """)
            
            # Forecast controls
            forecast_col1, forecast_col2, forecast_col3 = st.columns([1, 1, 2])
            
            with forecast_col1:
                forecast_horizon = st.slider(
                    "Forecast horizon (months)",
                    min_value=1,
                    max_value=3,
                    value=2,
                    help="Number of months to forecast ahead"
                )
            
            with forecast_col2:
                forecast_lag = st.selectbox(
                    "Rainfall lag for model",
                    options=[1, 2],
                    help="Lag months for rainfall effect in the model"
                )
            
            # Generate forecast with caching
            try:
                # Get forecast
                forecast_df = make_forecast(
                    df_filtered,
                    horizon_months=forecast_horizon,
                    rainfall_lag=forecast_lag
                )
                
                # Get backtest metrics
                metrics = backtest_forecast(
                    df_filtered,
                    test_months=min(12, len(df_filtered) // 2),
                    rainfall_lag=forecast_lag
                )
                
                # Prepare data for visualization
                # Get last 12 months of actuals
                last_12_months = df_filtered.tail(12).copy()
                last_12_months = last_12_months.groupby(last_12_months.index).agg({
                    'cases': 'sum'
                })
                
                # Create forecast visualization
                fig_forecast = go.Figure()
                
                # Add actual cases
                fig_forecast.add_trace(go.Scatter(
                    x=last_12_months.index,
                    y=last_12_months['cases'],
                    mode='lines+markers',
                    name='Actual Cases',
                    line=dict(color='#2E86AB', width=2),
                    marker=dict(size=6)
                ))
                
                # Add forecast with confidence interval
                if len(forecast_df) > 0:
                    # Add forecast line
                    fig_forecast.add_trace(go.Scatter(
                        x=forecast_df['date'],
                        y=forecast_df['yhat'],
                        mode='lines+markers',
                        name='Forecast',
                        line=dict(color='#A23B72', width=2, dash='dash'),
                        marker=dict(size=6)
                    ))
                    
                    # Add confidence interval
                    x_area = list(forecast_df['date']) + list(forecast_df['date'][::-1])
                    y_area = list(forecast_df['yhat_upper']) + list(forecast_df['yhat_lower'][::-1])
                    
                    fig_forecast.add_trace(go.Scatter(
                        x=x_area,
                        y=y_area,
                        fill='toself',
                        fillcolor='rgba(162, 59, 114, 0.2)',
                        line=dict(color='rgba(162, 59, 114, 0)'),
                        name='95% Confidence Interval',
                        showlegend=True,
                        hoverinfo='skip'
                    ))
                    
                    # Connect actual to forecast with a dotted line
                    if len(last_12_months) > 0 and len(forecast_df) > 0:
                        fig_forecast.add_trace(go.Scatter(
                            x=[last_12_months.index[-1], forecast_df['date'].iloc[0]],
                            y=[last_12_months['cases'].iloc[-1], forecast_df['yhat'].iloc[0]],
                            mode='lines',
                            line=dict(color='gray', width=1, dash='dot'),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                
                # Update layout
                fig_forecast.update_layout(
                    title="Dengue Cases Forecast",
                    xaxis_title="Date",
                    yaxis_title="Cases",
                    hovermode='x unified',
                    showlegend=True,
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis=dict(
                        gridcolor='#E0E0E0',
                        showgrid=True,
                        zeroline=False
                    ),
                    yaxis=dict(
                        gridcolor='#E0E0E0',
                        showgrid=True,
                        zeroline=False
                    )
                )
                
                # Display forecast chart
                st.plotly_chart(fig_forecast, use_container_width=True)
                
                # Display metrics
                col_metric1, col_metric2, col_metric3 = st.columns(3)
                
                with col_metric1:
                    mae_val = metrics.get('mae', np.nan)
                    if not pd.isna(mae_val):
                        st.metric("MAE (Backtest)", f"{mae_val:.1f} cases")
                    else:
                        st.metric("MAE (Backtest)", "Insufficient data")
                
                with col_metric2:
                    rmse_val = metrics.get('rmse', np.nan)
                    if not pd.isna(rmse_val):
                        st.metric("RMSE (Backtest)", f"{rmse_val:.1f} cases")
                    else:
                        st.metric("RMSE (Backtest)", "Insufficient data")
                
                with col_metric3:
                    n_tests = metrics.get('n_tests', 0)
                    st.metric("Backtest Samples", f"{n_tests} months")
                
                # Model description
                if len(forecast_df) > 0:
                    st.info(f"**Model:** {forecast_df.iloc[0]['model_notes']}")
                
            except Exception as e:
                st.error(f"Error generating forecast: {str(e)}")
                st.info("This may happen with limited data. Try selecting different provinces or date ranges.")
            
            # Phylogenetics Section
            st.markdown("---")
            with st.expander("🧬 Phylogenetics (Coming Soon)"):
                col_phylo1, col_phylo2 = st.columns([1, 2])
                
                with col_phylo1:
                    # Display placeholder image
                    try:
                        from PIL import Image
                        phylo_img_path = Path(__file__).parent.parent / "assets" / "phylo_placeholder.png"
                        if phylo_img_path.exists():
                            img = Image.open(phylo_img_path)
                            st.image(img, caption="Phylogenetic Tree Visualization (Placeholder)", width='stretch')
                        else:
                            st.info("Phylogenetic tree visualization will appear here")
                    except:
                        st.info("Phylogenetic tree visualization will appear here")
                
                with col_phylo2:
                    st.markdown("""
                    ### Planned Phylogenetic Analysis Pipeline
                    
                    **Coming in future versions:**
                    
                    1. **Sequence Alignment** (MAFFT)
                       - Multiple sequence alignment of dengue genomes
                       - Automatic detection of serotype-specific regions
                    
                    2. **Quality Control** (Nextclade)
                       - Sequence quality assessment
                       - Clade assignment and mutation calling
                       - Detection of potential sequencing errors
                    
                    3. **Tree Construction** (IQ-TREE)
                       - Maximum likelihood phylogenetic inference
                       - Model selection and bootstrap support
                       - Serotype-specific tree generation
                    
                    4. **Temporal Analysis** (TreeTime)
                       - Molecular clock calibration
                       - Ancestral state reconstruction
                       - Transmission cluster identification
                    
                    5. **Visualization** (Nextstrain/Auspice)
                       - Interactive tree exploration
                       - Geographic and temporal mapping
                       - Mutation tracking across lineages
                    """)
                
                st.markdown("---")
                
                # Auspice JSON uploader
                st.markdown("### 📁 Auspice JSON Preview (Experimental)")
                st.markdown("Upload a Nextstrain Auspice JSON file to preview metadata:")
                
                uploaded_file = st.file_uploader(
                    "Choose an Auspice JSON file",
                    type=['json'],
                    key='auspice_upload',
                    help="Upload a Nextstrain Auspice JSON for basic metadata preview"
                )
                
                if uploaded_file is not None:
                    try:
                        # Read and parse JSON
                        import json
                        import tempfile
                        import os
                        
                        json_content = json.loads(uploaded_file.read())
                        
                        # Save to temp file
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                            json.dump(json_content, tmp_file)
                            temp_path = tmp_file.name
                        
                        st.success(f"✅ File uploaded successfully and saved to temporary location")
                        
                        # Extract basic metadata
                        metadata = {}
                        
                        # Check for tree structure
                        if 'tree' in json_content:
                            def count_nodes(node):
                                count = 1
                                if 'children' in node:
                                    for child in node['children']:
                                        count += count_nodes(child)
                                return count
                            
                            metadata['Total nodes'] = count_nodes(json_content['tree'])
                        
                        # Check for metadata
                        if 'meta' in json_content:
                            meta = json_content['meta']
                            if 'title' in meta:
                                metadata['Title'] = meta['title']
                            if 'updated' in meta:
                                metadata['Last updated'] = meta['updated']
                            if 'panels' in meta:
                                metadata['Panels'] = ', '.join(meta['panels'])
                            if 'genome_annotations' in meta:
                                metadata['Genome annotations'] = len(meta['genome_annotations'])
                        
                        # Display metadata
                        if metadata:
                            st.markdown("**File Metadata:**")
                            for key, value in metadata.items():
                                st.write(f"- {key}: {value}")
                        
                        # Provide link to external viewer
                        st.info("""
                        💡 **View in Auspice:**
                        To fully explore this phylogenetic tree, use the Nextstrain Auspice viewer:
                        1. Visit [auspice.us](https://auspice.us)
                        2. Drag and drop your JSON file
                        3. Explore the interactive tree with full functionality
                        """)
                        
                    except json.JSONDecodeError:
                        st.error("Invalid JSON file. Please upload a valid Auspice JSON.")
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
                else:
                    st.info("No file uploaded yet. Upload an Auspice JSON to see metadata preview.")
            
        else:
            st.warning("No data available for the selected filters.")
    else:
        st.warning("Please select at least one province and one serotype.")
    
    # Footer
    st.divider()
    st.caption("GeneTropica MVP - Version 0.1.0 | Developed by Russell Young | Data updated through mock generation - September 2025")


if __name__ == "__main__":
    main()