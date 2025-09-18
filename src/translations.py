"""
Translations for Indonesian (Bahasa Indonesia) and English.
"""

TRANSLATIONS = {
    'en': {
        # Main headers
        'app_title': '🦟 GeneTropica — Dengue · Climate · Forecast (MVP) by Russell Young',
        'ksp_serotypes': '🧬 Serotypes/Lineages',
        'ksp_climate': '🌡️ Climate Correlation',
        'ksp_forecast': '📈 Forecast Models',
        
        # Sidebar
        'filters': '🔍 Filters',
        'year_range': 'Year Range',
        'year_range_help': 'Select the range of years to include',
        'provinces': 'Provinces',
        'provinces_help': 'Select provinces to display',
        'serotypes': 'Serotypes',
        'serotypes_help': 'Filter by dominant serotype',
        'map_type': 'Map Type',
        'map_type_help': 'Bubble map recommended - shows all provinces clearly',
        'bubble_map': 'Bubble Map',
        'choropleth': 'Choropleth',
        'sources_ethics': '📚 Sources & Ethics',
        'data_sources': 'Data Sources',
        'mock_data_notice': '⚠️ Mock Data Notice',
        'mock_data_desc': 'This demo currently uses synthetic mock data for demonstration purposes.',
        'language': '🌐 Language',
        
        # Map section
        'map_header': '🗺️ Dengue Serotype Distribution Map',
        'select_month': '📅 Select Month',
        'select_month_help': 'Slide to animate through time',
        'showing_data_for': 'Showing data for:',
        'download_data': '📥 Download Data',
        'download_help': 'Download the filtered dataset as CSV',
        
        # Statistics
        'monthly_stats': '📊 Monthly Statistics',
        'total_cases': 'Total Cases',
        'avg_rainfall': 'Avg Rainfall',
        'avg_temperature': 'Avg Temperature',
        'serotype_dist': 'Serotype Distribution',
        'provinces_unit': 'provinces',
        
        # Trends section
        'trends_header': '📈 Trends & Climate Analysis',
        'smooth_data': 'Smooth serotype data',
        'smooth_help': 'Apply 3-month rolling average to serotype composition',
        'rainfall_lag': 'Rainfall lag (months)',
        'rainfall_lag_help': 'Shift rainfall data to find lagged correlations',
        'serotype_comp': 'Serotype Composition Over Time',
        'cases_climate': 'Cases vs Climate Variables',
        'correlations': '📊 Correlations with cases:',
        'stacked_note': '📊 Stacked areas sum to 100% at each time point',
        
        # Forecast section
        'forecast_header': '📊 Forecast (Prototype)',
        'forecast_warning': '⚠️ Educational Prototype Disclaimer',
        'forecast_disclaimer': '''This forecast is a simple statistical model for educational purposes only. 
        It is NOT intended for clinical decision-making or public health planning.
        Always consult qualified health professionals for medical advice.''',
        'forecast_horizon': 'Forecast horizon (months)',
        'forecast_horizon_help': 'Number of months to forecast ahead',
        'forecast_lag': 'Rainfall lag for model',
        'forecast_lag_help': 'Lag months for rainfall effect in the model',
        'mae_backtest': 'MAE (Backtest)',
        'rmse_backtest': 'RMSE (Backtest)',
        'backtest_samples': 'Backtest Samples',
        'insufficient_data': 'Insufficient data',
        'cases_unit': 'cases',
        'months_unit': 'months',
        'model_label': 'Model:',
        
        # Phylogenetics section
        'phylo_header': '🧬 Phylogenetics (Coming Soon)',
        'phylo_pipeline': 'Planned Phylogenetic Analysis Pipeline',
        'phylo_coming': 'Coming in future versions:',
        'auspice_preview': '📁 Auspice JSON Preview (Experimental)',
        'auspice_desc': 'Upload a Nextstrain Auspice JSON file to preview metadata:',
        'choose_file': 'Choose an Auspice JSON file',
        'file_uploaded': '✅ File uploaded successfully and saved to temporary location',
        'file_metadata': 'File Metadata:',
        
        # Footer
        'footer': 'GeneTropica MVP - Version 0.1.0 | Data updated through mock generation',
        
        # Status badges
        'provinces_selected': 'provinces selected',
        'province_selected': 'province selected',
        'years_label': 'Years:',
        
        # Error messages
        'error_loading': 'Error loading data:',
        'generate_mock': 'Please run `python -m src.data_io --make-mock` to generate mock data.',
        'no_data_filters': 'No data matches the selected filters. Try adjusting your selection.',
        'select_province_serotype': 'Please select at least one province and one serotype.',
        'error_forecast': 'Error generating forecast:',
        'limited_data_msg': 'This may happen with limited data. Try selecting different provinces or date ranges.'
    },
    
    'id': {  # Indonesian (Bahasa Indonesia)
        # Main headers
        'app_title': '🦟 GeneTropica — Demam Berdarah · Iklim · Prakiraan (MVP) oleh Russell Young',
        'ksp_serotypes': '🧬 Serotipe/Garis Keturunan',
        'ksp_climate': '🌡️ Korelasi Iklim',
        'ksp_forecast': '📈 Model Prakiraan',
        
        # Sidebar
        'filters': '🔍 Filter',
        'year_range': 'Rentang Tahun',
        'year_range_help': 'Pilih rentang tahun yang akan disertakan',
        'provinces': 'Provinsi',
        'provinces_help': 'Pilih provinsi untuk ditampilkan',
        'serotypes': 'Serotipe',
        'serotypes_help': 'Filter berdasarkan serotipe dominan',
        'map_type': 'Jenis Peta',
        'map_type_help': 'Peta gelembung direkomendasikan - menampilkan semua provinsi dengan jelas',
        'bubble_map': 'Peta Gelembung',
        'choropleth': 'Choropleth',
        'sources_ethics': '📚 Sumber & Etika',
        'data_sources': 'Sumber Data',
        'mock_data_notice': '⚠️ Pemberitahuan Data Simulasi',
        'mock_data_desc': 'Demo ini saat ini menggunakan data simulasi sintetis untuk tujuan demonstrasi.',
        'language': '🌐 Bahasa',
        
        # Map section
        'map_header': '🗺️ Peta Distribusi Serotipe Demam Berdarah',
        'select_month': '📅 Pilih Bulan',
        'select_month_help': 'Geser untuk animasi waktu',
        'showing_data_for': 'Menampilkan data untuk:',
        'download_data': '📥 Unduh Data',
        'download_help': 'Unduh dataset yang telah difilter sebagai CSV',
        
        # Statistics
        'monthly_stats': '📊 Statistik Bulanan',
        'total_cases': 'Total Kasus',
        'avg_rainfall': 'Rata-rata Curah Hujan',
        'avg_temperature': 'Rata-rata Suhu',
        'serotype_dist': 'Distribusi Serotipe',
        'provinces_unit': 'provinsi',
        
        # Trends section
        'trends_header': '📈 Analisis Tren & Iklim',
        'smooth_data': 'Haluskan data serotipe',
        'smooth_help': 'Terapkan rata-rata bergerak 3 bulan pada komposisi serotipe',
        'rainfall_lag': 'Jeda curah hujan (bulan)',
        'rainfall_lag_help': 'Geser data curah hujan untuk menemukan korelasi tertunda',
        'serotype_comp': 'Komposisi Serotipe Sepanjang Waktu',
        'cases_climate': 'Kasus vs Variabel Iklim',
        'correlations': '📊 Korelasi dengan kasus:',
        'stacked_note': '📊 Area bertumpuk berjumlah 100% pada setiap titik waktu',
        
        # Forecast section
        'forecast_header': '📊 Prakiraan (Prototipe)',
        'forecast_warning': '⚠️ Peringatan Prototipe Edukasi',
        'forecast_disclaimer': '''Prakiraan ini adalah model statistik sederhana untuk tujuan edukasi saja. 
        TIDAK dimaksudkan untuk pengambilan keputusan klinis atau perencanaan kesehatan masyarakat.
        Selalu konsultasikan dengan profesional kesehatan yang berkualifikasi untuk saran medis.''',
        'forecast_horizon': 'Horizon prakiraan (bulan)',
        'forecast_horizon_help': 'Jumlah bulan untuk prakiraan ke depan',
        'forecast_lag': 'Jeda curah hujan untuk model',
        'forecast_lag_help': 'Jeda bulan untuk efek curah hujan dalam model',
        'mae_backtest': 'MAE (Uji Mundur)',
        'rmse_backtest': 'RMSE (Uji Mundur)',
        'backtest_samples': 'Sampel Uji Mundur',
        'insufficient_data': 'Data tidak mencukupi',
        'cases_unit': 'kasus',
        'months_unit': 'bulan',
        'model_label': 'Model:',
        
        # Phylogenetics section
        'phylo_header': '🧬 Filogenetik (Segera Hadir)',
        'phylo_pipeline': 'Rencana Pipeline Analisis Filogenetik',
        'phylo_coming': 'Akan datang di versi mendatang:',
        'auspice_preview': '📁 Pratinjau JSON Auspice (Eksperimental)',
        'auspice_desc': 'Unggah file Nextstrain Auspice JSON untuk pratinjau metadata:',
        'choose_file': 'Pilih file Auspice JSON',
        'file_uploaded': '✅ File berhasil diunggah dan disimpan ke lokasi sementara',
        'file_metadata': 'Metadata File:',
        
        # Footer
        'footer': 'GeneTropica MVP - Versi 0.1.0 | Data diperbarui melalui generasi simulasi',
        
        # Status badges
        'provinces_selected': 'provinsi dipilih',
        'province_selected': 'provinsi dipilih',
        'years_label': 'Tahun:',
        
        # Error messages
        'error_loading': 'Kesalahan memuat data:',
        'generate_mock': 'Silakan jalankan `python -m src.data_io --make-mock` untuk menghasilkan data simulasi.',
        'no_data_filters': 'Tidak ada data yang cocok dengan filter yang dipilih. Coba sesuaikan pilihan Anda.',
        'select_province_serotype': 'Silakan pilih setidaknya satu provinsi dan satu serotipe.',
        'error_forecast': 'Kesalahan menghasilkan prakiraan:',
        'limited_data_msg': 'Ini mungkin terjadi dengan data terbatas. Coba pilih provinsi atau rentang tanggal yang berbeda.'
    }
}

def get_text(key: str, language: str = 'en') -> str:
    """
    Get translated text for a given key.
    
    Args:
        key: Translation key
        language: Language code ('en' or 'id')
    
    Returns:
        Translated text or key if not found
    """
    return TRANSLATIONS.get(language, {}).get(key, key)

def get_province_name(province_id: str, language: str = 'en') -> str:
    """
    Get translated province name.
    
    Args:
        province_id: Province ID
        language: Language code
    
    Returns:
        Translated province name
    """
    province_names = {
        'en': {
            'DKI': 'DKI Jakarta',
            'JABAR': 'West Java',
            'JATENG': 'Central Java',
            'JATIM': 'East Java',
            'BANTEN': 'Banten',
            'DIY': 'Yogyakarta'
        },
        'id': {
            'DKI': 'DKI Jakarta',
            'JABAR': 'Jawa Barat',
            'JATENG': 'Jawa Tengah',
            'JATIM': 'Jawa Timur',
            'BANTEN': 'Banten',
            'DIY': 'DI Yogyakarta'
        }
    }
    
    return province_names.get(language, {}).get(province_id, province_id)