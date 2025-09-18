"""
GeneTropica - Main Streamlit Application
Dengue · Climate · Forecast (MVP)
With Indonesian localization and accessibility features
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
from src.translations import get_text, get_province_name


@st.cache_resource
def get_fitted_model_params(df: pd.DataFrame):
    """Cache expensive model fitting operations."""
    return {"cached": True, "timestamp": datetime.now()}


def create_choropleth_map(df_month, gdf, selected_provinces, lang='en'):
    """
    Create a Plotly choropleth map colored by dominant serotype.
    Falls back to scatter map if GeoJSON not available.
    """
    # Check if we have geometry data
    has_geometry = 'geometry' in gdf.columns and gdf['geometry'].notna().any()
    
    if not has_geometry:
        return create_simple_scatter_map(df_month, gdf, selected_provinces, lang)
    
    # Filter GeoDataFrame to selected provinces
    gdf_filtered = gdf[gdf['province_id'].isin(selected_provinces)].copy()
    
    # Merge data with geometries
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
        for i in range(1, 5):
            merged[f'denv{i}_share'] = 0
    
    # Convert GeoDataFrame to GeoJSON for Plotly
    try:
        geojson_dict = json.loads(gdf_filtered.to_json())
    except:
        return create_simple_scatter_map(df_month, gdf, selected_provinces, lang)
    
    # Create hover text with translations
    cases_label = get_text('cases_unit', lang).capitalize()
    rainfall_label = "Curah hujan" if lang == 'id' else "Rainfall"
    temp_label = "Suhu" if lang == 'id' else "Temperature"
    serotype_label = "Bagian Serotipe" if lang == 'id' else "Serotype Shares"
    
    merged['hover_text'] = merged.apply(
        lambda row: (
            f"<b>{get_province_name(row['province_id'], lang)}</b><br>"
            f"{cases_label}: {row['cases']:,}<br>"
            f"{rainfall_label}: {row['rainfall_mm']:.1f} mm<br>"
            f"{temp_label}: {row['temperature_c']:.1f} °C<br>"
            f"<br><b>{serotype_label}:</b><br>"
            f"DENV1: {row['denv1_share']:.1%}<br>"
            f"DENV2: {row['denv2_share']:.1%}<br>"
            f"DENV3: {row['denv3_share']:.1%}<br>"
            f"DENV4: {row['denv4_share']:.1%}"
        ) if pd.notna(row['cases']) else f"<b>{get_province_name(row['province_id'], lang)}</b><br>No data",
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
        labels={'dominant_serotype': 'Serotipe Dominan' if lang == 'id' else 'Dominant Serotype'},
    )
    
    # Update traces to use custom hover text
    fig.update_traces(
        customdata=merged[['hover_text']].values,
        hovertemplate='%{customdata[0]}<extra></extra>'
    )
    
    # Update layout
    fig.update_geos(
        center={"lat": -7.0, "lon": 110.0},
        projection_scale=8,
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
        resolution=50,
        scope="asia"
    )
    
    title_text = "Serotipe Dominan Demam Berdarah per Provinsi" if lang == 'id' else "Dengue Dominant Serotype by Province"
    
    fig.update_layout(
        title=title_text,
        height=600,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        legend=dict(
            title="Serotipe Dominan" if lang == 'id' else "Dominant Serotype",
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


def create_simple_scatter_map(df_month, gdf, selected_provinces, lang='en'):
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
    
    # Create translated province names
    merged['province_display'] = merged['province_id'].apply(lambda x: get_province_name(x, lang))
    
    # Create hover text with translations
    cases_label = get_text('cases_unit', lang).capitalize()
    rainfall_label = "Curah hujan" if lang == 'id' else "Rainfall"
    temp_label = "Suhu" if lang == 'id' else "Temperature"
    serotype_label = "Bagian Serotipe" if lang == 'id' else "Serotype Shares"
    
    merged['hover_text'] = merged.apply(
        lambda row: (
            f"<b>{row['province_display']}</b><br>"
            f"{cases_label}: {row['cases']:,}<br>"
            f"{rainfall_label}: {row['rainfall_mm']:.1f} mm<br>"
            f"{temp_label}: {row['temperature_c']:.1f} °C<br>"
            f"<br><b>{serotype_label}:</b><br>"
            f"DENV1: {row.get('denv1_share', 0):.1%}<br>"
            f"DENV2: {row.get('denv2_share', 0):.1%}<br>"
            f"DENV3: {row.get('denv3_share', 0):.1%}<br>"
            f"DENV4: {row.get('denv4_share', 0):.1%}"
        ) if pd.notna(row['cases']) else f"<b>{row['province_display']}</b><br>No data",
        axis=1
    )
    
    title_text = "Kasus Demam Berdarah per Provinsi (Peta Gelembung)" if lang == 'id' else "Dengue Cases by Province (Bubble Map)"
    
    # Create scatter map
    fig = px.scatter_geo(
        merged,
        lat='lat',
        lon='lon',
        color='dominant_serotype',
        size='cases',
        hover_name='province_display',
        color_discrete_map=SEROTYPE_PALETTE,
        size_max=50,
        title=title_text
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
    
    # Initialize session state for language
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    # Get current language
    lang = st.session_state.language
    
    # Custom CSS for better styling, WCAG compliance, and accessibility
    st.markdown(f"""
    <style>
    .main-header {{
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }}
    .ksp-item {{
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 500;
        text-align: center;
        display: block;
        white-space: nowrap;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }}
    .ksp-serotypes {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }}
    .ksp-climate {{
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
    }}
    .ksp-forecast {{
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }}
    .status-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }}
    .province-badge {{
        background-color: #E8F4F8;
        color: #2C3E50;
        border: 1px solid #BDC3C7;
    }}
    .month-badge {{
        background-color: #FFF5E6;
        color: #8B4513;
        border: 1px solid #D2691E;
    }}
    /* Accessibility improvements */
    .sr-only {{
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0,0,0,0);
        white-space: nowrap;
        border: 0;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Main title with translation
    st.markdown(f'<h1 class="main-header" role="heading" aria-level="1">{get_text("app_title", lang)}</h1>', 
                unsafe_allow_html=True)
    
    # Key Selling Points (KSPs) with translations and ARIA labels
    ksp_col1, ksp_col2, ksp_col3 = st.columns(3)
    
    with ksp_col1:
        st.markdown(f'<div class="ksp-item ksp-serotypes" role="button" aria-label="Serotype analysis feature">{get_text("ksp_serotypes", lang)}</div>', 
                   unsafe_allow_html=True)
    
    with ksp_col2:
        st.markdown(f'<div class="ksp-item ksp-climate" role="button" aria-label="Climate correlation feature">{get_text("ksp_climate", lang)}</div>', 
                   unsafe_allow_html=True)
    
    with ksp_col3:
        st.markdown(f'<div class="ksp-item ksp-forecast" role="button" aria-label="Forecast model feature">{get_text("ksp_forecast", lang)}</div>', 
                   unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Load data with caching
    try:
        with st.spinner('Loading data...' if lang == 'en' else 'Memuat data...'):
            gdf = load_geo()
            df = load_features()
        
        # Get date range from data
        min_year = df.index.year.min()
        max_year = df.index.year.max()
        available_months = df.index.unique().sort_values()
        
    except Exception as e:
        st.error(f"{get_text('error_loading', lang)}: {e}")
        st.info(get_text('generate_mock', lang))
        return
    
    # Sidebar with language selector first
    with st.sidebar:
        # Language selector at the top
        st.markdown(f"### {get_text('language', lang)}")
        language = st.selectbox(
            "",
            options=['en', 'id'],
            index=0 if lang == 'en' else 1,
            format_func=lambda x: 'English' if x == 'en' else 'Bahasa Indonesia',
            key='language_selector',
            label_visibility="collapsed"
        )
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
        
        st.divider()
        
        st.header(get_text('filters', lang))
        
        # Year range slider
        year_range = st.slider(
            get_text('year_range', lang),
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            help=get_text('year_range_help', lang)
        )
        
        # Province multiselect
        all_provinces = sorted(df['province_id'].unique())
        
        selected_provinces = st.multiselect(
            get_text('provinces', lang),
            options=all_provinces,
            default=all_provinces,
            format_func=lambda x: get_province_name(x, lang),
            help=get_text('provinces_help', lang)
        )
        
        # Serotype multiselect
        all_serotypes = ['DENV1', 'DENV2', 'DENV3', 'DENV4']
        selected_serotypes = st.multiselect(
            get_text('serotypes', lang),
            options=all_serotypes,
            default=all_serotypes,
            help=get_text('serotypes_help', lang)
        )
        
        st.divider()
        
        # Map type selector
        map_type = st.radio(
            get_text('map_type', lang),
            options=["Bubble Map", "Choropleth"],
            index=0,
            format_func=lambda x: get_text('bubble_map', lang) if x == "Bubble Map" else get_text('choropleth', lang),
            help=get_text('map_type_help', lang)
        )
        
        st.divider()
        
        # Sources & Ethics section
        with st.expander(get_text('sources_ethics', lang)):
            st.markdown(f"""
            ### {get_text('data_sources', lang)}
            
            **{get_text('mock_data_notice', lang)}**
            
            {get_text('mock_data_desc', lang)}
            """)
        
        st.divider()
        st.caption("Data filters update visualizations in real-time" if lang == 'en' else "Filter data memperbarui visualisasi secara real-time")
    
    # Filter data based on selections
    if selected_provinces and selected_serotypes:
        df_filtered = build_province_month_df(
            province=selected_provinces,
            year_range=year_range,
            serotypes=selected_serotypes
        )
        
        if len(df_filtered) == 0:
            st.warning(get_text('no_data_filters', lang))
            return
            
        # Get available months after filtering
        available_months_filtered = df_filtered.index.unique().sort_values()
        
        # Helper badges showing current selection
        provinces_text = f"{len(selected_provinces)} {get_text('provinces_selected' if len(selected_provinces) != 1 else 'province_selected', lang)}"
        year_text = f"{year_range[0]}–{year_range[1]}"
        st.markdown(
            f'<div style="margin-bottom: 1rem;">'
            f'<span class="status-badge province-badge" role="status" aria-label="Selected provinces">📍 {provinces_text}</span>'
            f'<span class="status-badge month-badge" role="status" aria-label="Selected years">📅 {get_text("years_label", lang)} {year_text}</span>'
            f'</div>', 
            unsafe_allow_html=True
        )
        
        # Main content area
        st.header(get_text('map_header', lang))
        
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
                get_text('select_month', lang),
                options=list(month_options.keys()),
                value=default_index,
                format_func=lambda x: month_options[x],
                help=get_text('select_month_help', lang)
            )
            
            selected_month = available_months_filtered[selected_month_index]
            
            # Display selected month prominently
            st.markdown(f"### {get_text('showing_data_for', lang)} **{selected_month.strftime('%B %Y')}**")
            
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
                    label=get_text('download_data', lang),
                    data=csv_data,
                    file_name=f"genetropica_data_{selected_month.strftime('%Y%m')}.csv",
                    mime="text/csv",
                    help=get_text('download_help', lang)
                )
            
            # Create two columns for map and stats
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create and display the map based on selection
                if map_type == "Bubble Map":
                    fig = create_simple_scatter_map(df_month, gdf, selected_provinces, lang)
                else:
                    fig = create_choropleth_map(df_month, gdf, selected_provinces, lang)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Accessibility caption
                map_caption = ("Interactive map showing dengue serotype distribution across Indonesian provinces. "
                             "Each province is colored by its dominant serotype." if lang == 'en' else
                             "Peta interaktif menunjukkan distribusi serotipe demam berdarah di provinsi-provinsi Indonesia. "
                             "Setiap provinsi diwarnai berdasarkan serotipe dominannya.")
                st.caption(f"🗺️ {map_caption}")
            
            with col2:
                # Display statistics for selected month
                st.markdown(f"### {get_text('monthly_stats', lang)}")
                
                if len(df_month) > 0:
                    total_cases = df_month['cases'].sum()
                    avg_rainfall = df_month['rainfall_mm'].mean()
                    avg_temp = df_month['temperature_c'].mean()
                    
                    st.metric(get_text('total_cases', lang), f"{total_cases:,}")
                    st.metric(get_text('avg_rainfall', lang), f"{avg_rainfall:.1f} mm")
                    st.metric(get_text('avg_temperature', lang), f"{avg_temp:.1f} °C")
                    
                    # Serotype distribution
                    st.markdown(f"#### {get_text('serotype_dist', lang)}")
                    serotype_counts = df_month['dominant_serotype'].value_counts()
                    for serotype, count in serotype_counts.items():
                        color = SEROTYPE_PALETTE.get(serotype, '#888')
                        st.markdown(
                            f"<span style='color: {color}'>●</span> **{serotype}**: {count} {get_text('provinces_unit', lang)}",
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No data for selected filters" if lang == 'en' else "Tidak ada data untuk filter yang dipilih")
            
            # Legend for serotype colors with WCAG compliant colors
            st.markdown("---")
            st.markdown(f"### 🎨 {'Serotype Color Legend' if lang == 'en' else 'Legenda Warna Serotipe'}")
            legend_cols = st.columns(4)
            for i, (serotype, color) in enumerate(SEROTYPE_PALETTE.items()):
                with legend_cols[i]:
                    st.markdown(
                        f"<div style='text-align: center;' role='img' aria-label='{serotype} color indicator'>"
                        f"<span style='color: {color}; font-size: 24px;'>●</span><br>"
                        f"<b>{serotype}</b>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
            
            # Trends and Climate Analysis Section
            st.markdown("---")
            st.header(get_text('trends_header', lang))
            
            # Add smoothing option and lag slider in columns
            control_col1, control_col2, control_col3 = st.columns([1, 1, 2])
            
            with control_col1:
                smooth_data = st.checkbox(
                    get_text('smooth_data', lang), 
                    value=False,
                    help=get_text('smooth_help', lang)
                )
            
            with control_col2:
                lag_months = st.slider(
                    get_text('rainfall_lag', lang),
                    min_value=0, 
                    max_value=3, 
                    value=0,
                    help=get_text('rainfall_lag_help', lang)
                )
            
            # Two column layout for charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader(get_text('serotype_comp', lang))
                
                # Create stacked area chart
                fig_serotype = create_serotype_stacked_area(
                    df_filtered,
                    SEROTYPE_PALETTE,
                    smooth=smooth_data,
                    window=3
                )
                st.plotly_chart(fig_serotype, use_container_width=True)
                
                # Validation note with accessibility
                st.caption(get_text('stacked_note', lang))
            
            with chart_col2:
                st.subheader(get_text('cases_climate', lang))
                
                # Create dual-axis chart
                fig_climate, rainfall_corr, temp_corr = create_cases_climate_dual_axis(
                    df_filtered,
                    lag_months=lag_months
                )
                st.plotly_chart(fig_climate, use_container_width=True)
                
                # Display correlations
                st.caption(get_text('correlations', lang))
                corr_col1, corr_col2 = st.columns(2)
                with corr_col1:
                    rainfall_text = "Curah hujan" if lang == 'id' else "Rainfall"
                    corr_text = f"{rainfall_text} (lag {lag_months}mo): **{rainfall_corr:.3f}**" if not pd.isna(rainfall_corr) else f"{rainfall_text}: No data"
                    st.caption(f"💧 {corr_text}")
                with corr_col2:
                    temp_text = "Suhu" if lang == 'id' else "Temperature"
                    temp_corr_text = f"{temp_text}: **{temp_corr:.3f}**" if not pd.isna(temp_corr) else f"{temp_text}: No data"
                    st.caption(f"🌡️ {temp_corr_text}")
            
            # Forecast Section
            st.markdown("---")
            st.header(get_text('forecast_header', lang))
            
            # Disclaimer
            st.warning(f"""
            {get_text('forecast_warning', lang)}
            
            {get_text('forecast_disclaimer', lang)}
            """)
            
            # Forecast controls
            forecast_col1, forecast_col2, forecast_col3 = st.columns([1, 1, 2])
            
            with forecast_col1:
                forecast_horizon = st.slider(
                    get_text('forecast_horizon', lang),
                    min_value=1,
                    max_value=3,
                    value=2,
                    help=get_text('forecast_horizon_help', lang)
                )
            
            with forecast_col2:
                forecast_lag = st.selectbox(
                    get_text('forecast_lag', lang),
                    options=[1, 2],
                    help=get_text('forecast_lag_help', lang)
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
                last_12_months = df_filtered.tail(12).copy()
                last_12_months = last_12_months.groupby(last_12_months.index).agg({
                    'cases': 'sum'
                })
                
                # Create forecast visualization
                fig_forecast = go.Figure()
                
                # Add actual cases
                actual_label = "Kasus Aktual" if lang == 'id' else "Actual Cases"
                fig_forecast.add_trace(go.Scatter(
                    x=last_12_months.index,
                    y=last_12_months['cases'],
                    mode='lines+markers',
                    name=actual_label,
                    line=dict(color='#2E86AB', width=2),
                    marker=dict(size=6)
                ))
                
                # Add forecast with confidence interval
                if len(forecast_df) > 0:
                    # Add forecast line
                    forecast_label = "Prakiraan" if lang == 'id' else "Forecast"
                    fig_forecast.add_trace(go.Scatter(
                        x=forecast_df['date'],
                        y=forecast_df['yhat'],
                        mode='lines+markers',
                        name=forecast_label,
                        line=dict(color='#A23B72', width=2, dash='dash'),
                        marker=dict(size=6)
                    ))
                    
                    # Add confidence interval
                    x_area = list(forecast_df['date']) + list(forecast_df['date'][::-1])
                    y_area = list(forecast_df['yhat_upper']) + list(forecast_df['yhat_lower'][::-1])
                    
                    interval_label = "Interval Kepercayaan 95%" if lang == 'id' else "95% Confidence Interval"
                    fig_forecast.add_trace(go.Scatter(
                        x=x_area,
                        y=y_area,
                        fill='toself',
                        fillcolor='rgba(162, 59, 114, 0.2)',
                        line=dict(color='rgba(162, 59, 114, 0)'),
                        name=interval_label,
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
                title_text = "Prakiraan Kasus Demam Berdarah" if lang == 'id' else "Dengue Cases Forecast"
                fig_forecast.update_layout(
                    title=title_text,
                    xaxis_title="Tanggal" if lang == 'id' else "Date",
                    yaxis_title="Kasus" if lang == 'id' else "Cases",
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
                
                # Accessibility caption for forecast
                forecast_caption = ("Time series chart showing historical dengue cases and forecasted values with confidence intervals." if lang == 'en' else
                                  "Grafik seri waktu menunjukkan kasus demam berdarah historis dan nilai prakiraan dengan interval kepercayaan.")
                st.caption(f"📈 {forecast_caption}")
                
                # Display metrics
                col_metric1, col_metric2, col_metric3 = st.columns(3)
                
                with col_metric1:
                    mae_val = metrics.get('mae', np.nan)
                    if not pd.isna(mae_val):
                        st.metric(get_text('mae_backtest', lang), f"{mae_val:.1f} {get_text('cases_unit', lang)}")
                    else:
                        st.metric(get_text('mae_backtest', lang), get_text('insufficient_data', lang))
                
                with col_metric2:
                    rmse_val = metrics.get('rmse', np.nan)
                    if not pd.isna(rmse_val):
                        st.metric(get_text('rmse_backtest', lang), f"{rmse_val:.1f} {get_text('cases_unit', lang)}")
                    else:
                        st.metric(get_text('rmse_backtest', lang), get_text('insufficient_data', lang))
                
                with col_metric3:
                    n_tests = metrics.get('n_tests', 0)
                    st.metric(get_text('backtest_samples', lang), f"{n_tests} {get_text('months_unit', lang)}")
                
                # Model description
                if len(forecast_df) > 0:
                    st.info(f"**{get_text('model_label', lang)}** {forecast_df.iloc[0]['model_notes']}")
                
            except Exception as e:
                st.error(f"{get_text('error_forecast', lang)}: {str(e)}")
                st.info(get_text('limited_data_msg', lang))
            
            # Phylogenetics Section
            st.markdown("---")
            with st.expander(get_text('phylo_header', lang)):
                col_phylo1, col_phylo2 = st.columns([1, 2])
                
                with col_phylo1:
                    # Display placeholder image
                    try:
                        from PIL import Image
                        phylo_img_path = Path(__file__).parent.parent / "assets" / "phylo_placeholder.png"
                        if phylo_img_path.exists():
                            img = Image.open(phylo_img_path)
                            caption_text = "Visualisasi Pohon Filogenetik (Placeholder)" if lang == 'id' else "Phylogenetic Tree Visualization (Placeholder)"
                            st.image(img, caption=caption_text, width='stretch')
                        else:
                            st.info("Phylogenetic tree visualization will appear here" if lang == 'en' else 
                                   "Visualisasi pohon filogenetik akan muncul di sini")
                    except:
                        st.info("Phylogenetic tree visualization will appear here" if lang == 'en' else 
                               "Visualisasi pohon filogenetik akan muncul di sini")
                
                with col_phylo2:
                    st.markdown(f"""
                    ### {get_text('phylo_pipeline', lang)}
                    
                    **{get_text('phylo_coming', lang)}**
                    
                    1. **Sequence Alignment** (MAFFT)
                    2. **Quality Control** (Nextclade)
                    3. **Tree Construction** (IQ-TREE)
                    4. **Temporal Analysis** (TreeTime)
                    5. **Visualization** (Nextstrain/Auspice)
                    """)
                
                st.markdown("---")
                
                # Auspice JSON uploader
                st.markdown(f"### {get_text('auspice_preview', lang)}")
                st.markdown(get_text('auspice_desc', lang))
                
                uploaded_file = st.file_uploader(
                    get_text('choose_file', lang),
                    type=['json'],
                    key='auspice_upload',
                    help="Upload a Nextstrain Auspice JSON for basic metadata preview"
                )
                
                if uploaded_file is not None:
                    try:
                        import tempfile
                        import os
                        
                        json_content = json.loads(uploaded_file.read())
                        
                        # Save to temp file
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                            json.dump(json_content, tmp_file)
                            temp_path = tmp_file.name
                        
                        st.success(get_text('file_uploaded', lang))
                        
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
                        
                        # Display metadata
                        if metadata:
                            st.markdown(f"**{get_text('file_metadata', lang)}**")
                            for key, value in metadata.items():
                                st.write(f"- {key}: {value}")
                        
                    except json.JSONDecodeError:
                        st.error("Invalid JSON file" if lang == 'en' else "File JSON tidak valid")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
        else:
            st.warning("No data available" if lang == 'en' else "Tidak ada data tersedia")
    else:
        st.warning(get_text('select_province_serotype', lang))
    
    # Footer
    st.divider()
    footer_text = get_text('footer', lang)
    st.caption(f"{footer_text} | Developed by Russell Young")


if __name__ == "__main__":
    main()