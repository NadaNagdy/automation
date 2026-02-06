import gspread
import facebook
import os
import time
import re

# 1. دالة تحويل روابط Google Drive إلى روابط مباشرة "خامية"
def get_drive_direct_link(url):
    # استخراج الـ ID من أي شكل لرابط جوجل درايف (d/id أو id=id)
    match = re.search(r'(?:id=|/d/|/file/d/)([^/&?]+)', url)
    if match:
        file_id = match.group(1)
        # هذه الصيغة هي الأفضل لتجاوز حماية جوجل والسماح لفيسبوك بسحب الصورة
        return f'https://drive.google.com/uc?export=view&id={file_id}'
    return url

# 2. الاتصال بجوجل شيت (باستخدام ملف الاعتمادات الذي ينشئه الأكشن)
try:
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open("FINAL_FULL_DATA").sheet1
except Exception as e:
    print(f"❌ خطأ في الوصول لجوجل شيت: {e}")
    exit(1)

# 3. الاتصال بفيسبوك (تأكد من تحديث FB_TOKEN في GitHub Secrets)
graph = facebook.GraphAPI(access_token=os.getenv('FB_TOKEN'))

# جلب كافة البيانات
all_records = sh.get_all_values()
to_post = []

# 4. البحث عن 3 صفوف (B: نص، C: صورة، D: الحالة)
# نبدأ من الصف الثاني (i=2) لتخطي العناوين
for i, row in enumerate(all_records[1:], start=2):
    text_content = row[1].strip() if len(row) > 1 else ""
    image_link = row[2].strip() if len(row) > 2 else ""
    status = row[3].strip() if len(row) > 3 else ""

    # شرط النشر: وجود نص وصورة وأن الحالة فارغة تماماً
    if text_content and image_link and status == "":
        to_post.append({
            "row_idx": i, 
            "message": text_content, 
            "image": image_link
        })
    
    # التوقف عند تجميع 3 بوستات
    if len(to_post) == 3:
        break

# 5. دورة النشر (Execution)
if not to_post:
    print("نظيفة: لا توجد صفوف جديدة للنشر حالياً.")
else:
    for item in to_post:
        try:
            print(f"جاري معالجة الصف {item['row_idx']}...")
            
            # تحويل الرابط للصيغة المباشرة
            direct_url = get_drive_direct_link(item['image'])
            
            # رفع الصورة كـ Media على صفحة فيسبوك
            graph.put_photo(
                image=direct_url,
                message=item['message']
            )
            
            # تحديث العمود D بكلمة Done فور النجاح
            sh.update_cell(item['row_idx'], 4, "Done")
            print(f"✅ تم نشر الصف {item['row_idx']} بنجاح على فيسبوك.")
            
            # انتظار 10 ثوانٍ بين كل بوست والآخر للأمان
            time.sleep(10)
        except Exception as e:
            print(f"❌ فشل في نشر الصف {item['row_idx']}: {e}")

print("--- تم الانتهاء من دورة التشغيل ---")
