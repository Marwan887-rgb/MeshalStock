#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خادم API لنظام تحديث البيانات
يوفر endpoints للواجهة الأمامية لتشغيل سكربتات جلب البيانات
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import subprocess
import threading
import uuid
import queue
import time
import os
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import math
import numpy as np
import jwt
from functools import wraps
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# Supabase client (optional - falls back to CSV if not configured)
try:
    from supabase_client import get_supabase_client, get_stock_data, get_all_symbols
    USE_SUPABASE = bool(os.getenv('SUPABASE_KEY'))
    if USE_SUPABASE:
        print("✓ Supabase enabled - using database for faster performance")
except Exception as e:
    USE_SUPABASE = False
    print(f"⚠ Supabase not available, using CSV files: {e}")

app = Flask(__name__, static_url_path='', static_folder='.')

# إعدادات التطبيق
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'admin123')
app.config['TOKEN_EXPIRY_HOURS'] = int(os.getenv('TOKEN_EXPIRY_HOURS', '24'))

# إعدادات CORS - في الإنتاج، حدد النطاقات المسموح بها
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*')
if allowed_origins == '*':
    CORS(app)
else:
    origins_list = [origin.strip() for origin in allowed_origins.split(',')]
    CORS(app, origins=origins_list)

# Rate Limiting للحماية من DDoS
if os.getenv('RATE_LIMIT_ENABLED', 'True') == 'True':
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[f"{os.getenv('RATE_LIMIT_PER_MINUTE', '60')}/minute"]
    )
else:
    limiter = None

# تحديد المجلد الأساسي بناءً على موقع الملف الحالي
# هذا يحل مشكلة المسارات العربية (المستندات)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Base Directory: {BASE_DIR}")

# تخزين حالة المهام
jobs = {}
job_outputs = {}

# Cache للمؤشرات (تحديث كل 10 دقائق لتجنب rate limiting)
market_cache = {
    'data': None,
    'timestamp': None,
    'ttl': 600  # 10 دقائق
}

# ========================================
# دوال المصادقة والأمان
# ========================================

def generate_token(username):
    """توليد JWT token"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=app.config['TOKEN_EXPIRY_HOURS']),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    """التحقق من صحة التوكن"""
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # التوكن منتهي الصلاحية
    except jwt.InvalidTokenError:
        return None  # التوكن غير صالح

def token_required(f):
    """Decorator للتحقق من التوكن"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # البحث عن التوكن في الـ headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# ========================================
# Routes
# ========================================

@app.route('/')
def root():
    """عرض الصفحة الرئيسية"""
    return app.send_static_file('index.html')

