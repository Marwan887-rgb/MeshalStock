#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبار مباشر لـ yfinance"""

import yfinance as yf

print("Testing yfinance...")

# اختبار واحد
try:
    ticker = yf.Ticker('^DJI')
    print(f"\n1. Testing history...")
    hist = ticker.history(period="2d")
    print(f"   History: {len(hist)} rows")
    if not hist.empty:
        print(f"   Latest: {hist['Close'].iloc[-1]}")
except Exception as e:
    print(f"   Error: {e}")

# اختبار fast_info
try:
    print(f"\n2. Testing fast_info...")
    fast_info = ticker.fast_info
    print(f"   Fast info keys: {list(fast_info.keys())[:5]}")
    price = fast_info.get('lastPrice')
    print(f"   Price: {price}")
except Exception as e:
    print(f"   Error: {e}")

# اختبار info
try:
    print(f"\n3. Testing info...")
    info = ticker.info
    price = info.get('currentPrice') or info.get('regularMarketPrice')
    print(f"   Price from info: {price}")
except Exception as e:
    print(f"   Error: {e}")

print("\nDone!")
