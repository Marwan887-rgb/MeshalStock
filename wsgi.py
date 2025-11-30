#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI Entry Point for MeshalStock
استخدم هذا الملف للنشر مع Gunicorn أو خوادم WSGI أخرى

مثال:
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""

import sys
from pathlib import Path

# Initialize data on first run (background)
try:
    from initialize_data import initialize_data
    print("🔍 Checking for data files on startup...")
    initialize_data(background=True)
except Exception as e:
    print(f"⚠️  Could not initialize data: {e}")

from api_server import app

if __name__ == "__main__":
    app.run()
