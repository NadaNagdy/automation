import gspread
import facebook
import os
import time
import re
import requests
from io import BytesIO

# 1. دالة استخراج الـ ID وتحويله لرابط تحميل مباشر (Direct Download)
def get_drive_direct_link(url):
    match = re.search(r'(?:id=|/d/|/file/d/)([^/&?]+)', url)
    if match:
        file_id = match.group(1)
        # رابط تحميل مباشر للخام (Raw Data)
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    return url

# 2. الاتصال بجوجل شيت
try:
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open("FINAL_FULL_DATA").sheet1
except Exception as e:
    print(f"❌ خطأ شيت: {e}")
    exit(1)

# 3. الاتصال بفيسبوك
graph = facebook.GraphAPI(access_token=os.getenv('FB_TOKEN'))

all_records = sh.get_all_values()
to_post = []

# 4. تجميع 3 صفوف (B: نص، C: رابط درايف)
for i, row in enumerate(all_records[1:], start=2):
    text_content = row[1].strip() if len(row) > 1 else ""
    image_link = row[2].strip() if len(row) > 2 else ""
    status = row[3].strip() if len(row) > 3 else ""

    if text_content and image_link and status == "":
        to_post.append({"row_idx": i, "message": text_content, "image": image_link})
    
    if len(to_post) == 3: break

# 5. النشر عبر تحميل الصورة ثم رفعها
for item in to_post:
    try:
        print(f"جاري معالجة الصف {item['row_idx']}...")
        direct_url = get_drive_direct_link(item['image'])
        
        # تحميل الصورة في الذاكرة (Memory) لتجاوز مشاكل الروابط
        image_response = requests.get(direct_url)
        if image_response.status_code == 200:
            image_data = BytesIO(image_response.content)
            
            # رفع الصورة كملف فعلي
            graph.put_photo(image=image_data, message=item['message'])
            
            sh.update_cell(item['row_idx'], 4, "Done")
            print(f"✅ تم النشر بنجاح للصف {item['row_idx']}")
        else:
            print(f"❌ فشل تحميل الصورة من درايف: {image_response.status_code}")
            
        time.sleep(10)
    except Exception as e:
        print(f"❌ فشل في الصف {item['row_idx']}: {e}")

print("--- انتهى التشغيل ---")
