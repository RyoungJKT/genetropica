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

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.transforms import (
    load_geo, 
    load_features, 
    build_province_month_df,
    compute_dominant_serotype,
    SEROTYPE_PALETTE
)


def create_choropleth_map(df_month, gdf, selected_provinces):
    """
    Create a Plotly choropleth map colored by dominant serotype.
    
    Args:
        df_month: DataFrame for a specific month
        gdf: GeoDataFrame with province geometries
        selected_provinces: List of selected province IDs
    
    Returns:
        Plotly figure
    """
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
    geojson_dict = json.loads(gdf_filtered.to_json())
    
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
        center={"lat": -6.5, "lon": 107.0},
        projection_scale=25,
        showcountries=True,
        countrycolor="lightgray",
        showcoastlines=True,
        coastlinecolor="lightgray",
        showland=True,
        landcolor="#f0f0f0",
        showocean=True,
        oceancolor="#e6f2ff",
        fitbounds="locations",
        visible=True
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
            x=1.02
        ),
        geo=dict(
            showframe=True,
            showcoastlines=True,
            projection_type='natural earth'
        )
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
        countrycolor="lightgray",
        showcoastlines=True,
        coastlinecolor="lightgray",
        showland=True,
        landcolor="#f0f0f0",
        showocean=True,
        oceancolor="#e6f2ff",
        fitbounds="locations"
    )
    
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )
    
    return fig


def main():
    """Main application entry point."""
    
    # Page configuration
    st.set_page_config(
        page_title="GeneTropica",
        page_icon="🦟",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main title
    st.title("GeneTropica — Dengue · Climate · Forecast (MVP)")
    
    # Load data
    try:
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
    
    # Sidebar filters
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
            options=["Choropleth", "Bubble Map"],
            help="Choose visualization type"
        )
        
        st.divider()
        st.caption("Data filters update the map in real-time")
    
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
            
            # Create two columns for map and stats
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create and display the map based on selection
                if map_type == "Choropleth":
                    fig = create_choropleth_map(df_month, gdf, selected_provinces)
                else:
                    fig = create_simple_scatter_map(df_month, gdf, selected_provinces)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Debug info (can be removed later)
                with st.expander("🔧 Debug Info"):
                    st.write("Selected provinces:", selected_provinces)
                    st.write("Data points for month:", len(df_month))
                    st.write("Province centers:", gdf[['province_id', 'lon', 'lat']].to_dict('records'))
            
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
            
            # Legend for serotype colors
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
        else:
            st.warning("No data available for the selected filters.")
    else:
        st.warning("Please select at least one province and one serotype.")
    
    # Footer
    st.divider()
    st.caption("GeneTropica MVP - Version 0.1.0 | Data updated through mock generation")


if __name__ == "__main__":
    main()