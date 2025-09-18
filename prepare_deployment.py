"""
Prepare the repository for Streamlit Cloud deployment.
Run this before deploying to ensure mock data exists.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data_io import generate_mock_data

def prepare_for_deployment():
    """Prepare the repository for cloud deployment."""
    
    print("🚀 Preparing GeneTropica for deployment...")
    print("-" * 50)
    
    # 1. Generate mock data
    print("\n📊 Generating mock datasets...")
    try:
        generate_mock_data()
        print("✅ Mock data generated successfully!")
    except Exception as e:
        print(f"❌ Error generating mock data: {e}")
        return False
    
    # 2. Check required files
    print("\n📁 Checking required files...")
    required_files = [
        "requirements.txt",
        "app/app.py",
        ".streamlit/config.toml",
        "data/mock/provinces.geojson",
        "data/mock/features.csv",
        "data/mock/dengue_cases.csv",
        "data/mock/climate.csv",
        "data/mock/serotype_share.csv"
    ]
    
    root = Path(__file__).parent
    missing = []
    for file in required_files:
        filepath = root / file
        if filepath.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING!")
            missing.append(file)
    
    if missing:
        print(f"\n⚠️ Missing {len(missing)} required files!")
        print("Please ensure all files are present before deploying.")
        return False
    
    # 3. Check file sizes
    print("\n📏 Checking data file sizes...")
    data_dir = root / "data" / "mock"
    total_size = 0
    for file in data_dir.glob("*"):
        if file.is_file():
            size = file.stat().st_size / 1024  # KB
            total_size += size
            print(f"  {file.name}: {size:.1f} KB")
    
    print(f"\n  Total data size: {total_size:.1f} KB")
    if total_size > 10240:  # 10MB warning
        print("  ⚠️ Large data files may slow deployment")
    
    print("\n" + "=" * 50)
    print("✅ Deployment preparation complete!")
    print("\nNext steps:")
    print("1. Commit all changes to GitHub")
    print("2. Go to share.streamlit.io")
    print("3. Deploy with app/app.py as main file")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = prepare_for_deployment()
    sys.exit(0 if success else 1)