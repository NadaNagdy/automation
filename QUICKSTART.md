# دليل البدء السريع ⚡

## الخطوات الأساسية في 5 دقائق

### 1️⃣ احصل على Google Credentials

```
1. اذهب إلى: https://console.cloud.google.com/
2. أنشئ مشروع جديد
3. فعّل Google Sheets API
4. أنشئ Service Account → حمّل ملف JSON
5. شارك Google Sheet مع البريد من الملف
```

### 2️⃣ احصل على Facebook Token

```
1. اذهب إلى: https://developers.facebook.com/
2. أنشئ تطبيق جديد
3. Graph API Explorer → اختر صفحتك
4. أضف صلاحيات: pages_manage_posts
5. Generate Token → Extend Access Token
```

### 3️⃣ أنشئ Repository على GitHub

```bash
# أنشئ repository جديد على GitHub
# ثم نفذ:

git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# انسخ جميع الملفات إلى المجلد
# ثم:

git add .
git commit -m "Initial setup"
git push origin main
```

### 4️⃣ أضف Secrets

```
Settings → Secrets and variables → Actions → New secret

Secret 1:
Name: FB_TOKEN
Value: [الصق Facebook Token هنا]

Secret 2:
Name: GOOGLE_CREDENTIALS
Value: [الصق محتوى ملف JSON كاملاً هنا]
```

### 5️⃣ اختبر التشغيل

```
Actions → Facebook Auto Poster → Run workflow
```

---

## 🎯 متطلبات Google Sheet

تأكد من أن الشيت يحتوي على:

```
- العمود A: محتوى البوست
- العمود D: حالة النشر (فارغ أو "Done")
- اسم الشيت: FINAL_FULL_DATA
```

---

## ⚙️ التخصيص السريع

### تغيير عدد البوستات

**الإعداد الحالي: بوست واحد في كل تشغيل × 5 مرات يومياً = 5 بوستات**

إذا أردت تغيير العدد:

في `script.py` السطر 54:
```python
if len(to_post) == 1:  # غيّر الرقم هنا (مثلاً: 2 أو 3)
```

**ملاحظة:** إذا غيرت الرقم إلى 2، ستنشر 2×5 = 10 بوستات يومياً!

### تغيير التوقيت

**الإعداد الحالي: 5 مرات يومياً (7 صباحاً، 11 صباحاً، 3 عصراً، 7 مساءً، 11 مساءً بتوقيت UTC)**

في `.github/workflows/main.yml`:
```yaml
schedule:
  - cron: '0 7 * * *'   # 9 صباحاً بتوقيت القاهرة
  - cron: '0 11 * * *'  # 1 ظهراً
  - cron: '0 15 * * *'  # 5 مساءً
  - cron: '0 19 * * *'  # 9 مساءً
  - cron: '0 23 * * *'  # 1 صباحاً
```

📖 **لتفاصيل أكثر وأمثلة إضافية، راجع ملف SCHEDULE.md**

### فلترة المحتوى

في `script.py` دالة `is_valid_content`:
```python
# مثال: نشر البوستات التي تحتوي روابط فقط
if "http" not in text:
    return False
```

---

## 🚨 حل المشاكل الشائعة

| المشكلة | الحل |
|---------|------|
| "FB_TOKEN not found" | تأكد من إضافته في Secrets |
| "Spreadsheet not found" | تأكد من اسم الشيت والمشاركة |
| "Permission denied" | تحقق من صلاحيات Token |
| لا ينشر | تحقق من العمود D (يجب أن يكون فارغاً) |

---

## ✅ Checklist قبل البدء

- [ ] Google Cloud Project جاهز
- [ ] Service Account JSON محمّل
- [ ] Sheet مشارك مع Service Account
- [ ] Facebook App منشأ
- [ ] Page Access Token جاهز (Long-lived)
- [ ] GitHub Repository منشأ
- [ ] Secrets مضافة بشكل صحيح
- [ ] الملفات مرفوعة على GitHub
- [ ] تم اختبار التشغيل اليدوي

---

**🎉 مبروك! الآن لديك نظام نشر تلقائي مجاني بالكامل**
