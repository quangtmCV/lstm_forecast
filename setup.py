#!/usr/bin/env python3
"""
Setup script for LSTM Weather Forecast System
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("🔧 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_data_file():
    """Check if data file exists"""
    data_file = "data/POWER_Point_Daily_20111207_20250807_021d01N_105d83E_LST.csv"
    if os.path.exists(data_file):
        print(f"✅ Data file found: {data_file}")
        return True
    else:
        print(f"❌ Data file not found: {data_file}")
        print("Please ensure the data file exists before running the forecast.")
        return False

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    try:
        sys.path.append('src')
        from data_loader import DataLoader
        from model import build_model
        from trainer import Trainer
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 LSTM Weather Forecast System Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required. Current version:", sys.version)
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Install dependencies
    if not install_requirements():
        return False
    
    # Check data file
    if not check_data_file():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo run the forecast system:")
    print("  python src/main.py --mode once")
    print("  python src/main.py --mode scheduler")
    print("  or run: run_daily_forecast.bat (Windows)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
