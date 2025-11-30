#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Client for MeshalStock
Database connection and operations
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://jeeqdxewehgnhvuvrprs.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Create Supabase client
supabase: Client = None

def get_supabase_client():
    """Get or create Supabase client instance"""
    global supabase
    
    if supabase is None:
        if not SUPABASE_KEY:
            print("⚠️  SUPABASE_KEY is not set - Supabase features disabled")
            return None
        
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print(f"✓ Supabase client connected to: {SUPABASE_URL}")
        except Exception as e:
            print(f"⚠️  Failed to connect to Supabase: {e}")
            return None
    
    return supabase


# Database Schema
"""
Table: stock_data

Columns:
- id: bigint (primary key, auto-increment)
- symbol: text (indexed)
- market: text ('saudi' or 'us') (indexed)
- date: date (indexed)
- open: numeric
- high: numeric
- low: numeric
- close: numeric
- volume: bigint
- created_at: timestamp (auto)

Indexes:
- symbol (for fast lookup)
- market (for filtering)
- date (for time-based queries)
- composite: (symbol, date) for unique constraint

SQL to create table:
CREATE TABLE stock_data (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    market TEXT NOT NULL CHECK (market IN ('saudi', 'us')),
    date DATE NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(symbol, market, date)
);

CREATE INDEX idx_stock_symbol ON stock_data(symbol);
CREATE INDEX idx_stock_market ON stock_data(market);
CREATE INDEX idx_stock_date ON stock_data(date);
CREATE INDEX idx_stock_symbol_date ON stock_data(symbol, date);
"""


def insert_stock_data(symbol, market, date, open_price, high, low, close, volume):
    """
    Insert a single stock data record
    
    Args:
        symbol: Stock symbol
        market: 'saudi' or 'us'
        date: Date string (YYYY-MM-DD)
        open_price: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
    
    Returns:
        Inserted record or None if error
    """
    try:
        client = get_supabase_client()
        if client is None:
            return None
        
        data = {
            'symbol': symbol,
            'market': market,
            'date': date,
            'open': float(open_price),
            'high': float(high),
            'low': float(low),
            'close': float(close),
            'volume': int(volume)
        }
        
        result = client.table('stock_data').upsert(data).execute()
        return result.data
        
    except Exception as e:
        print(f"Error inserting data for {symbol}: {e}")
        return None


def insert_stock_data_batch(records):
    """
    Insert multiple stock data records at once
    
    Args:
        records: List of dicts with keys: symbol, market, date, open, high, low, close, volume
    
    Returns:
        Number of records inserted
    """
    try:
        client = get_supabase_client()
        if client is None:
            return 0
        
        # Convert to proper types
        for record in records:
            record['open'] = float(record['open'])
            record['high'] = float(record['high'])
            record['low'] = float(record['low'])
            record['close'] = float(record['close'])
            record['volume'] = int(record['volume'])
        
        # Supabase supports upsert (insert or update)
        result = client.table('stock_data').upsert(records).execute()
        return len(result.data) if result.data else 0
        
    except Exception as e:
        print(f"Error inserting batch data: {e}")
        return 0


def get_stock_data(symbol, market, start_date=None, end_date=None):
    """
    Get stock data for a symbol
    
    Args:
        symbol: Stock symbol
        market: 'saudi' or 'us'
        start_date: Start date (YYYY-MM-DD) optional
        end_date: End date (YYYY-MM-DD) optional
    
    Returns:
        List of records
    """
    try:
        client = get_supabase_client()
        if client is None:
            return []
        
        query = client.table('stock_data').select('*').eq('symbol', symbol).eq('market', market)
        
        if start_date:
            query = query.gte('date', start_date)
        if end_date:
            query = query.lte('date', end_date)
        
        query = query.order('date', desc=False)
        
        result = query.execute()
        return result.data
        
    except Exception as e:
        print(f"Error getting data for {symbol}: {e}")
        return []


def get_all_symbols(market):
    """
    Get all unique symbols for a market
    
    Args:
        market: 'saudi' or 'us'
    
    Returns:
        List of symbols
    """
    try:
        client = get_supabase_client()
        if client is None:
            return []
        
        # Use RPC or pagination to get all unique symbols
        # Method 1: Get all with large limit and pagination
        all_symbols = set()
        page_size = 1000
        offset = 0
        
        while True:
            result = client.table('stock_data')\
                .select('symbol')\
                .eq('market', market)\
                .range(offset, offset + page_size - 1)\
                .execute()
            
            if not result.data:
                break
            
            # Add symbols to set
            all_symbols.update([row['symbol'] for row in result.data])
            
            # If we got less than page_size, we're done
            if len(result.data) < page_size:
                break
            
            offset += page_size
        
        return sorted(list(all_symbols))
        
    except Exception as e:
        print(f"Error getting symbols for {market}: {e}")
        return []


def get_latest_date(symbol, market):
    """
    Get the latest date for a symbol
    
    Args:
        symbol: Stock symbol
        market: 'saudi' or 'us'
    
    Returns:
        Latest date string or None
    """
    try:
        client = get_supabase_client()
        if client is None:
            return None
        
        result = client.table('stock_data').select('date').eq('symbol', symbol).eq('market', market).order('date', desc=True).limit(1).execute()
        
        if result.data:
            return result.data[0]['date']
        return None
        
    except Exception as e:
        print(f"Error getting latest date for {symbol}: {e}")
        return None


if __name__ == '__main__':
    # Test connection
    try:
        client = get_supabase_client()
        print("✓ Successfully connected to Supabase!")
        print(f"URL: {SUPABASE_URL}")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
