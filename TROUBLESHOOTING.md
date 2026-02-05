# 🔧 دليل حل المشاكل الشائعة

## ❌ خطأ: Could not open requirements file

### المشكلة:
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

### السبب:
لم يتم رفع ملف `requirements.txt` إلى الـ Repository على GitHub.

### الحل:

#### الطريقة 1: رفع الملفات بشكل صحيح

تأكد من رفع **جميع** الملفات التالية إلى الـ Repository:

```bash
# 1. انتقل إلى مجلد المشروع
cd facebook-auto-poster

# 2. تأكد من وجود الملفات
ls -la

# يجب أن ترى:
# - script.py
# - requirements.txt
# - .github/workflows/main.yml
# - README.md
# - .gitignore

# 3. أضف جميع الملفات
git add script.py
git add requirements.txt
git add .github/workflows/main.yml
git add README.md
git add .gitignore
git add QUICKSTART.md
git add SCHEDULE.md
git add credentials.example.json

# 4. احفظ التغييرات
git commit -m "Add all project files"

# 5. ارفع على GitHub
git push origin main
```

#### الطريقة 2: رفع عبر واجهة GitHub

1. اذهب إلى الـ Repository على GitHub
2. اضغط `Add file` → `Upload files`
3. اسحب جميع الملفات التي حملتها
4. اضغط `Commit changes`

---

## ✅ Checklist قبل التشغيل

تأكد من وجود هذه الملفات في الـ Repository:

- [ ] `script.py` ✓
- [ ] `requirements.txt` ✓
- [ ] `.github/workflows/main.yml` ✓
- [ ] `README.md` ✓
- [ ] `.gitignore` ✓

---

## 🔍 كيفية التحقق من الملفات

### عبر GitHub:
1. اذهب إلى الـ Repository
2. يجب أن ترى جميع الملفات في الصفحة الرئيسية
3. اضغط على `requirements.txt` للتأكد من محتواه

### عبر Terminal:
```bash
# عرض الملفات في المجلد الحالي
ls -la

# عرض محتوى requirements.txt
cat requirements.txt
```

---

## ❌ خطأ: FB_TOKEN not found

### المشكلة:
```
ValueError: FB_TOKEN غير موجود في متغيرات البيئة
```

### الحل:
1. اذهب إلى `Settings` → `Secrets and variables` → `Actions`
2. تأكد من وجود Secret باسم `FB_TOKEN` **بالضبط** (حساس لحالة الأحرف)
3. تأكد من أن القيمة هي Facebook Access Token الصحيح

---

## ❌ خطأ: Spreadsheet not found

### المشكلة:
```
gspread.exceptions.SpreadsheetNotFound: FINAL_FULL_DATA
```

### الأسباب المحتملة:

1. **اسم الشيت غير صحيح**
   - الحل: تأكد من أن اسم Google Sheet بالضبط: `FINAL_FULL_DATA`

2. **لم تتم مشاركة الشيت مع Service Account**
   - الحل: افتح ملف `credentials.json` واستخرج البريد الإلكتروني
   - شارك الشيت مع هذا البريد (ينتهي بـ `.iam.gserviceaccount.com`)

3. **Service Account ليس لديه صلاحيات**
   - الحل: عند المشاركة، اختر `Editor` وليس `Viewer`

---

## ❌ خطأ: Invalid credentials

### المشكلة:
```
google.auth.exceptions.DefaultCredentialsError
```

### الحل:
1. تأكد من إضافة `GOOGLE_CREDENTIALS` في GitHub Secrets
2. تأكد من نسخ **كامل** محتوى ملف JSON (من `{` إلى `}`)
3. لا تضف مسافات أو أسطر إضافية

---

## ❌ خطأ: GraphAPIError

### المشكلة:
```
facebook.GraphAPIError: (#200) The user hasn't authorized the application to perform this action
```

### الحل:
1. تأكد من أن الـ Token لديه صلاحيات:
   - `pages_manage_posts`
   - `pages_read_engagement`
2. جدد الـ Token من Graph API Explorer
3. استخدم Long-lived Token وليس Short-lived

---

## 🐛 كيفية قراءة Logs

1. اذهب إلى تبويب `Actions` في الـ Repository
2. اضغط على آخر Workflow Run
3. اضغط على `post-to-facebook`
4. اضغط على `Run Facebook Posting Script`
5. اقرأ الأخطاء بالتفصيل

---

## 💡 نصائح إضافية

### اختبر محلياً أولاً (اختياري)

قبل الرفع على GitHub، يمكنك اختبار السكريبت على جهازك:

```bash
# 1. ثبت المكتبات
pip install -r requirements.txt

# 2. أضف ملف credentials.json في نفس المجلد

# 3. أضف متغير البيئة
export FB_TOKEN="your_facebook_token_here"
export GOOGLE_CREDENTIALS=$(cat credentials.json)

# 4. شغل السكريبت
python script.py
```

### راقب استهلاك GitHub Actions

- اذهب إلى `Settings` → `Billing and plans`
- راقب عدد الدقائق المستخدمة
- الحد المجاني: 2000 دقيقة/شهر

---

## 📞 الحصول على المساعدة

إذا استمرت المشكلة:

1. ✅ تأكد من اتباع جميع الخطوات في `README.md`
2. ✅ راجع `QUICKSTART.md` للتأكد من الإعداد الأساسي
3. ✅ انسخ **رسالة الخطأ كاملة** من Logs
4. ✅ تحقق من أن جميع الملفات موجودة في Repository

---

## 🔄 إعادة التشغيل بعد الإصلاح

بعد إصلاح المشكلة:

1. انتظر الوقت المحدد في الجدول التلقائي، أو
2. اذهب إلى `Actions` → `Facebook Auto Poster` → `Run workflow` للتشغيل اليدوي

---

✅ **معظم المشاكل تحل برفع الملفات بشكل صحيح وإعداد Secrets بدقة!**
