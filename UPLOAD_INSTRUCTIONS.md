# 🚀 تعليمات رفع المشروع على GitHub و Render و Vercel

## الخطوة 1️⃣: رفع على GitHub

### 1. إنشاء Repository على GitHub:
1. اذهب إلى: https://github.com/new
2. اسم المشروع: `MeshalStock`
3. الوصف: `نظام تحليل الأسهم المتقدم`
4. اختر **Private**
5. اضغط **Create repository**

### 2. رفع الكود من PowerShell:

```powershell
# انتقل لمجلد المشروع
cd "c:\Users\mrn88\OneDrive\المستندات\MeshalStock"

# تهيئة Git (إذا لم يتم بعد)
git init

# إضافة جميع الملفات
git add .

# عمل Commit
git commit -m "Initial commit - MeshalStock Web Application"

# ربط بـ GitHub (استبدل YOUR_USERNAME باسمك على GitHub)
git remote add origin https://github.com/YOUR_USERNAME/MeshalStock.git

# رفع الكود
git branch -M main
git push -u origin main
```

---

## الخطوة 2️⃣: توليد المفاتيح السرية

قبل النشر، احتفظ بهذه المفاتيح (ستحتاجها لاحقاً):

```powershell
# توليد SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# توليد JWT_SECRET_KEY
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

**احفظ النتائج** - ستحتاجها في الخطوات القادمة!

---

## الخطوة 3️⃣: النشر على Render.com (الأساسي - مجاني)

### 1. إنشاء حساب:
- اذهب إلى: https://render.com
- اضغط **Get Started** أو **Sign Up**
- اختر **Sign up with GitHub**
- امنح Render الصلاحيات

### 2. إنشاء Web Service:
1. من Dashboard، اضغط **New +** → **Web Service**
2. اضغط **Connect** بجانب repository `MeshalStock`
3. املأ المعلومات:

```
Name: meshalstock
Region: اختر الأقرب (Frankfurt أو Singapore)
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT api_server:app
```

### 3. إضافة Environment Variables:

في قسم **Environment Variables**، أضف:

```
SECRET_KEY=<النتيجة من الخطوة 2>
JWT_SECRET_KEY=<النتيجة من الخطوة 2>
ADMIN_PASSWORD=<كلمة المرور التي تريدها>
FLASK_ENV=production
ALLOWED_ORIGINS=*
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=30
TOKEN_EXPIRY_HOURS=24
```

### 4. اختر الخطة:
- اختر **Free** (مجاني)
- اضغط **Create Web Service**

### 5. انتظر النشر:
- سيستغرق 5-10 دقائق
- ستحصل على رابط مثل: `https://meshalstock.onrender.com`

---

## الخطوة 4️⃣: النشر على Vercel (اختياري - للواجهة فقط)

⚠️ **تنبيه**: Vercel لا يدعم جميع ميزات Flask (خاصة تحديث البيانات)

### 1. إنشاء حساب:
- اذهب إلى: https://vercel.com
- اضغط **Sign Up**
- اختر **Continue with GitHub**

### 2. Import Project:
1. من Dashboard، اضغط **Add New...** → **Project**
2. اختر `MeshalStock` من القائمة
3. اضغط **Import**

### 3. إعداد المشروع:
```
Framework Preset: Other
Build Command: (اتركه فارغاً)
Output Directory: (اتركه فارغاً)
Install Command: pip install -r requirements.txt
```

### 4. Environment Variables:
أضف نفس المتغيرات من Render + هذا:
```
PYTHON_VERSION=3.11
```

### 5. Deploy:
- اضغط **Deploy**
- انتظر 2-3 دقائق
- ستحصل على رابط مثل: `https://meshal-stock.vercel.app`

---

## الخطوة 5️⃣: تحديث ALLOWED_ORIGINS

بعد الحصول على روابط Render و Vercel:

### في Render Dashboard:
1. اذهب إلى **Environment**
2. عدّل `ALLOWED_ORIGINS`:
```
ALLOWED_ORIGINS=https://meshalstock.onrender.com,https://meshal-stock.vercel.app
```
3. احفظ التغييرات (سيعيد النشر تلقائياً)

---

## 🎯 النتيجة النهائية:

### Render (التطبيق الكامل):
✅ جميع الميزات تعمل
✅ تحديث البيانات
✅ API كامل
🔗 الرابط: `https://meshalstock.onrender.com`

### Vercel (الواجهة + API البسيط):
✅ الواجهة الأمامية
✅ عرض البيانات
⚠️ تحديث البيانات قد لا يعمل
🔗 الرابط: `https://meshal-stock.vercel.app`

---

## 🔄 التحديثات المستقبلية:

بعد رفع الكود على GitHub، أي تحديث:

```powershell
# إضافة التغييرات
git add .

# Commit مع وصف
git commit -m "وصف التحديث هنا"

# رفع للـ GitHub
git push

# Render و Vercel سيحدثان تلقائياً! 🎉
```

---

## 📞 استكشاف الأخطاء:

### مشكلة: Render يعطي خطأ 503
**الحل**: تحقق من Logs في Dashboard

### مشكلة: Vercel Timeout
**الحل**: طبيعي - استخدم Render للميزات الكاملة

### مشكلة: لا يظهر البيانات
**الحل**: تحقق من Environment Variables

---

## ✅ قائمة التحقق:

- [ ] رفع الكود على GitHub
- [ ] نشر على Render
- [ ] إضافة Environment Variables في Render
- [ ] نشر على Vercel (اختياري)
- [ ] إضافة Environment Variables في Vercel
- [ ] تحديث ALLOWED_ORIGINS
- [ ] اختبار الرابطين

---

## 🎉 تهانينا!

تطبيقك الآن على الإنترنت! 🚀
