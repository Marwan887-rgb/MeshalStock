# 🚀 دليل إعداد Supabase لـ MeshalStock

هذا الدليل يشرح كيفية إعداد قاعدة بيانات Supabase لتسريع أداء التطبيق.

---

## 📋 المتطلبات

- حساب Supabase (مجاني) - [supabase.com](https://supabase.com)
- Python 3.8+ مع pip
- بيانات CSV موجودة في `data_sa/` و `data_us/`

---

## 🎯 الفوائد

| الميزة | قبل (CSV) | بعد (Database) |
|--------|-----------|----------------|
| **السرعة** | 5-7 ثوان | 0.5-1 ثانية ⚡ |
| **Deployment** | 15 دقيقة | فوري ✅ |
| **البيانات** | تُحذف | دائمة 💾 |
| **التحديث** | بطيء | سريع 🚀 |

---

## 📝 خطوات الإعداد

### 1️⃣ إنشاء مشروع Supabase

1. اذهب إلى [supabase.com](https://supabase.com)
2. سجل دخول أو أنشئ حساب جديد
3. اضغط **"New Project"**
4. املأ البيانات:
   - **Name**: MeshalStock
   - **Database Password**: احفظه في مكان آمن
   - **Region**: اختر الأقرب (مثل: Europe West)
5. اضغط **"Create new project"**
6. انتظر 2-3 دقائق حتى يكتمل الإعداد

---

### 2️⃣ الحصول على API Keys

بعد إنشاء المشروع:

1. اذهب إلى **Settings** (⚙️) في الشريط الجانبي
2. اختر **API**
3. ستجد:
   - **Project URL**: انسخه
   - **anon public key**: انسخه

مثال:
```
URL: https://jeeqdxewehgnhvuvrprs.supabase.co
Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 3️⃣ إضافة Keys إلى .env

افتح ملف `.env` (أو أنشئه من `.env.example`) وأضف:

```bash
SUPABASE_URL=https://jeeqdxewehgnhvuvrprs.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

⚠️ **مهم:** لا ترفع ملف `.env` على GitHub!

---

### 4️⃣ إنشاء الجدول (Table)

1. في Supabase Dashboard، اذهب إلى **SQL Editor** (أيقونة <>)
2. اضغط **"New query"**
3. انسخ محتويات ملف `supabase_schema.sql`
4. الصقه في المحرر
5. اضغط **"Run"** (أو Ctrl+Enter)
6. يجب أن تظهر رسالة: `Table created successfully!`

---

### 5️⃣ تثبيت المكتبات

```bash
pip install -r requirements.txt
```

هذا سيثبت `supabase==2.3.0` مع بقية المكتبات.

---

### 6️⃣ رفع البيانات من CSV إلى Supabase

```bash
python migrate_to_supabase.py
```

هذا الأمر سيقوم بـ:
- قراءة جميع ملفات CSV
- تحويلها إلى records
- رفعها على Supabase (batch upload)

⏱️ **الوقت المتوقع:** 15-20 دقيقة لـ 500+ سهم

---

### 7️⃣ التحقق من البيانات

في Supabase Dashboard:

1. اذهب إلى **Table Editor** (أيقونة الجدول)
2. اختر جدول `stock_data`
3. يجب أن تشاهد البيانات

أو من Python:

```python
python supabase_client.py
```

يجب أن تظهر: `✓ Successfully connected to Supabase!`

---

## 🔧 الاستخدام

### الحصول على بيانات سهم:

```python
from supabase_client import get_stock_data

# جلب آخر 6 أشهر لسهم AAPL
data = get_stock_data('AAPL', 'us', start_date='2024-06-01')
print(f"Found {len(data)} records")
```

### الحصول على جميع الرموز:

```python
from supabase_client import get_all_symbols

symbols_us = get_all_symbols('us')
symbols_sa = get_all_symbols('saudi')

print(f"US: {len(symbols_us)} stocks")
print(f"Saudi: {len(symbols_sa)} stocks")
```

### إضافة بيانات جديدة:

```python
from supabase_client import insert_stock_data

insert_stock_data(
    symbol='AAPL',
    market='us',
    date='2024-11-30',
    open_price=150.0,
    high=152.0,
    low=149.0,
    close=151.5,
    volume=50000000
)
```

---

## 📊 بنية الجدول

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT | Primary key (auto) |
| `symbol` | TEXT | رمز السهم (AAPL, 2222.SR) |
| `market` | TEXT | 'saudi' أو 'us' |
| `date` | DATE | تاريخ التداول |
| `open` | NUMERIC | سعر الافتتاح |
| `high` | NUMERIC | أعلى سعر |
| `low` | NUMERIC | أدنى سعر |
| `close` | NUMERIC | سعر الإغلاق |
| `volume` | BIGINT | حجم التداول |
| `created_at` | TIMESTAMP | وقت الإضافة (auto) |

### Indexes (للسرعة):
- `idx_stock_symbol` - بحث سريع بالرمز
- `idx_stock_market` - تصفية حسب السوق
- `idx_stock_date` - ترتيب حسب التاريخ
- `idx_stock_symbol_date` - أسرع استعلام

---

## 🔒 الأمان

- ✅ Row Level Security (RLS) مفعّل
- ✅ القراءة متاحة للجميع (public)
- ✅ الكتابة محمية بـ API key
- ✅ لا يمكن حذف البيانات من الواجهة الأمامية

---

## 🚀 النشر على Render

بعد إعداد Supabase:

1. أضف Environment Variables في Render:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_key_here
   ```

2. ادفع التعديلات:
   ```bash
   git add .
   git commit -m "feat: add Supabase integration"
   git push
   ```

3. Render سيعيد النشر تلقائياً
4. البيانات ستكون جاهزة فوراً! ✅

---

## ❓ استكشاف الأخطاء

### خطأ: "Failed to connect to Supabase"
- تأكد من `SUPABASE_KEY` في ملف `.env`
- تأكد من `SUPABASE_URL` صحيح

### خطأ: "Table 'stock_data' does not exist"
- قم بتشغيل `supabase_schema.sql` في SQL Editor

### خطأ: "Permission denied"
- تأكد من Row Level Security policies مضبوطة
- استخدم service role key للكتابة

### البيانات لا تظهر
- تأكد من `migrate_to_supabase.py` اكتمل بنجاح
- تحقق في Table Editor في Supabase Dashboard

---

## 📞 الدعم

إذا واجهت مشاكل:
1. راجع Supabase logs في Dashboard
2. تحقق من Python errors في console
3. تأكد من API keys صحيحة

---

## 🎉 الخلاصة

بعد إعداد Supabase:
- ⚡ أداء أسرع 10x
- 💾 بيانات دائمة
- 🚀 deployment فوري
- 📊 إدارة سهلة

**وقت الإعداد الكلي:** ~30 دقيقة (مرة واحدة فقط!)
