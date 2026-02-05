# Facebook Auto Poster - النشر التلقائي على فيسبوك

مشروع للنشر التلقائي على صفحة Facebook من Google Sheets باستخدام GitHub Actions - بديل مجاني لـ Zapier.

## 📋 المميزات

- ✅ نشر 5 بوستات يومياً موزعة على مدار اليوم
- ✅ قراءة البيانات من Google Sheets
- ✅ فلترة ذكية للمحتوى قبل النشر
- ✅ تسجيل حالة كل بوست (Done/Failed)
- ✅ مجاني 100% باستخدام GitHub Actions
- ✅ آمن - البيانات السرية محمية في GitHub Secrets

## ⏰ جدول النشر

النظام مضبوط على نشر **بوست واحد** في كل من الأوقات التالية (بتوقيت UTC):

- 07:00 UTC (09:00 صباحاً بتوقيت القاهرة)
- 11:00 UTC (01:00 ظهراً)
- 15:00 UTC (05:00 مساءً)
- 19:00 UTC (09:00 مساءً)
- 23:00 UTC (01:00 صباحاً في اليوم التالي)

📖 **لمعرفة كيفية تعديل التوقيت حسب منطقتك، راجع ملف [SCHEDULE.md](SCHEDULE.md)**

## 🚀 خطوات الإعداد

### 1. إعداد Google Sheets API

#### أ) إنشاء مشروع في Google Cloud Console

