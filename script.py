import gspread
import facebook
import os
import time

# الاتصال بجوجل شيت
gc = gspread.service_account(filename='credentials.json')
sh = gc.open("FINAL_FULL_DATA").sheet1

# الاتصال بفيسبوك
graph = facebook.GraphAPI(access_token=os.getenv('FB_TOKEN'))

all_records = sh.get_all_values()
to_post = []

# البحث عن 3 صفوف صالحة للنشر
for i, row in enumerate(all_records[1:], start=2):
    # التأكد من وجود نص في العمود B (Index 1) وصورة في العمود C (Index 2)
    text_content = row[1].strip() if len(row) > 1 else ""
    image_url = row[2].strip() if len(row) > 2 else ""
    status = row[3] if len(row) > 3 else "" # العمود D للحالة

    # الشرط: (نص موجود) و (رابط صورة موجود) و (لم ينشر بعد)
    if text_content and image_url and status == "":
        to_post.append({
            "row_idx": i, 
            "message": text_content, 
            "image": image_url
        })
    
    if len(to_post) == 3:
        break

# تنفيذ النشر
for item in to_post:
    try:
        print(f"جاري نشر الصف {item['row_idx']}...")
        # نشر الصورة مع النص
        graph.put_photo(image=item['image'], message=item['message'])
        
        # تحديث الحالة إلى Done في العمود D
        sh.update_cell(item['row_idx'], 4, "Done")
        
        time.sleep(10) # أمان لتجنب الـ Spam
    except Exception as e:
        print(f"فشل في نشر الصف {item['row_idx']}: {e}")

print("تمت المهمة بنجاح.")