@app.route('/api/health')
def health_check():
    """فحص صحة الخادم"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """تسجيل الدخول والحصول على توكن"""
    data = request.get_json()
    
    if not data or 'password' not in data:
        return jsonify({'error': 'Password is required'}), 400
    
    password = data['password']
    
    # التحقق من كلمة المرور
    if password == app.config['ADMIN_PASSWORD']:
        token = generate_token('admin')
        return jsonify({
            'success': True,
            'token': token,
            'expires_in': app.config['TOKEN_EXPIRY_HOURS'] * 3600  # بالثواني
        })
    else:
        return jsonify({'error': 'Invalid password'}), 401

@app.route('/api/auth/verify', methods=['POST'])
@token_required
def verify():
    """التحقق من صلاحية التوكن"""
    return jsonify({'valid': True})


class JobRunner:
    """فئة لتشغيل المهام في الخلفية"""
    
    def __init__(self, job_id, command):
        self.job_id = job_id
        self.command = command
        self.output_queue = queue.Queue()
        self.process = None
        self.status = 'pending'
        self.progress = 0
        self.total = 0
        self.stats = {}
        
    def run(self):
        """تشغيل المهمة"""
        try:
            self.status = 'running'
            jobs[self.job_id] = {
                'status': self.status,
                'progress': 0,
                'total': 0,
                'started_at': datetime.now().isoformat(),
                'stats': {}
            }
            
            # إعداد بيئة التشغيل لضمان دعم UTF-8
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            # تشغيل السكربت
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                bufsize=1,
                universal_newlines=True,
                env=env
            )
            
            # قراءة المخرجات
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.parse_output(line)
                    job_outputs.setdefault(self.job_id, []).append(line.strip())
                    
                    # تحديث حالة المهمة
                    jobs[self.job_id].update({
                        'status': self.status,
                        'progress': self.progress,
                        'total': self.total,
                        'stats': self.stats
                    })
            
            self.process.wait()
            
            # تحديد الحالة النهائية
            if self.process.returncode == 0:
                self.status = 'completed'
            else:
                self.status = 'failed'
            
            jobs[self.job_id].update({
                'status': self.status,
                'completed_at': datetime.now().isoformat(),
                'return_code': self.process.returncode
            })
            
        except Exception as e:
            self.status = 'error'
            jobs[self.job_id].update({
                'status': self.status,
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            })
    
    def parse_output(self, line):
        """تحليل مخرجات السكربت لاستخراج التقدم"""
        # البحث عن سطر التقدم
        if 'التقدم:' in line:
            try:
                # التقدم: 5/243 (2.1%)
                parts = line.split('التقدم:')[1].split('(')[0].strip()
                completed, total = parts.split('/')
                self.progress = int(completed.strip())
                self.total = int(total.strip())
            except:
                pass
        
        # البحث عن إحصائيات
        if 'جديد:' in line:
            try:
                # جديد: 5, محدث: 10, محدث مسبقاً: 2, فشل: 0
                parts = line.split('-')[-1].strip()
                items = parts.split(',')
                for item in items:
                    key, value = item.split(':')
                    key = key.strip()
                    value = int(value.strip())
                    
                    if 'جديد' in key:
                        self.stats['new'] = value
                    elif 'محدث' in key and 'مسبقاً' not in key:
                        self.stats['updated'] = value
                    elif 'محدث مسبقاً' in key:
                        self.stats['up_to_date'] = value
                    elif 'فشل' in key:
                        self.stats['failed'] = value
            except:
                pass


@app.route('/api/fetch/saudi', methods=['POST'])
@token_required
def fetch_saudi():
    """بدء جلب بيانات الأسهم السعودية"""
    job_id = str(uuid.uuid4())
    
    # الحصول على اختيارات من الطلب
    data = request.get_json() or {}
    test_mode = data.get('test', False)
    workers = data.get('workers', 2)  # تقليل العدد الافتراضي
    
    # بناء الأمر
    # استخدام sys.executable لضمان استخدام نفس مفسر بايثون
    import sys
    command = [sys.executable, '-u', 'fetch_saudi_data.py', '--workers', str(workers)]
    
    if test_mode:
        command.extend(['--test', '--symbols', '1120.SR,2222.SR,7010.SR'])
    
    # إنشاء وتشغيل المهمة
    # تهيئة المهمة في القاموس فوراً لتجنب Race Condition
    jobs[job_id] = {
        'status': 'starting',
        'progress': 0,
        'total': 0,
        'started_at': datetime.now().isoformat(),
        'stats': {}
    }
    
    runner = JobRunner(job_id, command)
    thread = threading.Thread(target=runner.run)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'status': 'started',
        'message': 'بدأت عملية جلب البيانات السعودية'
    })


@app.route('/api/fetch/us', methods=['POST'])
@token_required
def fetch_us():
    """بدء جلب بيانات الأسهم الأمريكية"""
    job_id = str(uuid.uuid4())
    
    # الحصول على اختيارات من الطلب
    data = request.get_json() or {}
    test_mode = data.get('test', False)
    workers = data.get('workers', 2)  # تقليل العدد الافتراضي
    
    # بناء الأمر
    import sys
    command = [sys.executable, '-u', 'fetch_us_data.py', '--workers', str(workers)]
    
    if test_mode:
        command.extend(['--test', '--symbols', 'AAPL,MSFT,GOOGL'])
    
    # إنشاء وتشغيل المهمة
    # تهيئة المهمة في القاموس فوراً لتجنب Race Condition
    jobs[job_id] = {
        'status': 'starting',
        'progress': 0,
        'total': 0,
        'started_at': datetime.now().isoformat(),
        'stats': {}
    }
    
    runner = JobRunner(job_id, command)
    thread = threading.Thread(target=runner.run)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'status': 'started',
        'message': 'بدأت عملية جلب البيانات الأمريكية'
    })


@app.route('/api/market-summary', methods=['GET'])
def market_summary():
    """جلب ملخص السوق للمؤشرات الرئيسية"""
    # الرموز المطلوبة
    tickers = {
        'TASI': '^TASI.SR',
        'DJI': '^DJI',
        'NASDAQ': '^IXIC',
        'SP500': '^GSPC',
        'OIL': 'CL=F',
        'GOLD': 'GC=F',
        'SILVER': 'SI=F',
        'BTC': 'BTC-USD'
    }
    
    results = {}
    
    try:
        print(f"Fetching market summary for: {list(tickers.keys())}")
        # جلب البيانات دفعة واحدة لتحسين الأداء
        data = yf.download(list(tickers.values()), period="5d", progress=False, auto_adjust=True)
        
        # التحقق من أن البيانات ليست فارغة
        if data.empty:
            print("Error: yfinance returned empty data")
            return jsonify({'error': 'No data returned from yfinance'}), 500

        print("Data fetched successfully")
        
        for name, symbol in tickers.items():
            try:
                # استخراج البيانات للسهم المحدد
                # ملاحظة: yfinance يعيد MultiIndex إذا كان هناك أكثر من رمز
                if len(tickers) > 1:
                    try:
                        stock_data = data['Close'][symbol]
                    except KeyError:
                        print(f"Symbol {symbol} not found in data columns: {data.columns}")
                        results[name] = {'error': 'Symbol not found'}
                        continue
                else:
                    stock_data = data['Close']
                
                # التأكد من وجود بيانات
                valid_data = stock_data.dropna()
                if len(valid_data) >= 2:
                    current_price = valid_data.iloc[-1]
                    prev_price = valid_data.iloc[-2]
                    
                    change = current_price - prev_price
                    change_percent = (change / prev_price) * 100
                    
                    results[name] = {
                        'price': round(float(current_price), 2),
                        'change': round(float(change), 2),
                        'change_percent': round(float(change_percent), 2),
                        'status': 'up' if change >= 0 else 'down'
                    }
                    print(f"{name}: {current_price}")
                else:
                    print(f"{name}: Insufficient data (len={len(valid_data)})")
                    results[name] = {'error': 'Insufficient data'}
                    
            except Exception as e:
                print(f"Error processing {name}: {e}")
                results[name] = {'error': str(e)}
                
        return jsonify(results)
        
    except Exception as e:
        print(f"Global error in market summary: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<job_id>', methods=['GET'])
@token_required
def get_status(job_id):
    """الحصول على حالة مهمة"""
    if job_id not in jobs:
        return jsonify({
            'error': 'المهمة غير موجودة'
        }), 404
    
    job_info = jobs[job_id]
    
    # إضافة آخر سطور من المخرجات
    outputs = job_outputs.get(job_id, [])
    recent_output = outputs[-10:] if len(outputs) > 10 else outputs
    
    return jsonify({
        'job_id': job_id,
        **job_info,
        'recent_output': recent_output
    })


@app.route('/api/jobs', methods=['GET'])
@token_required
def list_jobs():
    """قائمة بجميع المهام"""
    return jsonify({
        'jobs': jobs
    })


@app.route('/api/symbols/<market>', methods=['GET'])
def get_symbols(market):
    """جلب قائمة الرموز المتاحة من الملفات المحلية"""
    try:
        symbols_map = {}
        
        # تحميل الأسماء العربية إذا كان السوق السعودي
        if market == 'saudi':
            directory = os.path.join(BASE_DIR, 'data_sa')
            try:
                symbols_path = os.path.join(BASE_DIR, 'symbols_sa.txt')
                if os.path.exists(symbols_path):
                    df_symbols = pd.read_csv(symbols_path)
                    # تنظيف الأسماء والرموز
                    for _, row in df_symbols.iterrows():
                        sym = str(row['Symbol']).strip()
                        name = str(row['NameAr']).strip()
                        symbols_map[sym] = name
            except Exception as e:
                print(f"Error reading symbols_sa.txt: {e}")
                
        elif market == 'us':
            directory = os.path.join(BASE_DIR, 'data_us')
        else:
            return jsonify({'error': 'Invalid market'}), 400
            
        if not os.path.exists(directory):
            return jsonify({'error': f'Directory {directory} not found'}), 404
            
        symbols = []
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                # إزالة الامتداد .csv
                symbol = filename[:-4]
                
                # البحث عن الاسم العربي
                name_ar = symbols_map.get(symbol, "")
                if not name_ar and market == 'saudi':
                     # محاولة البحث بدون .SR إذا لم يوجد
                     clean_sym = symbol.replace('.SR', '')
                     name_ar = symbols_map.get(clean_sym, "")
                
                symbols.append({
                    'symbol': symbol,
                    'name': name_ar if name_ar else (symbol if market == 'us' else 'سهم سعودي')
                })
                
        # ترتيب القائمة
        symbols.sort(key=lambda x: x['symbol'])
        
        return jsonify({'symbols': symbols})
        
    except Exception as e:
        print(f"Error listing symbols: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/<market>/<symbol>', methods=['GET'])
def get_history(market, symbol):
    """جلب البيانات التاريخية لسهم معين (آخر 6.5 أشهر)"""
    try:
        if market == 'saudi':
            directory = os.path.join(BASE_DIR, 'data_sa')
        elif market == 'us':
            directory = os.path.join(BASE_DIR, 'data_us')
        else:
            return jsonify({'error': 'Invalid market'}), 400
            
        file_path = os.path.join(directory, f"{symbol}.csv")
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        # قراءة ملف CSV
        df = pd.read_csv(file_path)
        
        # تحويل عمود التاريخ
        df['Date'] = pd.to_datetime(df['Date'])
        
        # تحديد الفترة الزمنية (6 أشهر بالضبط)
        end_date = df['Date'].max()
        start_date = end_date - pd.DateOffset(months=6)
        
        # تصفية البيانات
        mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
        filtered_df = df.loc[mask].copy()
        
        # تحويل البيانات إلى JSON
        # نحتاج تحويل التاريخ إلى string
        filtered_df['Date'] = filtered_df['Date'].dt.strftime('%Y-%m-%d')
        
        result = filtered_df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='records')
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500



def calculate_levels(df):
    """حساب مستويات جان وفيبوناتشي للسهم"""
    try:
        # تحويل التاريخ وتصفية آخر 6 أشهر
        if 'Date' not in df.columns: return None
        df['Date'] = pd.to_datetime(df['Date'])
        
        if df.empty: return None
        
        end_date = df['Date'].max()
        start_date = end_date - pd.DateOffset(months=6)
        df_filtered = df[df['Date'] >= start_date].copy()
        
        if df_filtered.empty: return None
        
        # العثور على أقل قاع
        min_low = df_filtered['Low'].min()
        min_low_idx = df_filtered['Low'].idxmin()
        
        # العثور على أول قمة بعد القاع
        peak_high = None
        
        # نأخذ البيانات من بعد القاع
        df_subset = df_filtered.loc[min_low_idx:].reset_index(drop=True)
        
        if len(df_subset) < 3: return None
        
        for i in range(1, len(df_subset) - 1):
            curr = df_subset.iloc[i]['High']
            prev = df_subset.iloc[i-1]['High']
            next_val = df_subset.iloc[i+1]['High']
            
            if curr > prev and curr > next_val:
                peak_high = curr
                break
                
        if peak_high is None or peak_high <= min_low:
            return None
            
        # حساب المستويات
        levels = []
        
        # Gann (Dynamic)
        sqrt_low = math.sqrt(min_low)
        sqrt_peak = math.sqrt(peak_high)
        delta = sqrt_peak - sqrt_low
        
        levels.append({'type': 'Gann 180', 'value': (sqrt_low + 2*delta)**2})
        levels.append({'type': 'Gann 270', 'value': (sqrt_low + 3*delta)**2})
        levels.append({'type': 'Gann 360', 'value': (sqrt_low + 4*delta)**2})
        
        # Fibo
        fib_range = peak_high - min_low
        levels.append({'type': 'Fibo 100', 'value': peak_high})
        levels.append({'type': 'Fibo 161.8', 'value': min_low + fib_range * 1.618})
        levels.append({'type': 'Fibo 261.8', 'value': min_low + fib_range * 2.618})
        levels.append({'type': 'Fibo 423.6', 'value': min_low + fib_range * 4.236})
        
        return levels
    except Exception as e:
        print(f"Error calculating levels: {e}")
        return None

@app.route('/api/scan/fibo_gann', methods=['GET'])
def scan_fibo_gann():
    """فحص جميع الأسهم لاستخراج الفرص (اختراق أو ارتداد)"""
    market = request.args.get('market', 'saudi')
    
    if market == 'saudi':
        directory = os.path.join(BASE_DIR, 'data_sa')
        # تحميل خريطة الأسماء
        symbols_map = {}
        try:
            symbols_path = os.path.join(BASE_DIR, 'symbols_sa.txt')
            if os.path.exists(symbols_path):
                df_sym = pd.read_csv(symbols_path)
                for _, row in df_sym.iterrows():
                    symbols_map[str(row['Symbol']).strip()] = str(row['NameAr']).strip()
        except: pass
    elif market == 'us':
        directory = os.path.join(BASE_DIR, 'data_us')
        symbols_map = {}
    else:
        return jsonify({'error': 'Invalid market'}), 400
        
    if not os.path.exists(directory):
        return jsonify({'results': []})
        
    results = []
    
    for filename in os.listdir(directory):
        if not filename.endswith('.csv'): continue
        
        symbol = filename[:-4]
        file_path = os.path.join(directory, filename)
        
        try:
            df = pd.read_csv(file_path)
            levels = calculate_levels(df)
            
            if not levels: continue
            
            # فحص آخر شمعة
            last_candle = df.iloc[-1]
            open_p = last_candle['Open']
            close_p = last_candle['Close']
            high_p = last_candle['High']
            low_p = last_candle['Low']
            
            match = False
            match_reason = ""
            match_level = 0
            
            for level in levels:
                val = level['value']
                
                # الشرط الأساسي: الشمعة تلامس المستوى (الهاي أعلى واللو أقل)
                if low_p <= val <= high_p:
                    
                    # 1. اختراق (Breakout): الإغلاق فوق المستوى والافتتاح تحته
                    if open_p < val < close_p:
                        match = True
                        match_reason = f"اختراق {level['type']}"
                        match_level = val
                        break
                        
                    # 2. ارتداد (Bounce): هبط للمستوى (اللو أقل منه) لكن أغلق فوقه
                    # يفضل أن يكون الافتتاح أيضاً فوقه ليكون ارتداد واضح، أو مجرد ذيل
                    elif low_p <= val and close_p > val:
                        match = True
                        match_reason = f"ارتداد من {level['type']}"
                        match_level = val
                        break
            
            if match:
                name = symbols_map.get(symbol, symbol)
                if market == 'saudi':
                    clean_sym = symbol.replace('.SR', '')
                    name = symbols_map.get(clean_sym, name)
                    
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'close': close_p,
                    'reason': match_reason,
                    'level': match_level
                })
                
        except Exception as e:
            continue
            
    return jsonify({'results': results})


@app.route('/api/market-data/<market>', methods=['GET'])
def get_market_data(market):
    """جلب بيانات السوق كاملة للعرض في الجدول"""
    try:
        # الحصول على التاريخ المطلوب (اختياري)
        target_date = request.args.get('date', None)
        
        # Try Supabase first
        if USE_SUPABASE:
            try:
                return get_market_data_from_supabase(market, target_date)
            except Exception as e:
                print(f"Supabase error, falling back to CSV: {e}")
        
        # Fallback to CSV
        if market == 'saudi':
            directory = os.path.join(BASE_DIR, 'data_sa')
            # تحميل خريطة الأسماء
            symbols_map = {}
            try:
                symbols_path = os.path.join(BASE_DIR, 'symbols_sa.txt')
                if os.path.exists(symbols_path):
                    df_sym = pd.read_csv(symbols_path)
                    for _, row in df_sym.iterrows():
                        symbols_map[str(row['Symbol']).strip()] = str(row['NameAr']).strip()
            except: pass
        elif market == 'us':
            directory = os.path.join(BASE_DIR, 'data_us')
            symbols_map = {}
        else:
            return jsonify({'error': 'Invalid market'}), 400
            
        if not os.path.exists(directory):
            print(f"Directory not found: {os.path.abspath(directory)}")
            return jsonify({'data': [], 'date': None, 'available_dates': []})
            
        print(f"Reading market data from: {os.path.abspath(directory)}")
        if target_date:
            print(f"Target date requested: {target_date}")
            
        data_list = []
        actual_date = None  # التاريخ الفعلي المستخدم
        available_dates = set()  # جميع التواريخ المتاحة
        
        for filename in os.listdir(directory):
            if not filename.endswith('.csv'): continue
            
            symbol = filename[:-4]
            file_path = os.path.join(directory, filename)
            
            try:
                # قراءة الملف
                df = pd.read_csv(file_path)
                
                if len(df) < 2: continue
                
                # تحويل التاريخ
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.sort_values('Date')
                
                # جمع جميع التواريخ المتاحة
                for d in df['Date']:
                    available_dates.add(d.strftime('%Y-%m-%d'))
                
                # إذا تم تحديد تاريخ معين
                if target_date:
                    target_dt = pd.to_datetime(target_date)
                    # البحث عن أقرب تاريخ
                    df_filtered = df[df['Date'] <= target_dt]
                    if len(df_filtered) == 0:
                        continue  # لا توجد بيانات قبل هذا التاريخ
                    last_row = df_filtered.iloc[-1]
                    
                    # إيجاد الصف السابق
                    last_idx = df_filtered.index[-1]
                    if last_idx > 0:
                        prev_row = df.iloc[last_idx - 1]
                    else:
                        prev_row = last_row  # لا يوجد سابق
                else:
                    # استخدام آخر تاريخ
                    last_row = df.iloc[-1]
                    prev_row = df.iloc[-2]
                
                # حفظ التاريخ الفعلي
                if actual_date is None:
                    actual_date = last_row['Date'].strftime('%Y-%m-%d')
                
                price = float(last_row['Close'])
                prev_close = float(prev_row['Close'])
                change = price - prev_close
                change_pct = (change / prev_close) * 100
                volume = int(last_row['Volume'])
                
                name = symbols_map.get(symbol, symbol)
                if market == 'saudi':
                    clean_sym = symbol.replace('.SR', '')
                    name = symbols_map.get(clean_sym, name)
                
                data_list.append({
                    'symbol': symbol,
                    'name': name,
                    'price': round(price, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_pct, 2),
                    'volume': volume
                })
                
            except Exception as e:
                continue
        
        # إذا لم توجد بيانات للتاريخ المحدد
        if target_date and len(data_list) == 0:
            return jsonify({
                'data': [],
                'date': target_date,
                'message': 'لا توجد بيانات لهذا التاريخ'
            })
                
        return jsonify({
            'data': data_list,
            'date': actual_date,
            'available_dates': sorted(list(available_dates), reverse=True)[:30]  # آخر 30 تاريخ
        })
        
    except Exception as e:
        print(f"Error getting market data: {e}")
        return jsonify({'error': str(e)}), 500


def get_market_data_from_supabase(market, target_date=None):
    """
    Get market data from Supabase for stock list display
    Fast version: Uses SQL aggregation to get latest data for all symbols
    
    Args:
        market: 'saudi' or 'us'
        target_date: Optional date filter (YYYY-MM-DD)
    
    Returns:
        JSON response with data list
    """
    from supabase_client import get_supabase_client
    
    client = get_supabase_client()
    if client is None:
        raise Exception("Supabase client not available")
    
    # Load symbol names for Saudi market
    symbols_map = {}
    if market == 'saudi':
        try:
            symbols_path = os.path.join(BASE_DIR, 'symbols_sa.txt')
            if os.path.exists(symbols_path):
                df_sym = pd.read_csv(symbols_path)
                for _, row in df_sym.iterrows():
                    symbols_map[str(row['Symbol']).strip()] = str(row['NameAr']).strip()
        except: pass
    
    # Use efficient Python aggregation - fetch all data once, process in memory
    return get_market_data_from_supabase_fallback(client, market, target_date, symbols_map)


def get_market_data_from_supabase_fallback(client, market, target_date, symbols_map):
    """
    Efficient method: Fetch recent data for all symbols at once
    Only gets last few dates (not all history) to minimize data transfer
    """
    
    # Strategy: Get recent dates for the market, then process
    # This is much faster than querying each symbol separately
    
    # First, determine what dates to fetch
    if target_date:
        # Get data up to target date
        date_query = client.table('stock_data')\
            .select('date')\
            .eq('market', market)\
            .lte('date', target_date)\
            .order('date', desc=True)\
            .limit(500)
    else:
        # Get recent dates
        date_query = client.table('stock_data')\
            .select('date')\
            .eq('market', market)\
            .order('date', desc=True)\
            .limit(500)
    
    date_result = date_query.execute()
    
    if not date_result.data or len(date_result.data) == 0:
        return jsonify({'data': [], 'date': None, 'message': 'لا توجد بيانات'})
    
    # Get unique dates and take last 5 (enough for latest + previous)
    unique_dates = sorted(list(set([r['date'] for r in date_result.data])), reverse=True)[:5]
    
    if not unique_dates:
        return jsonify({'data': [], 'date': None, 'message': 'لا توجد تواريخ'})
    
    latest_date = unique_dates[0]
    
    # Fetch data for these dates only (much smaller dataset)
    data_query = client.table('stock_data')\
        .select('symbol, date, close, volume')\
        .eq('market', market)\
        .in_('date', unique_dates)\
        .order('symbol')\
        .order('date', desc=True)
    
    result = data_query.execute()
    
    if not result.data:
        return jsonify({'data': [], 'date': None, 'message': 'لا توجد بيانات'})
    
    # Process data efficiently
    df = pd.DataFrame(result.data)
    df['date'] = pd.to_datetime(df['date'])
    
    data_list = []
    
    for symbol in df['symbol'].unique():
        symbol_df = df[df['symbol'] == symbol].sort_values('date', ascending=False)
        
        if len(symbol_df) < 1:
            continue
        
        # Latest data
        last_row = symbol_df.iloc[0]
        # Previous data
        prev_row = symbol_df.iloc[1] if len(symbol_df) > 1 else last_row
        
        close = float(last_row['close'])
        prev_close = float(prev_row['close'])
        volume = int(last_row['volume'])
        
        change = close - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
        
        # Get symbol name
        name = symbol
        if market == 'saudi':
            clean_sym = symbol.replace('.SR', '')
            name = symbols_map.get(clean_sym, symbol)
        
        data_list.append({
            'symbol': symbol,
            'name': name,
            'price': round(close, 2),
            'change': round(change, 2),
            'change_percent': round(change_pct, 2),
            'volume': volume
        })
    
    return jsonify({
        'data': data_list,
        'date': latest_date,
        'count': len(data_list)
    })


def get_stock_data_from_source(symbol, market):
    """
    Get stock data from Supabase or CSV (fallback)
    
    Args:
        symbol: Stock symbol
        market: 'saudi' or 'us'
    
    Returns:
        pandas DataFrame with columns: Date, Open, High, Low, Close, Volume
    """
    if USE_SUPABASE:
        try:
            # Get data from Supabase
            data = get_stock_data(symbol, market)
            if data and len(data) > 0:
                df = pd.DataFrame(data)
                df['Date'] = pd.to_datetime(df['date'])
                df = df.rename(columns={
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                })
                df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
                df = df.sort_values('Date')
                return df
        except Exception as e:
            print(f"Supabase error for {symbol}, falling back to CSV: {e}")
    
    # Fallback to CSV
    if market == 'saudi':
        directory = os.path.join(BASE_DIR, 'data_sa')
    else:
        directory = os.path.join(BASE_DIR, 'data_us')
    
    file_path = os.path.join(directory, f'{symbol}.csv')
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        return df
    
    return None


@app.route('/api/scan/weekly/<market>', methods=['GET'])
def weekly_scan(market):
    """
    فحص أسبوعي للأسهم بناءً على شروط محددة:
    1. شمعة خضراء بإغلاق قريب من الأعلى
    2. الإغلاق متجاوز أو على حدود قمة سابقة (6 أشهر)
    3. الحجم أكبر من الشمعة السابقة
    """
    try:
        # التحقق من السوق
        if market not in ['saudi', 'us']:
            return jsonify({'error': 'Invalid market'}), 400
        
        results = []
        total_stocks = 0
        passed_green = 0
        passed_shadow = 0
        passed_peak = 0
        passed_volume = 0
        
        # جلب قائمة الأسهم
        use_db = USE_SUPABASE  # Local variable for this request
        
        if use_db:
            try:
                symbols = get_all_symbols(market)
                print(f"Using Supabase: {len(symbols)} symbols from {market}")
            except Exception as e:
                print(f"Supabase error, falling back to CSV: {e}")
                use_db = False
        
        if not use_db:
            # Fallback to CSV
            directory = os.path.join(BASE_DIR, 'data_sa' if market == 'saudi' else 'data_us')
            if not os.path.exists(directory):
                return jsonify({'error': f'Directory not found: {directory}'}), 404
            symbols = [f[:-4] for f in os.listdir(directory) if f.endswith('.csv')]
        
        # فحص كل سهم
        for symbol in symbols:
            total_stocks += 1
            
            try:
                # قراءة البيانات اليومية من Supabase أو CSV
                df = get_stock_data_from_source(symbol, market)
                
                if df is None or len(df) < 30:  # نحتاج بيانات كافية
                    continue
                
                # تحويل لبيانات أسبوعية (Date already converted in helper function)
                df.set_index('Date', inplace=True)
                weekly = df.resample('W').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
                
                if len(weekly) < 26:  # نحتاج 6 أشهر على الأقل (~26 أسبوع)
                    continue
                
                # آخر شمعة أسبوعية
                last_candle = weekly.iloc[-1]
                prev_candle = weekly.iloc[-2]
                prev_prev_candle = weekly.iloc[-3]  # الشمعة قبل السابقة
                
                # الشرط 1: شمعة خضراء بإغلاق قريب من الأعلى
                is_green = last_candle['Close'] > last_candle['Open']
                
                if not is_green:
                    continue
                
                passed_green += 1
                
                body_size = abs(last_candle['Close'] - last_candle['Open'])
                upper_shadow = last_candle['High'] - max(last_candle['Open'], last_candle['Close'])
                
                # الظل العلوي يجب أن يكون أقل من 30% من حجم الجسم
                # تجنب القسمة على صفر إذا كان الجسم صغير جداً
                if body_size > 0:
                    has_short_upper_shadow = upper_shadow < (body_size * 0.3)
                else:
                    # إذا كان الجسم = 0 (doji)، نتحقق من الظل فقط
                    has_short_upper_shadow = upper_shadow < 0.01
                
                if not has_short_upper_shadow:
                    continue
                
                passed_shadow += 1
                
                # الشرط 2: الإغلاق متجاوز أو على حدود قمة سابقة (6 أشهر)
                last_6_months = weekly.iloc[-26:-1]  # آخر 26 أسبوع (6 أشهر) عدا الأخير
                highest_in_6months = last_6_months['High'].max()
                
                # الإغلاق يجب أن يكون >= 98% من أعلى قمة
                close_near_or_above_peak = last_candle['Close'] >= (highest_in_6months * 0.98)
                
                if not close_near_or_above_peak:
                    continue
                
                passed_peak += 1
                
                # الشرط 3: الحجم أكبر من أي من الشمعتين السابقتين
                volume_increased = (last_candle['Volume'] > prev_candle['Volume']) or \
                                   (last_candle['Volume'] > prev_prev_candle['Volume'])
                
                if not volume_increased:
                    continue
                
                passed_volume += 1
                
                # جميع الشروط تحققت!
                # حساب نسبة الحجم مقارنة بأعلى من الشمعتين السابقتين
                max_prev_volume = max(prev_candle['Volume'], prev_prev_candle['Volume'])
                volume_ratio = (last_candle['Volume'] / max_prev_volume) if max_prev_volume > 0 else 1
                
                results.append({
                    'symbol': symbol,
                    'name': symbol,  # يمكن إضافة الأسماء لاحقاً
                    'close': round(float(last_candle['Close']), 2),
                    'open': round(float(last_candle['Open']), 2),
                    'high': round(float(last_candle['High']), 2),
                    'low': round(float(last_candle['Low']), 2),
                    'volume': int(last_candle['Volume']),
                    'prev_volume': int(max_prev_volume),
                    'volume_ratio': round(float(volume_ratio), 2),
                    'highest_6m': round(float(highest_in_6months), 2),
                    'change_percent': round(((last_candle['Close'] - last_candle['Open']) / last_candle['Open']) * 100, 2),
                    'date': weekly.index[-1].strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
        
        # ترتيب النتائج حسب نسبة التغيير
        results.sort(key=lambda x: x['change_percent'], reverse=True)
        
        # طباعة إحصائيات الفحص
        print(f"\n=== Weekly Scan Stats for {market.upper()} ===")
        print(f"Total stocks checked: {total_stocks}")
        print(f"Passed green candle: {passed_green}")
        print(f"Passed short shadow: {passed_shadow}")
        print(f"Passed peak level: {passed_peak}")
        print(f"Passed volume increase: {passed_volume}")
        print(f"Final results: {len(results)}")
        print("=" * 40)
        
        return jsonify({
            'success': True,
            'market': market,
            'count': len(results),
            'results': results,
            'stats': {
                'total_checked': total_stocks,
                'passed_green': passed_green,
                'passed_shadow': passed_shadow,
                'passed_peak': passed_peak,
                'passed_volume': passed_volume
            }
        })
        
    except Exception as e:
        print(f"Error in weekly scan: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/test/supabase', methods=['GET'])
def test_supabase():
    """Test Supabase connection and data"""
    try:
        if not USE_SUPABASE:
            return jsonify({
                'supabase_enabled': False,
                'message': 'Supabase is disabled, using CSV files'
            })
        
        # Test get_all_symbols
        us_symbols = get_all_symbols('us')
        saudi_symbols = get_all_symbols('saudi')
        
        # Get sample data for WELL
        well_data = get_stock_data('WELL', 'us')
        well_latest = None
        well_count = 0
        if well_data:
            well_count = len(well_data)
            if well_count > 0:
                well_latest = well_data[-1]['date']
        
        # Get sample data for last symbol
        last_us = sorted(us_symbols)[-1] if us_symbols else None
        last_data = get_stock_data(last_us, 'us') if last_us else None
        last_latest = None
        last_count = 0
        if last_data:
            last_count = len(last_data)
            if last_count > 0:
                last_latest = last_data[-1]['date']
        
        return jsonify({
            'supabase_enabled': True,
            'us_symbols_count': len(us_symbols),
            'saudi_symbols_count': len(saudi_symbols),
            'us_symbols_sample': us_symbols[:10] if us_symbols else [],
            'us_last_10_symbols': sorted(us_symbols)[-10:] if us_symbols else [],
            'well_test': {
                'symbol': 'WELL',
                'record_count': well_count,
                'latest_date': well_latest
            },
            'last_symbol_test': {
                'symbol': last_us,
                'record_count': last_count,
                'latest_date': last_latest
            },
            'message': 'Supabase is working correctly!'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'supabase_enabled': USE_SUPABASE
        }), 500


if __name__ == '__main__':
    print("=" * 50)
    print("STARTING MESHALSTOCK API SERVER")
    print("=" * 50)
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Server running at: http://{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}")
    print("\nAvailable Endpoints:")
    print("  - GET  /api/health              Check health")
    print("  - GET  /api/test/supabase       Test Supabase connection")
    print("  - POST /api/auth/login          Login (get token)")
    print("  - POST /api/auth/verify         Verify token")
    print("  - POST /api/fetch/saudi         Fetch Saudi data [AUTH]")
    print("  - POST /api/fetch/us            Fetch US data [AUTH]")
    print("  - GET  /api/market-summary      Market summary")
    print("  - GET  /api/status/<job_id>     Job status [AUTH]")
    print("  - GET  /api/jobs                List jobs [AUTH]")
    print("  - GET  /api/symbols/<market>    Get symbols")
    print("  - GET  /api/history/<market>    Get history")
    print("  - GET  /api/scan/fibo_gann      Scan opportunities")
    print("  - GET  /api/scan/weekly         Weekly scan")
    print("  - GET  /api/market-data         Market data")
    print("=" * 50)
    print(f"\n⚠️  SECURITY NOTES:")
    print(f"   - Change SECRET_KEY in .env file")
    print(f"   - Change ADMIN_PASSWORD in .env file")
    print(f"   - Configure ALLOWED_ORIGINS for production")
    print("=" * 50)
    
    # Initialize data if not present (background fetch)
    try:
        from initialize_data import initialize_data
        print("\n🔍 Checking for data files...")
        initialize_data(background=True)
    except Exception as e:
        print(f"⚠️  Could not initialize data: {e}")
        print("You can manually update data from the web interface.")
    
    print("\n" + "=" * 50)
    print("🚀 SERVER READY")
    print("=" * 50)
    
    # إعدادات التشغيل
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    
    app.run(debug=debug_mode, use_reloader=debug_mode, host=host, port=port, threaded=True)