1. اذهب إلى [Google Cloud Console](https://console.cloud.google.com/)
2. أنشئ مشروع جديد (New Project)
3. فعّل Google Sheets API و Google Drive API:
   - من القائمة: `APIs & Services` → `Enable APIs and Services`
   - ابحث عن "Google Sheets API" وفعّله
   - ابحث عن "Google Drive API" وفعّله

#### ب) إنشاء Service Account

1. اذهب إلى `APIs & Services` → `Credentials`
2. اضغط `Create Credentials` → `Service Account`
3. أدخل اسم الحساب واضغط Create
4. اضغط على Service Account الذي أنشأته
5. اذهب إلى تبويب `Keys`
6. اضغط `Add Key` → `Create New Key` → `JSON`
7. سيتم تنزيل ملف JSON - احتفظ به في مكان آمن

#### ج) مشاركة Google Sheet

1. افتح ملف Google Sheet الخاص بك (FINAL_FULL_DATA)
2. اضغط على زر "Share"
3. الصق البريد الإلكتروني من ملف JSON (يبدأ بـ `...@...iam.gserviceaccount.com`)
4. اختر صلاحية "Editor"
5. اضغط Share

### 2. إعداد Facebook Access Token

#### أ) إنشاء Facebook App

1. اذهب إلى [Facebook Developers](https://developers.facebook.com/)
2. اضغط `My Apps` → `Create App`
3. اختر نوع التطبيق المناسب (Business)
4. أدخل اسم التطبيق

#### ب) الحصول على Page Access Token

1. من لوحة التطبيق، اذهب إلى `Tools` → `Graph API Explorer`
2. اختر التطبيق الخاص بك
3. اختر الصفحة التي تريد النشر عليها
4. أضف الصلاحيات التالية:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `publish_to_groups` (إذا كنت تنشر في مجموعة)
5. اضغط `Generate Access Token`
6. **مهم**: حوّل الـ Token إلى Long-lived Token:
   - اذهب إلى: `https://developers.facebook.com/tools/debug/accesstoken/`
   - الصق الـ Token
   - اضغط `Extend Access Token`
   - احتفظ بالـ Token الجديد

### 3. إعداد GitHub Repository

#### أ) إنشاء Repository

1. اذهب إلى GitHub وأنشئ repository جديد
2. سمّه مثلاً: `facebook-auto-poster`
3. اجعله Private للأمان

#### ب) رفع الملفات

1. افتح Terminal/Command Prompt
2. نفذ الأوامر التالية:

```bash
git clone https://github.com/YOUR_USERNAME/facebook-auto-poster.git
cd facebook-auto-poster

# انسخ الملفات التالية إلى المجلد:
# - script.py
# - requirements.txt
# - .github/workflows/main.yml

git add .
git commit -m "Initial commit"
git push origin main
```

#### ج) إضافة Secrets

1. اذهب إلى Repository Settings
2. من القائمة الجانبية: `Secrets and variables` → `Actions`
3. اضغط `New repository secret`
4. أضف Secret الأول:
   - Name: `FB_TOKEN`
   - Value: الصق Facebook Access Token
5. أضف Secret الثاني:
   - Name: `GOOGLE_CREDENTIALS`
   - Value: افتح ملف JSON من Google وانسخ **كامل** محتواه والصقه هنا

### 4. تجربة التشغيل

#### تشغيل يدوي (للاختبار):

1. اذهب إلى تبويب `Actions` في الـ Repository
2. اختر `Facebook Auto Poster` من القائمة
3. اضغط `Run workflow`
4. راقب النتيجة في Logs

#### التشغيل التلقائي:

- سيعمل السكريبت **تلقائياً كل ساعة**
- يمكنك تعديل التوقيت من ملف `.github/workflows/main.yml`

## ⚙️ تخصيص الإعدادات

### تغيير عدد البوستات

في ملف `script.py`، غيّر الرقم في هذا السطر:

```python
if len(to_post) == 3:  # غيّر 3 إلى العدد المطلوب
```

### تعديل معايير الفلترة

في دالة `is_valid_content` في ملف `script.py`:

```python
def is_valid_content(text):
    # مثال 1: نشر البوستات التي تحتوي على روابط فقط
    if "http" not in text:
        return False
    
    # مثال 2: استبعاد كلمات معينة
    forbidden_words = ["مسودة", "تجربة"]
    if any(word in text for word in forbidden_words):
        return False
    
    # مثال 3: التأكد من طول النص
    if len(text.strip()) < 10:
        return False
    
    return True
```

### تغيير توقيت النشر

في ملف `.github/workflows/main.yml`، الإعداد الحالي:

```yaml
schedule:
  - cron: '0 7 * * *'   # 7 صباحاً UTC (9 صباحاً بتوقيت القاهرة)
  - cron: '0 11 * * *'  # 11 صباحاً UTC (1 ظهراً)
  - cron: '0 15 * * *'  # 3 عصراً UTC (5 مساءً)
  - cron: '0 19 * * *'  # 7 مساءً UTC (9 مساءً)
  - cron: '0 23 * * *'  # 11 مساءً UTC (1 صباحاً)
```

**أمثلة لتوقيتات أخرى:**

```yaml
# 3 مرات يومياً فقط:
schedule:
  - cron: '0 9 * * *'   # 9 صباحاً
  - cron: '0 15 * * *'  # 3 عصراً
  - cron: '0 21 * * *'  # 9 مساءً

# كل ساعتين (12 مرة يومياً):
schedule:
  - cron: '0 */2 * * *'
```

📖 **راجع ملف [SCHEDULE.md](SCHEDULE.md) لمزيد من الأمثلة والشرح التفصيلي**

## 📊 هيكل Google Sheet المطلوب

| Column A (Content) | Column B | Column C | Column D (Status) |
|-------------------|----------|----------|-------------------|
| نص البوست الأول... | - | - | |
| نص البوست الثاني... | - | - | Done |
| نص البوست الثالث... | - | - | |

- **العمود A**: محتوى البوست
- **العمود D**: حالة النشر (فارغ = لم ينشر بعد، Done = تم النشر)

## 🔍 استكشاف الأخطاء

### الخطأ: "FB_TOKEN غير موجود"
- تأكد من إضافة FB_TOKEN في GitHub Secrets
- تأكد من صحة اسم الـ Secret (حساس لحالة الأحرف)

### الخطأ: "Permission denied"
- تأكد من أن الـ Access Token لديه الصلاحيات المطلوبة
- تحقق من أن الـ Token لم ينتهِ

### الخطأ: "Spreadsheet not found"
- تأكد من اسم الـ Sheet: "FINAL_FULL_DATA"
- تأكد من مشاركة الـ Sheet مع Service Account Email

### الخطأ: "Rate limit exceeded"
- زد فترة الانتظار بين البوستات في السكريبت
- قلل عدد البوستات في كل تشغيل

## 📈 إضافات متقدمة (اختيارية)

### تسجيل النتائج للتحليل في Power BI

أضف عموداً جديداً (E) للتاريخ والوقت، ثم فك التشفير عن هذا السطر في دالة `log_result`:

```python
sheet.update_cell(row_idx, 5, timestamp)
```

### إرسال إشعارات عند الفشل

يمكنك إضافة إشعارات عبر Telegram أو Email عند فشل النشر.

## 📝 ملاحظات مهمة

- ⚠️ GitHub Actions مجاني لـ 2000 دقيقة شهرياً للحسابات المجانية
- ⚠️ كل تشغيل يستغرق ~1-2 دقيقة، مع 5 تشغيلات يومياً = 5-10 دقائق يومياً
- ⚠️ الاستهلاك الشهري المتوقع: 150-300 دقيقة (أقل من الحد المجاني)
- ✅ لا داعي للقلق بشأن الحدود - الاستخدام أقل بكثير من المسموح
- ✅ لا تنشر Secrets أو Tokens في الكود أبداً

## 🆘 الدعم

إذا واجهت أي مشكلة:
1. تحقق من Logs في تبويب Actions
2. راجع قسم استكشاف الأخطاء أعلاه
3. تأكد من صحة جميع الـ Secrets

## 📄 الترخيص

هذا المشروع مفتوح المصدر ويمكنك استخدامه وتعديله بحرية.

---

**تم إنشاء هذا المشروع كبديل مجاني واحترافي لـ Zapier** 🚀
