#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize data on first run
Downloads essential stock data if not present
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent

def check_data_exists():
    """Check if data directories have CSV files"""
    data_sa = BASE_DIR / 'data_sa'
    data_us = BASE_DIR / 'data_us'
    
    sa_files = list(data_sa.glob('*.csv')) if data_sa.exists() else []
    us_files = list(data_us.glob('*.csv')) if data_us.exists() else []
    
    print(f"📁 Found {len(sa_files)} Saudi stocks, {len(us_files)} US stocks")
    
    # Need at least 50 stocks in each market
    return len(sa_files) >= 50 and len(us_files) >= 50

def fetch_data_background():
    """Fetch data in background without blocking server startup"""
    
    print("\n" + "=" * 70)
    print("🚀 BACKGROUND DATA FETCH STARTED")
    print("=" * 70)
    print("This will download stock data in the background...")
    print("Server will continue to start. Data will be available in 10-15 minutes.")
    print()
    
    try:
        # Create marker file to indicate fetch is in progress
        marker_file = BASE_DIR / '.data_fetch_in_progress'
        marker_file.write_text(f"Started at {datetime.now().isoformat()}")
        
        # Fetch US data (limit to top stocks for faster initial load)
        print("📊 Fetching US market data (top 100 stocks)...")
        result_us = subprocess.run([
            sys.executable,
            str(BASE_DIR / 'fetch_us_data.py')
        ], capture_output=True, text=True, timeout=900)  # 15 min timeout
        
        if result_us.returncode == 0:
            print("✓ US data fetch completed")
        else:
            print(f"⚠ US data fetch had issues: {result_us.stderr[:200]}")
        
        # Fetch Saudi data
        print("📊 Fetching Saudi market data...")
        result_sa = subprocess.run([
            sys.executable,
            str(BASE_DIR / 'fetch_saudi_data.py')
        ], capture_output=True, text=True, timeout=900)  # 15 min timeout
        
        if result_sa.returncode == 0:
            print("✓ Saudi data fetch completed")
        else:
            print(f"⚠ Saudi data fetch had issues: {result_sa.stderr[:200]}")
        
        # Remove marker file
        if marker_file.exists():
            marker_file.unlink()
        
        print("\n" + "=" * 70)
        print("✓ BACKGROUND DATA FETCH COMPLETE")
        print("=" * 70)
        
    except subprocess.TimeoutExpired:
        print("⚠ Data fetch timed out (15 minutes). You can update manually from the web interface.")
    except Exception as e:
        print(f"⚠ Warning: Data initialization failed: {e}")
        print("You can manually update data from the web interface.")

def initialize_data(background=True):
    """
    Initialize data if not present
    
    Args:
        background: If True, fetch data in background thread (non-blocking)
                   If False, fetch data synchronously (blocking)
    """
    
    if check_data_exists():
        print("✓ Data files already exist. Skipping initialization.")
        return True
    
    print("\n" + "⚠" * 35)
    print("⚠️  NO DATA FOUND - FIRST RUN DETECTED")
    print("⚠" * 35)
    
    if background:
        # Start background fetch in a separate thread
        import threading
        thread = threading.Thread(target=fetch_data_background, daemon=True)
        thread.start()
        print("✓ Background data fetch started. Server will continue to start...")
        return True
    else:
        # Synchronous fetch (blocking)
        fetch_data_background()
        return True

if __name__ == '__main__':
    initialize_data(background=False)
