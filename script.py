import gspread
import facebook
import os
import time
import re
import requests
from io import BytesIO
from google.oauth2.service_account import Credentials

# 1. تحويل روابط جوجل درايف لصيغة التحميل المباشر
def get_drive_direct_link(url):
    match = re.search(r'(?:id=|/d/|/file/d/)([^/&?]+)', url)
    if match:
        file_id = match.group(1)
        # رابط تحميل مباشر يتخطى صفحة المعاينة
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    return url

# 2. إعداد الاتصال بجوجل شيت (gspread 6.0.0)
try:
    # Load configuration
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)

    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    if not os.path.exists('credentials.json'):
        raise FileNotFoundError("ملف credentials.json غير موجود. يرجى اتباع التعليمات في README.md لإنشائه.")

    # إنشاء ملف الاعتمادات مؤقتاً أو القراءة مباشرة
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open(config.get("sheet_name", "FINAL_FULL_DATA")).sheet1
except Exception as e:
    print(f"❌ خطأ في الإعداد: {e}")
    exit(1)

# 3. الاتصال بفيسبوك (facebook-sdk 3.1.0)
try:
    fb_token = os.getenv('FB_TOKEN')
    if not fb_token:
         raise ValueError("FB_TOKEN environment variable is not set.")
    graph = facebook.GraphAPI(access_token=fb_token)
except Exception as e:
    print(f"❌ خطأ في الاتصال بفيسبوك: {e}")
    exit(1)

all_records = sh.get_all_values()
to_post = []

# 4. تجميع البيانات (تخطي العناوين والبحث عن صفوف غير مكتملة)
# Configured columns
COL_CONTENT = config.get("columns", {}).get("content", 0)
COL_IMAGE = config.get("columns", {}).get("image", 1)
COL_STATUS = config.get("columns", {}).get("status", 2)
BATCH_SIZE = config.get("batch_size", 3)

for i, row in enumerate(all_records[1:], start=2):
    # Ensure row has enough columns
    if len(row) <= max(COL_CONTENT, COL_IMAGE, COL_STATUS):
        continue

    text_content = row[COL_CONTENT].strip()
    image_link = row[COL_IMAGE].strip()
    status = row[COL_STATUS].strip()

    if text_content and image_link and status == "":
        to_post.append({"row_idx": i, "message": text_content, "image": image_link})
    
    if len(to_post) == BATCH_SIZE:
        break

# 5. دورة النشر (تحميل الصورة ثم رفعها كـ Bytes)
for item in to_post:
    try:
        print(f"جاري معالجة الصف {item['row_idx']}...")
        direct_url = get_drive_direct_link(item['image'])
        
        # تحميل الصورة برمجياً (requests 2.31.0)
        response = requests.get(direct_url, timeout=30)
        if response.status_code == 200:
            image_bytes = BytesIO(response.content)
            
            # رفع الصورة لفيسبوك كملف ميديا
            graph.put_photo(image=image_bytes, message=item['message'])
            
            # تحديث الحالة في العمود المحدد (1-based index)
            # config["columns"]["status"] is 0-based, so add 1
            status_col_idx = config.get("columns", {}).get("status", 2) + 1
            sh.update_cell(item['row_idx'], status_col_idx, "Done")
            print(f"✅ تم النشر وتحديث الصف {item['row_idx']}")
        else:
            print(f"❌ فشل تحميل الصورة، كود الاستجابة: {response.status_code}")
            
        time.sleep(10) # انتظار لتجنب الـ Rate Limit
    except Exception as e:
        print(f"❌ خطأ في معالجة الصف {item['row_idx']}: {e}")

print("--- انتهت دورة الأتمتة بنجاح ---")
