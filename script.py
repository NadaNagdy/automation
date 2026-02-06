import gspread
import facebook
import os
import time

# 1. الاتصال بجوجل شيت (تأكد أن الملف يتم إنشاؤه عبر الـ Action)
try:
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open("FINAL_FULL_DATA").sheet1
except Exception as e:
    print(f"خطأ في الاتصال بجوجل شيت: {e}")
    exit(1)

# 2. الاتصال بفيسبوك باستخدام التوكن من البيئة
graph = facebook.GraphAPI(access_token=os.getenv('FB_TOKEN'))

all_records = sh.get_all_values()
to_post = []

# 3. البحث عن 3 صفوف صالحة للنشر (تجاهل الفارغ)
for i, row in enumerate(all_records[1:], start=2):
    # العمود B نص (Index 1) والعمود C صورة (Index 2)
    text_content = row[1].strip() if len(row) > 1 else ""
    image_url = row[2].strip() if len(row) > 2 else ""
    status = row[3] if len(row) > 3 else "" # العمود D للحالة

    # الشرط: نص وصورة موجودين والعمود D فارغ
    if text_content and image_url and status == "":
        to_post.append({
            "row_idx": i, 
            "message": text_content, 
            "image": image_url
        })
    
    if len(to_post) == 3:
        break

# 4. تنفيذ النشر باستخدام الطريقة الحديثة
for item in to_post:
    try:
        print(f"جاري نشر الصف {item['row_idx']}...")
        
        # التعديل: استخدام Feed مع ربط الصورة كـ Link لضمان القبول
        graph.put_object(
            parent_object='me', 
            connection_name='feed', 
            message=item['message'], 
            link=item['image']
        )
        
        # تحديث الحالة إلى Done في العمود D
        sh.update_cell(item['row_idx'], 4, "Done")
        print(f"✅ تم نشر الصف {item['row_idx']} بنجاح.")
        
        time.sleep(10) # أمان لتجنب الـ Spam
    except Exception as e:
        print(f"❌ فشل في نشر الصف {item['row_idx']}: {e}")

print("--- تمت المهمة بنجاح ---")
