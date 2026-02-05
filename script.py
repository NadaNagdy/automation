import gspread
import facebook
import os
import time
import re
from datetime import datetime

def is_valid_content(text):
    """
    التحقق من صحة المحتوى قبل النشر
    يمكنك تعديل هذه الدالة حسب احتياجاتك
    """
    # تجاهل المحتوى الفارغ أو القصير جداً
    if not text or len(text.strip()) < 5:
        return False
    
    # مثال: استبعاد الصفوف التي تحتوي على كلمات معينة
    # forbidden_words = ["مسودة", "تجربة", "اختبار"]
    # if any(word in text.lower() for word in forbidden_words):
    #     return False
    
    # مثال: التأكد من وجود رابط URL في المحتوى
    # url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    # if not re.search(url_pattern, text):
    #     return False
    
    return True

def log_result(sheet, row_idx, status, message=""):
    """
    تسجيل نتيجة النشر في الجدول
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # تحديث العمود D بالحالة
        sheet.update_cell(row_idx, 4, status)
        # يمكنك إضافة عمود للتاريخ والوقت (العمود E مثلاً)
        # sheet.update_cell(row_idx, 5, timestamp)
    except Exception as e:
        print(f"خطأ في تسجيل النتيجة: {e}")

def main():
    try:
        # 1. الاتصال بـ Google Sheets
        print("جاري الاتصال بـ Google Sheets...")
        
        # استخدام credentials من متغيرات البيئة
        credentials_json = os.getenv('GOOGLE_CREDENTIALS')
        if credentials_json:
            import json
            from google.oauth2.service_account import Credentials
            
            creds_dict = json.loads(credentials_json)
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            gc = gspread.authorize(credentials)
        else:
            # استخدام ملف credentials.json إذا كان موجوداً
            gc = gspread.service_account(filename='credentials.json')
        
        sh = gc.open("FINAL_FULL_DATA").sheet1
        print("✓ تم الاتصال بنجاح")
        
        # 2. الاتصال بـ Facebook
        print("جاري الاتصال بـ Facebook...")
        fb_token = os.getenv('FB_TOKEN')
        if not fb_token:
            raise ValueError("FB_TOKEN غير موجود في متغيرات البيئة")
        
        graph = facebook.GraphAPI(access_token=fb_token)
        print("✓ تم الاتصال بنجاح")
        
        # 3. جلب البيانات من الجدول
        print("جاري جلب البيانات...")
        all_records = sh.get_all_values()
        to_post = []
        
        # البحث عن 3 صفوف صالحة للنشر
        for i, row in enumerate(all_records[1:], start=2):  # تخطي صف العناوين
            if not row:  # تخطي الصفوف الفارغة
                continue
                
            content = row[0] if len(row) > 0 else ""  # المحتوى من العمود A
            status = row[3] if len(row) > 3 else ""   # الحالة من العمود D
            
            # التحقق: الحالة فارغة والمحتوى صالح
            if status == "" and is_valid_content(content):
                to_post.append({
                    "row_idx": i,
                    "content": content
                })
            
            # إيقاف البحث بعد إيجاد 3 صفوف
            if len(to_post) == 3:
                break
        
        print(f"تم إيجاد {len(to_post)} بوست للنشر")
        
        # 4. نشر البوستات
        successful_posts = 0
        for item in to_post:
            try:
                print(f"\nجاري نشر الصف رقم {item['row_idx']}...")
                print(f"المحتوى: {item['content'][:50]}...")
                
                # النشر على Facebook
                result = graph.put_object(
                    parent_object='me',
                    connection_name='feed',
                    message=item['content']
                )
                
                # تسجيل النجاح
                log_result(sh, item['row_idx'], "Done")
                successful_posts += 1
                print(f"✓ تم النشر بنجاح (Post ID: {result.get('id', 'N/A')})")
                
                # انتظار 10 ثواني بين كل بوست لتجنب Rate Limiting
                if successful_posts < len(to_post):
                    time.sleep(10)
                    
            except facebook.GraphAPIError as e:
                error_msg = f"Facebook API Error: {e}"
                print(f"✗ {error_msg}")
                log_result(sh, item['row_idx'], "Failed", error_msg)
                
            except Exception as e:
                error_msg = f"خطأ عام: {e}"
                print(f"✗ {error_msg}")
                log_result(sh, item['row_idx'], "Failed", error_msg)
        
        # 5. النتيجة النهائية
        print(f"\n{'='*50}")
        print(f"اكتملت العملية بنجاح!")
        print(f"تم نشر {successful_posts} من أصل {len(to_post)} بوستات")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"خطأ عام في البرنامج: {e}")
        raise

if __name__ == "__main__":
    main()
