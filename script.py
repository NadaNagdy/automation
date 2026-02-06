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
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # إنشاء ملف الاعتمادات مؤقتاً أو القراءة مباشرة
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open("FINAL_FULL_DATA").sheet1
except Exception as e:
    print(f"❌ خطأ في الاتصال بجوجل شيت: {e}")
    exit(1)

# 3. الاتصال بفيسبوك (facebook-sdk 3.1.0)
graph = facebook.GraphAPI(access_token=os.getenv('FB_TOKEN'))

all_records = sh.get_all_values()
to_post = []

# 4. تجميع البيانات (تخطي العناوين والبحث عن صفوف غير مكتملة)
for i, row in enumerate(all_records[1:], start=2):
    text_content = row[1].strip() if len(row) > 1 else ""
    image_link = row[2].strip() if len(row) > 2 else ""
    status = row[3].strip() if len(row) > 3 else ""

    if text_content and image_link and status == "":
        to_post.append({"row_idx": i, "message": text_content, "image": image_link})
    
    if len(to_post) == 3:
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
            
            # تحديث الحالة في العمود D
            sh.update_cell(item['row_idx'], 4, "Done")
            print(f"✅ تم النشر وتحديث الصف {item['row_idx']}")
        else:
            print(f"❌ فشل تحميل الصورة، كود الاستجابة: {response.status_code}")
            
        time.sleep(10) # انتظار لتجنب الـ Rate Limit
    except Exception as e:
        print(f"❌ خطأ في معالجة الصف {item['row_idx']}: {e}")

print("--- انتهت دورة الأتمتة بنجاح ---")
