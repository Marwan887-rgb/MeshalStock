import yfinance as yf
import pandas as pd
import os
import time
import argparse
import sys
from datetime import datetime, timedelta

# Supabase integration (optional - falls back to CSV only)
try:
    from supabase_client import insert_stock_data_batch
    USE_SUPABASE = True
except ImportError:
    USE_SUPABASE = False
    print("⚠ Supabase not available, saving to CSV only")

# --- الإعدادات ---
# تحديد المجلد الأساسي بناءً على موقع الملف الحالي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SYMBOLS_FILE = os.path.join(BASE_DIR, 'symbols_sa.txt')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data_sa')
DEFAULT_START_DATE = '2024-11-01'  # تاريخ البداية الافتراضي للأسهم الجديدة
DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')    # تاريخ النهاية (اليوم)
LOG_FILE = os.path.join(BASE_DIR, 'saudi_data_fetch.log')

# --- الدالات ---

def setup_logging():
    """إعداد تسجيل الأحداث في ملف وسطر الأوامر."""
    def log(message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        try:
            print(log_message)
        except UnicodeEncodeError:
            # في حالة فشل طباعة الرموز العربية في الكونسول
            print(log_message.encode('utf-8', errors='ignore').decode('ascii', errors='ignore'))
            
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    return log

def get_symbols_from_file(file_path, log):
    """
    تقرأ رموز الأسهم من ملف CSV أو TXT.
    يفترض أن العمود الأول يحتوي على الرموز.
    """
    if not os.path.exists(file_path):
        log(f"E: لم يتم العثور على ملف الرموز {file_path}")
        return None
    try:
        df = pd.read_csv(file_path)
        if 'Symbol' not in df.columns:
            log(f"E: ملف الرموز {file_path} لا يحتوي على عمود 'Symbol'.")
            return None
        # إزالة أي رموز تحتوي على '^' وأي قيم فارغة
        symbols = df['Symbol'].dropna().astype(str)
        symbols = symbols[~symbols.str.contains(r'\^', na=False)]
        return symbols.tolist()
    except Exception as e:
        log(f"E: حدث خطأ عند قراءة ملف الرموز {file_path}: {e}")
        return None

def get_last_date_from_file(filepath, log):
    """
    قراءة آخر تاريخ من ملف CSV موجود.
    يرجع None إذا لم يكن الملف موجوداً أو فارغاً.
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        # محاولة قراءة الملف مع تخطي الترويسة المعقدة (3 أسطر)
        # نفترض أن الملف قد يكون بالتنسيق القديم (3 أسطر) أو الجديد (سطر واحد)
        
        # قراءة السطر الأول للتحقق
        with open(filepath, 'r') as f:
            first_line = f.readline()
        
        if 'Price' in first_line and 'Ticker' not in first_line:
             # احتمال أن يكون ملفاً قديماً مع ترويسة معقدة تبدأ بـ Price
             # لكن لنتأكد أكثر، الملفات القديمة تبدأ بـ Price,Close... والسطر الثاني Ticker...
             pass

        # القراءة الآمنة: نحاول قراءة الملف كملف عادي أولاً
        try:
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            # التحقق مما إذا كان التاريخ في الفهرس
            if isinstance(df.index, pd.DatetimeIndex) and not df.empty:
                return df.index.max()
        except:
            pass
            
        # محاولة قراءة الملف بتخطي 3 أسطر (للملفات القديمة)
        try:
            df = pd.read_csv(filepath, skiprows=3, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
            df['Date'] = pd.to_datetime(df['Date'])
            if not df.empty:
                return df['Date'].max()
        except:
            pass

        return None

    except Exception as e:
        log(f"⚠️ خطأ في قراءة الملف {filepath}: {e}")
        return None

def save_to_supabase(symbol, data, log):
    """
    حفظ البيانات في Supabase
    
    Args:
        symbol: رمز السهم
        data: DataFrame مع index = Date وأعمدة: Open, High, Low, Close, Volume
        log: logging function
    
    Returns:
        عدد السجلات المحفوظة أو 0 في حالة الفشل
    """
    if not USE_SUPABASE:
        return 0
    
    try:
        # تحويل DataFrame إلى قائمة من السجلات
        records = []
        for date_index, row in data.iterrows():
            record = {
                'symbol': symbol,
                'market': 'saudi',
                'date': date_index.strftime('%Y-%m-%d'),
                'open': float(row['Open']) if 'Open' in row and pd.notna(row['Open']) else 0,
                'high': float(row['High']) if 'High' in row and pd.notna(row['High']) else 0,
                'low': float(row['Low']) if 'Low' in row and pd.notna(row['Low']) else 0,
                'close': float(row['Close']) if 'Close' in row and pd.notna(row['Close']) else 0,
                'volume': int(row['Volume']) if 'Volume' in row and pd.notna(row['Volume']) else 0
            }
            records.append(record)
        
        # رفع على Supabase (batch)
        if records:
            batch_size = 500
            total_uploaded = 0
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                count = insert_stock_data_batch(batch)
                total_uploaded += count
            
            log(f"[Supabase] تم رفع {total_uploaded} سجل")
            return total_uploaded
        
        return 0
        
    except Exception as e:
        log(f"[Supabase] تحذير: فشل الرفع على Supabase: {e}")
        return 0


def fetch_and_update_data(symbol, log):
    """
    جلب البيانات الجديدة وتحديث الملف.
    - إذا كان الملف موجوداً: يجلب البيانات من آخر تاريخ حتى اليوم
    - إذا لم يكن موجوداً: يجلب البيانات من تاريخ البداية الافتراضي
    """
    output_filename = os.path.join(OUTPUT_DIR, f"{symbol}.csv")
    
    # تحديد تاريخ البداية
    last_date = get_last_date_from_file(output_filename, log)
    
    if last_date:
        # إضافة يوم واحد لآخر تاريخ موجود
        start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
        log(f"[ملف موجود] آخر تاريخ: {last_date.strftime('%Y-%m-%d')}")
        log(f"[تحديث] جلب البيانات من {start_date} حتى {DEFAULT_END_DATE}...")
        is_update = True
    else:
        start_date = DEFAULT_START_DATE
        log(f"[ملف جديد] جلب البيانات من {start_date} حتى {DEFAULT_END_DATE}...")
        is_update = False
    
    # تاريخ النهاية المحدد
    end_date = DEFAULT_END_DATE
    
    # التحقق من أن هناك بيانات جديدة محتملة
    if is_update and start_date > end_date:
        log(f"[OK] البيانات محدثة بالفعل - لا حاجة للتحديث")
        return 'up_to_date'
    
    try:
        # جلب البيانات الجديدة
        log(f"[جلب] جاري الاتصال بـ yfinance...")
        new_data = yf.download(
            tickers=symbol,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=False
        )
        
        if new_data.empty:
            log(f"[تحذير] لا توجد بيانات جديدة للسهم {symbol}")
            return 'no_new_data'
        
        # معالجة الأعمدة (Flatten MultiIndex)
        if isinstance(new_data.columns, pd.MultiIndex):
            # إذا كانت الأعمدة MultiIndex (Price, Ticker)، نحذف مستوى Ticker
            try:
                new_data.columns = new_data.columns.droplevel(1)
            except:
                pass
        
        # التأكد من ترتيب الأعمدة وتوحيدها
        desired_order = ['Close', 'High', 'Low', 'Open', 'Volume']
        # التحقق من وجود الأعمدة المطلوبة
        available_cols = [col for col in desired_order if col in new_data.columns]
        if available_cols:
            new_data = new_data[available_cols]
        
        # إذا كان الملف موجوداً: دمج البيانات
        if is_update and os.path.exists(output_filename):
            # قراءة الملف القديم بذكاء (التعامل مع التنسيقين)
            try:
                # محاولة قراءة التنسيق الجديد (سطر واحد)
                old_data = pd.read_csv(output_filename, index_col=0, parse_dates=True)
                
                # إذا لم يكن الفهرس تواريخ، قد يكون التنسيق القديم
                if not isinstance(old_data.index, pd.DatetimeIndex):
                    raise ValueError("Not a datetime index")
            except:
                # محاولة قراءة التنسيق القديم (تخطي 3 أسطر)
                old_data = pd.read_csv(output_filename, skiprows=3, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
                old_data['Date'] = pd.to_datetime(old_data['Date'])
                old_data.set_index('Date', inplace=True)
            
            # دمج البيانات القديمة والجديدة
            combined_data = pd.concat([old_data, new_data])
            
            # إزالة التكرارات والترتيب حسب التاريخ
            combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
            combined_data = combined_data.sort_index()
            
            # حفظ البيانات المدمجة (بتنسيق نظيف)
            combined_data.to_csv(output_filename)
            log(f"[نجاح] تم تحديث الملف - أضيف {len(new_data)} صف جديد")
            log(f"[احصائية] إجمالي البيانات الآن: {len(combined_data)} صف")
            
            # حفظ في Supabase (البيانات الجديدة فقط)
            save_to_supabase(symbol, new_data, log)
            
            return 'updated'
        else:
            # ملف جديد: حفظ البيانات مباشرة
            new_data.to_csv(output_filename)
            log(f"[نجاح] تم إنشاء ملف جديد - {len(new_data)} صف")
            
            # حفظ في Supabase
            save_to_supabase(symbol, new_data, log)
            
            return 'new'
            
    except Exception as e:
        log(f"[خطأ] خطأ أثناء جلب/تحديث البيانات لـ {symbol}: {e}")
        return 'failed'

# --- التنفيذ الرئيسي ---
if __name__ == "__main__":
    # إعداد معالجة الوسائط
    parser = argparse.ArgumentParser(description='Fetch Saudi Stock Data')
    parser.add_argument('--workers', type=int, default=1, help='Number of workers (ignored in this version)')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--symbols', type=str, help='Comma separated symbols for testing')
    args = parser.parse_args()

    log = setup_logging()
    
    log("=" * 60)
    log("*** بدء عملية تحديث بيانات الأسهم السعودية ***")
    log("=" * 60)
    
    # التأكد من وجود مجلد المخرجات
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        log(f"[مجلد] تم إنشاء المجلد: {OUTPUT_DIR}")

    # جلب قائمة الرموز
    if args.test and args.symbols:
        symbols = args.symbols.split(',')
        log(f"[اختبار] استخدام الرموز المحددة: {symbols}")
    else:
        symbols = get_symbols_from_file(SYMBOLS_FILE, log)
    
    if not symbols:
        log(f"[خطأ] فشل في الحصول على قائمة الرموز من {SYMBOLS_FILE}")
    else:
        log(f"[معلومة] تم العثور على {len(symbols)} رمزًا")
        log("=" * 60)
        
        total_symbols = len(symbols)
        stats = {'new': 0, 'updated': 0, 'up_to_date': 0, 'failed': 0, 'no_new_data': 0}
        
        for i, symbol in enumerate(symbols):
            log(f"\n--- التقدم: {i+1}/{total_symbols} ({((i+1)/total_symbols*100):.1f}%) ---")
            log(f"[معالجة] {symbol}")
            
            result = fetch_and_update_data(symbol, log)
            stats[result] = stats.get(result, 0) + 1
            
            # عرض الإحصائيات الحالية
            log(f"[احصائيات] جديد: {stats['new']}, محدث: {stats['updated']}, محدث مسبقاً: {stats['up_to_date']}, فشل: {stats['failed']}")
            
            # تأخير بسيط بين الطلبات
            time.sleep(1)
        
        log("\n" + "=" * 60)
        log("*** انتهت عملية تحديث البيانات! ***")
        log("=" * 60)
        log(f"[النتائج النهائية]:")
        log(f"   [+] ملفات جديدة: {stats['new']}")
        log(f"   [+] ملفات محدثة: {stats['updated']}")
        log(f"   [+] ملفات محدثة بالفعل: {stats['up_to_date']}")
        log(f"   [-] فشل: {stats['failed']}")
        log(f"   - لا توجد بيانات جديدة: {stats.get('no_new_data', 0)}")
        log("=" * 60)