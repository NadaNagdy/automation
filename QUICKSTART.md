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

في `script.py` السطر 54:
```python
if len(to_post) == 3:  # غيّر الرقم هنا
```

### تغيير التوقيت

في `.github/workflows/main.yml` السطر 6:
```yaml
- cron: '0 * * * *'  # كل ساعة
# - cron: '0 */3 * * *'  # كل 3 ساعات
# - cron: '0 9,15,21 * * *'  # 3 مرات يومياً
```

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
