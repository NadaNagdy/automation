# 🚨 حل سريع للمشكلة الحالية

## المشكلة التي واجهتها:
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

## السبب:
ملف `requirements.txt` غير موجود في الـ Repository على GitHub.

---

## ✅ الحل (خطوة بخطوة)

### الطريقة 1: رفع الملفات عبر Git (الأسرع)

#### 1. تحميل الملفات
لقد أرسلت لك جميع الملفات المطلوبة. حملها جميعاً.

#### 2. فتح Terminal/Command Prompt
انتقل إلى مجلد المشروع:
```bash
cd /path/to/facebook-auto-poster
```

#### 3. نسخ الملفات المحملة
انسخ جميع الملفات التي حملتها إلى مجلد المشروع:
- `script.py`
- `requirements.txt`
- `README.md`
- `QUICKSTART.md`
- `SCHEDULE.md`
- `TROUBLESHOOTING.md`
- `.gitignore`
- `credentials.example.json`
- مجلد `.github/` (بما فيه `workflows/main.yml`)

#### 4. رفع الملفات
```bash
# إضافة جميع الملفات
git add .

# التأكد من الملفات المضافة
git status

# حفظ التغييرات
git commit -m "Add all required project files"

# رفع على GitHub
git push origin main
```

---

### الطريقة 2: رفع عبر واجهة GitHub (الأسهل)

#### 1. اذهب إلى Repository
افتح الـ Repository على GitHub في المتصفح.

#### 2. رفع الملفات
1. اضغط على `Add file` → `Upload files`
2. اسحب **جميع** الملفات التي حملتها (ما عدا مجلد `.github`)
3. اضغط `Commit changes`

#### 3. رفع ملف Workflow
1. في الـ Repository، اضغط `Add file` → `Create new file`
2. في خانة الاسم، اكتب: `.github/workflows/main.yml`
   - سيتم إنشاء المجلدات تلقائياً
3. افتح الملف `main.yml` الذي حملته وانسخ محتواه بالكامل
4. الصقه في المحرر على GitHub
5. اضغط `Commit changes`

---

## 🔍 التحقق من نجاح الرفع

بعد رفع الملفات، تأكد من وجودها:

### في الصفحة الرئيسية للـ Repository يجب أن ترى:
```
📁 .github/
📄 .gitignore
📄 credentials.example.json
📄 QUICKSTART.md
📄 README.md
📄 requirements.txt
📄 SCHEDULE.md
📄 script.py
📄 TROUBLESHOOTING.md
```

### اضغط على `requirements.txt` للتأكد من محتواه:
يجب أن يحتوي على:
```
gspread==6.0.0
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
facebook-sdk==3.1.0
requests==2.31.0
```

---

## 🧪 اختبار التشغيل مرة أخرى

بعد رفع الملفات:

1. اذهب إلى تبويب `Actions`
2. اختر `Facebook Auto Poster`
3. اضغط `Run workflow` → `Run workflow`
4. انتظر 1-2 دقيقة
5. راقب النتيجة

### ✅ إذا نجح التشغيل:
ستظهر علامة ✓ خضراء وسيتم نشر البوست الأول!

### ❌ إذا ظهر خطأ آخر:
راجع ملف `TROUBLESHOOTING.md` للحلول الشائعة.

---

## 📋 Checklist النهائية

قبل التشغيل، تأكد من:

- [ ] رفع **جميع** الملفات على GitHub
- [ ] وجود ملف `.github/workflows/main.yml` في المكان الصحيح
- [ ] إضافة `FB_TOKEN` في GitHub Secrets
- [ ] إضافة `GOOGLE_CREDENTIALS` في GitHub Secrets
- [ ] مشاركة Google Sheet مع Service Account Email
- [ ] اسم الشيت هو `FINAL_FULL_DATA` بالضبط
- [ ] العمود D في الشيت فارغ في بعض الصفوف

---

## 💡 ملاحظة مهمة

**الملفات المخفية:**
ملف `.gitignore` يبدأ بنقطة، لذلك قد لا يظهر في بعض أنظمة التشغيل. 
- في Windows: فعّل "Show hidden files"
- في Mac/Linux: استخدم `ls -la` لرؤية الملفات المخفية

---

## 🎯 الخطوة التالية

بعد إصلاح هذه المشكلة، سيعمل النظام تلقائياً حسب الجدول:
- 5 مرات يومياً
- بوست واحد في كل مرة
- حسب الأوقات المحددة في `SCHEDULE.md`

**لا تحتاج لفعل أي شيء آخر - كل شيء سيعمل تلقائياً! 🚀**
