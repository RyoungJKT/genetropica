"""
GeneTropica - Main Streamlit Application
Dengue · Climate · Forecast (MVP)
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

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
    
    # Placeholder content
    st.markdown("""
    Welcome to GeneTropica, an integrated platform for:
    - 🦟 Dengue surveillance and analysis
    - 🌡️ Climate data correlation
    - 📈 Forecasting and predictions
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        st.info("Use this panel to navigate through different sections of the application.")
    
    # Footer
    st.divider()
    st.caption("GeneTropica MVP - Version 0.1.0")

if __name__ == "__main__":
    main()