#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI Entry Point for MeshalStock
استخدم هذا الملف للنشر مع Gunicorn أو خوادم WSGI أخرى

مثال:
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""

from api_server import app

if __name__ == "__main__":
    app.run()
