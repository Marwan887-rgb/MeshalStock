#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migrate CSV data to Supabase
Uploads all stock data from CSV files to Supabase database
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from supabase_client import get_supabase_client, insert_stock_data_batch

BASE_DIR = Path(__file__).parent

def migrate_market_data(market, batch_size=1000):
    """
    Migrate all CSV files from a market to Supabase
    
    Args:
        market: 'saudi' or 'us'
        batch_size: Number of records per batch
    
    Returns:
        Total records uploaded
    """
    
    if market == 'saudi':
        directory = BASE_DIR / 'data_sa'
    elif market == 'us':
        directory = BASE_DIR / 'data_us'
    else:
        print(f"Invalid market: {market}")
        return 0
    
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return 0
    
    csv_files = list(directory.glob('*.csv'))
    total_records = 0
    total_files = len(csv_files)
    
    print(f"\n{'='*70}")
    print(f"MIGRATING {market.upper()} MARKET DATA TO SUPABASE")
    print(f"{'='*70}")
    print(f"Found {total_files} CSV files")
    print()
    
    for idx, csv_file in enumerate(csv_files, 1):
        symbol = csv_file.stem
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Skip empty files
            if len(df) == 0:
                print(f"[{idx}/{total_files}] {symbol}: SKIPPED (empty)")
                continue
            
            # Prepare records
            records = []
            for _, row in df.iterrows():
                try:
                    record = {
                        'symbol': symbol,
                        'market': market,
                        'date': str(row['Date']).split()[0],  # Extract date only
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume'])
                    }
                    records.append(record)
                except Exception as e:
                    # Skip bad rows
                    continue
            
            if len(records) == 0:
                print(f"[{idx}/{total_files}] {symbol}: SKIPPED (no valid data)")
                continue
            
            # Upload in batches
            uploaded = 0
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                count = insert_stock_data_batch(batch)
                uploaded += count
            
            total_records += uploaded
            
            print(f"[{idx}/{total_files}] {symbol}: ✓ {uploaded} records uploaded")
            
        except Exception as e:
            print(f"[{idx}/{total_files}] {symbol}: ✗ ERROR: {e}")
            continue
    
    print()
    print(f"{'='*70}")
    print(f"MIGRATION COMPLETE")
    print(f"Total records uploaded: {total_records:,}")
    print(f"{'='*70}")
    
    return total_records


def main():
    """Main migration function"""
    
    print("\n" + "="*70)
    print("MESHALSTOCK CSV TO SUPABASE MIGRATION")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test connection
        client = get_supabase_client()
        print("✓ Connected to Supabase")
        
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
        print("\nMake sure you have set SUPABASE_KEY in your .env file:")
        print("SUPABASE_KEY=your_key_here")
        return
    
    # Migrate both markets
    total = 0
    
    # Saudi market
    saudi_count = migrate_market_data('saudi', batch_size=500)
    total += saudi_count
    
    # US market
    us_count = migrate_market_data('us', batch_size=500)
    total += us_count
    
    # Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Saudi market: {saudi_count:,} records")
    print(f"US market: {us_count:,} records")
    print(f"Total: {total:,} records")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == '__main__':
    main()
