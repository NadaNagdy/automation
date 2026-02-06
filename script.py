import gspread
import facebook
import os
import time
import re

# 1. دالة ذكية لتحويل روابط Google Drive إلى روابط مباشرة (Direct Links)
def get_drive_direct_link(url):
    if 'drive.google.com' in url:
        # استخراج الـ ID من الرابط بمختلف أشكاله
        match = re.search(r'/(?:d|file/d|open\?id=)([^/?]+)', url)
        if match:
            file_id = match.group(1)
            # استخدام صيغة الرابط المباشر التي يقبلها فيسبوك
            return f'https://drive.google.com/uc?export=download&id={file_id}'
    return url

# 2. الاتصال بجوجل شيت
try:
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open("FINAL_FULL_DATA").sheet1
except Exception as e:
    print(f"خطأ في الوصول للملف: {e}")
    exit(1)

# 3. الاتصال بفيسبوك (تأكد من استخدام Page Access Token)
graph = facebook.GraphAPI(access_token=os.getenv('FB_TOKEN'))

all_records = sh.get_all_values()
to_post = []

# 4. البحث عن 3 صفوف صالحة (العمود B نص، العمود C صورة)
for i, row in enumerate(all_records[1:], start=2):
    text_content = row[1].strip() if len(row) > 1 else ""
    image_link = row[2].strip() if len(row) > 2 else ""
    status = row[3] if len(row) > 3 else ""

    if text_content and image_link and status == "":
        to_post.append({
            "row_idx": i, 
            "message": text_content, 
            "image": image_link
        })
    
    if len(to_post) == 3:
        break

# 5. تنفيذ النشر
for item in to_post:
    try:
        print(f"جاري معالجة ونشر الصف {item['row_idx']}...")
        
        # تحويل الرابط قبل الإرسال
        final_image_url = get_drive_direct_link(item['image'])
        
        # النشر باستخدام الطريقة الأكثر استقراراً للـ Pages
        graph.put_object(
            parent_object='me', 
            connection_name='feed', 
            message=item['message'], 
            link=final_image_url
        )
        
        # تحديث العمود D بكلمة Done
        sh.update_cell(item['row_idx'], 4, "Done")
        print(f"✅ تم النشر بنجاح للصف {item['row_idx']}")
        
        time.sleep(10) # انتظار لتجنب الحظر
    except Exception as e:
        print(f"❌ خطأ في الصف {item['row_idx']}: {e}")

print("--- انتهت العملية ---")
