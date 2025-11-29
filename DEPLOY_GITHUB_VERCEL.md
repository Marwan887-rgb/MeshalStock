# 🚀 دليل النشر على GitHub و Vercel

## ⚠️ تنبيه مهم

**Vercel لا يدعم Flask بشكل كامل** - يدعم فقط Serverless Functions المحدودة.

**البدائل الأفضل:**
1. **Render.com** - يدعم Flask بشكل كامل ✅ (مجاني)
2. **Railway.app** - سهل ويدعم Python ✅ (مجاني)
3. **PythonAnywhere** - متخصص في Python ✅ (مجاني)
4. **Heroku** - الأشهر (مدفوع)

---

## 📋 الخطوة 1: تحضير المشروع

### 1. تثبيت Git (إذا لم يكن مثبتاً)
```bash
# تحميل من https://git-scm.com/downloads
```

### 2. إنشاء ملف .env للإنتاج
أنشئ ملف `.env` في المجلد الرئيسي:
```bash
FLASK_ENV=production
SECRET_KEY=YOUR_SECRET_KEY_HERE
ADMIN_PASSWORD=YOUR_STRONG_PASSWORD
JWT_SECRET_KEY=YOUR_JWT_SECRET_KEY
ALLOWED_ORIGINS=https://your-app-name.vercel.app
```

⚠️ **لا تنشر ملف `.env` على GitHub!** (موجود في `.gitignore`)

---

## 📋 الخطوة 2: رفع المشروع على GitHub

### 1. إنشاء Repository على GitHub
1. اذهب إلى https://github.com
2. اضغط **New Repository**
3. اسم المشروع: `MeshalStock`
4. اجعله **Private** (خاص) للأمان
5. **لا تضف** README أو .gitignore (موجودان بالفعل)

### 2. رفع الكود من Terminal/PowerShell
```bash
# افتح Terminal في مجلد المشروع
cd "c:\Users\mrn88\OneDrive\المستندات\MeshalStock"

# تهيئة Git
git init

# إضافة جميع الملفات
git add .

# أول commit
git commit -m "Initial commit - MeshalStock Web App"

# ربط بـ GitHub (استبدل USERNAME باسمك)
git remote add origin https://github.com/USERNAME/MeshalStock.git

# رفع الكود
git branch -M main
git push -u origin main
```

---

## 📋 الخطوة 3: النشر على Vercel (محدود)

### ⚠️ تحذير: Vercel لا يدعم:
- Background jobs (تحديث الأسهم)
- Long-running processes
- File system write (حفظ CSV)

**يعمل فقط:**
- عرض الصفحات
- API البسيطة (market-summary فقط)

### خطوات النشر على Vercel:

1. **إنشاء حساب على Vercel**
   - اذهب إلى https://vercel.com
   - سجل دخول بـ GitHub

2. **ربط المشروع**
   - اضغط **Import Project**
   - اختر `MeshalStock` من GitHub
   - اضغط **Import**

3. **إعداد Environment Variables**
   في Vercel Dashboard -> Settings -> Environment Variables:
   ```
   SECRET_KEY=your-secret-key
   ADMIN_PASSWORD=your-password
   JWT_SECRET_KEY=your-jwt-key
   ALLOWED_ORIGINS=https://your-app.vercel.app
   FLASK_ENV=production
   ```

4. **Deploy**
   - اضغط **Deploy**
   - انتظر 2-3 دقائق

---

## 🌟 البديل الأفضل: Render.com

### لماذا Render أفضل؟
✅ يدعم Flask بشكل كامل
✅ يدعم Background workers
✅ يدعم File storage
✅ مجاني للمشاريع الصغيرة
✅ Auto-deploy من GitHub

### خطوات النشر على Render:

1. **إنشاء حساب**
   - اذهب إلى https://render.com
   - سجل بـ GitHub

2. **New Web Service**
   - اختر `MeshalStock` repository
   - اسم الخدمة: `meshalstock`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn api_server:app`

3. **Environment Variables**
   أضف نفس المتغيرات:
   ```
   SECRET_KEY=...
   ADMIN_PASSWORD=...
   JWT_SECRET_KEY=...
   ALLOWED_ORIGINS=https://meshalstock.onrender.com
   FLASK_ENV=production
   ```

4. **Deploy**
   - اضغط **Create Web Service**
   - انتظر 5-10 دقائق
   - ستحصل على رابط: `https://meshalstock.onrender.com`

---

## 🔄 التحديثات المستقبلية

بعد رفع الكود على GitHub، أي تحديث:

```bash
# إضافة التغييرات
git add .

# Commit
git commit -m "وصف التحديث"

# رفع للـ GitHub
git push

# Vercel/Render سيعيد النشر تلقائياً
```

---

## 🛠️ استكشاف الأخطاء

### مشكلة: Vercel Serverless Timeout
**الحل:** استخدم Render أو Railway

### مشكلة: ملفات CSV لا تُحفظ
**الحل:** Vercel لا يدعم file storage - استخدم Render

### مشكلة: yfinance بطيء جداً
**الحل:** أضف Redis cache على Render

---

## 📞 الدعم

إذا واجهت مشاكل:
1. تحقق من Logs في Dashboard
2. تأكد من Environment Variables
3. تأكد من `requirements.txt` محدث

---

## 🎯 التوصية النهائية

**للمشروع الكامل (مع جميع الميزات):**
→ استخدم **Render.com** أو **Railway.app**

**للـ Frontend فقط (بدون تحديث الأسهم):**
→ يمكن استخدام Vercel

---

هل تريد المتابعة مع Vercel أم الانتقال لـ Render؟
