import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime, timedelta
from io import StringIO

# --- الإعدادات ---
DATA_DIR = 'data_us'
LOG_FILE = 'us_data_update.log'
COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

# --- الدالات ---

def setup_logging():
    """إعداد تسجيل الأحداث في ملف وسطر الأوامر."""
    def log(message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    return log

def read_and_clean_csv(file_path, log):
    """
    يقرأ ملف CSV، وينظفه، ويوحد الأعمدة والبيانات لضمان التوافق.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # تجاهل الأسطر الفارغة تماماً
            lines = [line for line in f if line.strip() and line.strip() != ',,,,,']
        
        if not lines:
            return None

        # التحقق من وجود الترويسة لتحديد من أين تبدأ البيانات الفعلية
        has_header = 'date' in lines[0].lower()
        start_row = 1 if has_header else 0
        
        # قراءة البيانات بدون ترويسة وفرض أسماء الأعمدة الصحيحة
        df = pd.read_csv(StringIO("\n".join(lines[start_row:])), header=None, names=COLUMNS)

        # --- تنظيف وتوحيد شامل للبيانات ---
        # 1. تحويل عمود التاريخ والتأكد من عدم وجود أخطاء
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # 2. تحويل الأعمدة الرقمية والتأكد من عدم وجود نصوص
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 3. إزالة أي صفوف تحتوي على قيم فارغة في الأعمدة الأساسية
        df.dropna(subset=COLUMNS, inplace=True)
        
        # 4. التأكد من أن نوع البيانات صحيح (Volume يجب أن يكون عددًا صحيحًا)
        if 'Volume' in df.columns and not df.empty:
            df['Volume'] = df['Volume'].astype(int)

        return df

    except Exception as e:
        log(f"حدث خطأ غير متوقع أثناء قراءة وتنظيف {os.path.basename(file_path)}: {e}")
        return None


def update_stock_data(log):
    """تحديث بيانات الأسهم للملفات الموجودة."""
    log("=== بدء عملية تحديث بيانات السوق الأمريكي ===")
    
    if not os.path.exists(DATA_DIR):
        log(f"خطأ: مجلد البيانات '{DATA_DIR}' غير موجود.")
        return

    files_to_update = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    total_files = len(files_to_update)
    
    if total_files == 0:
        log("لا توجد ملفات لتحديثها.")
        return
        
    log(f"تم العثور على {total_files} ملف لتحديثه.")

    # لجلب بيانات اليوم الحالي، يجب أن يكون تاريخ النهاية هو الغد
    end_date = datetime.now() + timedelta(days=1)

    for i, filename in enumerate(files_to_update):
        symbol = filename.replace('.csv', '')
        file_path = os.path.join(DATA_DIR, filename)
        log(f"--- ({i+1}/{total_files}) جاري معالجة {symbol} ---")

        try:
            df = read_and_clean_csv(file_path, log)
            
            if df is None or df.empty:
                log(f"⚠️ الملف {filename} فارغ أو لا يحتوي على بيانات صالحة بعد التنظيف. سيتم تخطيه.")
                continue
            
            # التأكد من أن التواريخ مرتبة قبل الحصول على آخر تاريخ
            df.sort_values(by='Date', inplace=True)
            last_date = df['Date'].max()
            start_date = last_date + timedelta(days=1)

            # مقارنة التواريخ فقط بدون الوقت
            if start_date.date() >= datetime.now().date():
                log(f"✅ البيانات لـ {symbol} محدثة بالفعل.")
                # نعيد حفظ الملف للتأكد من نظافته وتنسيقه الموحد
                df.to_csv(file_path, index=False, header=True)
                continue

            log(f"آخر تاريخ: {last_date.strftime('%Y-%m-%d')}. جلب البيانات من {start_date.strftime('%Y-%m-%d')}")

            new_data = yf.download(
                tickers=symbol,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                auto_adjust=False,
                progress=False
            )

            if new_data.empty:
                log(f"لا يوجد بيانات جديدة لـ {symbol}.")
                # نعيد حفظ الملف لضمان تنسيقه حتى لو لم يتغير شيء
                df.to_csv(file_path, index=False, header=True)
                continue
            
            new_data.reset_index(inplace=True)
            
            # فلترة الأعمدة المطلوبة فقط من البيانات الجديدة
            new_data = new_data[[col for col in COLUMNS if col in new_data.columns]]

            combined_df = pd.concat([df, new_data], ignore_index=True)
            combined_df.drop_duplicates(subset=['Date'], keep='last', inplace=True)
            combined_df.sort_values(by='Date', inplace=True)
            
            # التأكد من أنواع البيانات قبل الحفظ
            for col in ['Open', 'High', 'Low', 'Close']:
                 combined_df[col] = pd.to_numeric(combined_df[col])
            combined_df['Volume'] = pd.to_numeric(combined_df['Volume'])
            combined_df.dropna(inplace=True)
            
            if 'Volume' in combined_df.columns and not combined_df.empty:
                combined_df['Volume'] = combined_df['Volume'].astype(int)

            # حفظ الملف النهائي مع الترويسة
            combined_df.to_csv(file_path, index=False, header=True)
            
            log(f"✅ تم تحديث {symbol} بـ {len(new_data)} صف جديد.")

        except pd.errors.EmptyDataError:
            log(f"⚠️ الملف {filename} فارغ. سيتم تخطيه.")
        except Exception as e:
            log(f"❌ حدث خطأ أثناء تحديث {symbol}: {e}")
        
        time.sleep(1)

    log("🎉 انتهت عملية تحديث جميع البيانات للسوق الأمريكي.")

if __name__ == "__main__":
    log = setup_logging()
    update_stock_data(log)
