# 🚀 دليل نشر MeshalStock على الويب

## 📋 متطلبات النشر

### المتطلبات الأساسية:
- Python 3.8 أو أحدث
- خادم ويب (VPS/Cloud Server)
- Domain name (اختياري ولكن موصى به)
- SSL Certificate (للأمان)

---

## 🔧 الإعداد المحلي

### 1. تثبيت المكتبات:
```bash
pip install -r requirements.txt
```

### 2. إعداد المتغيرات البيئية:
```bash
# انسخ ملف المثال
cp .env.example .env

# عدّل الملف .env وضع قيمك الخاصة:
nano .env
```

**⚠️ مهم جداً:**
- غيّر `SECRET_KEY` إلى قيمة عشوائية قوية
- غيّر `JWT_SECRET_KEY` إلى قيمة عشوائية مختلفة
- غيّر `ADMIN_PASSWORD` من القيمة الافتراضية
- حدد `ALLOWED_ORIGINS` إذا كنت تعرف نطاقك

### 3. تشغيل محلي للاختبار:
```bash
python api_server.py
```

افتح المتصفح على: http://localhost:5000

---

## 🌐 النشر على الخادم

### الطريقة 1: النشر باستخدام Gunicorn (موصى به)

#### 1. تثبيت Gunicorn:
```bash
pip install gunicorn
```

#### 2. تشغيل التطبيق:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

**الخيارات:**
- `-w 4`: عدد العمليات (workers) - اضبطه حسب موارد الخادم
- `-b 0.0.0.0:5000`: الاستماع على جميع الواجهات على المنفذ 5000
- `--timeout 120`: زيادة مهلة الطلبات (مفيد لجلب البيانات)

#### 3. إنشاء ملف systemd service:
```bash
sudo nano /etc/systemd/system/meshalstock.service
```

أضف المحتوى التالي:
```ini
[Unit]
Description=MeshalStock Web Application
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/MeshalStock
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 api_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4. تفعيل الخدمة:
```bash
sudo systemctl enable meshalstock
sudo systemctl start meshalstock
sudo systemctl status meshalstock
```

---

### الطريقة 2: النشر على PythonAnywhere

#### 1. رفع الملفات:
- قم بتحميل جميع الملفات إلى PythonAnywhere
- أو استخدم Git: `git clone your-repo-url`

#### 2. إعداد Web App:
- اذهب إلى Web tab
- أضف web app جديد
- اختر Flask
- حدد مسار `api_server.py`

#### 3. إعداد WSGI:
عدّل ملف `wsgi.py`:
```python
import sys
path = '/home/yourusername/MeshalStock'
if path not in sys.path:
    sys.path.append(path)

from api_server import app as application
```

#### 4. إعادة تحميل:
```bash
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

---

### الطريقة 3: النشر على Heroku

#### 1. إنشاء Procfile:
```
web: gunicorn api_server:app
```

#### 2. النشر:
```bash
heroku login
heroku create meshalstock-app
git push heroku main
```

#### 3. إعداد المتغيرات البيئية:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ADMIN_PASSWORD=your-password
```

---

### الطريقة 4: النشر على AWS/DigitalOcean/Linode

#### 1. إعداد Nginx كـ Reverse Proxy:

إنشاء ملف config:
```bash
sudo nano /etc/nginx/sites-available/meshalstock
```

أضف:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # حد أقصى لحجم الطلبات
    client_max_body_size 10M;
}
```

#### 2. تفعيل الموقع:
```bash
sudo ln -s /etc/nginx/sites-available/meshalstock /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 3. إعداد SSL باستخدام Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔒 إعدادات الأمان الموصى بها

### 1. تغيير كلمة المرور الافتراضية:
في ملف `.env`:
```
ADMIN_PASSWORD=your-strong-password-here
```

### 2. إعداد CORS بشكل صحيح:
```
# في التطوير:
ALLOWED_ORIGINS=*

# في الإنتاج:
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 3. تفعيل HTTPS:
- استخدم SSL certificate
- غيّر جميع الروابط إلى HTTPS

### 4. تفعيل Rate Limiting:
```
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
```

### 5. استخدام مفاتيح سرية قوية:
```python
# توليد مفتاح سري قوي:
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📊 المراقبة والصيانة

### 1. فحص اللوقات:
```bash
# لوقات الخادم
sudo journalctl -u meshalstock -f

# لوقات nginx
sudo tail -f /var/log/nginx/error.log
```

### 2. مراقبة الأداء:
- استخدم أدوات مثل `htop` أو `glances`
- راقب استخدام الذاكرة والـ CPU

### 3. النسخ الاحتياطي:
```bash
# نسخ احتياطي للبيانات
tar -czf backup-$(date +%Y%m%d).tar.gz data_sa/ data_us/ .env
```

---

## 🐛 استكشاف الأخطاء

### المشكلة: التطبيق لا يعمل
```bash
# تحقق من الحالة
sudo systemctl status meshalstock

# أعد التشغيل
sudo systemctl restart meshalstock
```

### المشكلة: خطأ في الاتصال بـ API
- تحقق من أن المنفذ 5000 مفتوح
- تحقق من إعدادات الـ firewall

### المشكلة: مشاكل في CORS
- تأكد من إعداد `ALLOWED_ORIGINS` بشكل صحيح
- تحقق من headers في المتصفح (F12 > Network)

---

## 📱 التحديثات

### تحديث التطبيق:
```bash
cd /path/to/MeshalStock
git pull origin main
pip install -r requirements.txt --upgrade
sudo systemctl restart meshalstock
```

---

## ✅ قائمة فحص قبل النشر

- [ ] تغيير جميع المفاتيح السرية في `.env`
- [ ] تغيير كلمة المرور الافتراضية
- [ ] إعداد CORS للنطاق المحدد
- [ ] تثبيت SSL certificate
- [ ] اختبار جميع الوظائف
- [ ] إعداد النسخ الاحتياطي التلقائي
- [ ] إعداد المراقبة والتنبيهات
- [ ] توثيق معلومات الوصول

---

## 🆘 الدعم

إذا واجهت أي مشاكل:
1. تحقق من اللوقات
2. راجع هذا الدليل
3. تأكد من تثبيت جميع المكتبات
4. تحقق من إعدادات البيئة

**ملاحظة:** هذا التطبيق مصمم للاستخدام الشخصي. إذا كنت تريد نشره للعامة، فكر في إضافة:
- نظام مستخدمين متعدد
- قاعدة بيانات بدلاً من CSV
- نظام أذونات أكثر تعقيداً
- مزيد من آليات الأمان
