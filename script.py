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
    match = re.search(r'(?:id=|/d/|/file/d/)([^/&?]+)', url)
    if match:
        file_id = match.group(1)
        # رابط تحميل مباشر يتخطى صفحة المعاينة
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    return url

def get_instagram_compatible_url(url):
    """Returns a Google Drive URL format that works better with Instagram API (lh3)."""
    match = re.search(r'(?:id=|/d/|/file/d/)([^/&?]+)', url)
    if match:
        file_id = match.group(1)
        # lh3 link is often friendlier to Instagram's crawler for images
        return f'https://lh3.googleusercontent.com/d/{file_id}'
    return url

# --- Instagram Helpers ---
def get_instagram_id(page_id, access_token):
    """Fetches the Instagram Business Account ID linked to the Facebook Page."""
    url = f"https://graph.facebook.com/v19.0/{page_id}?fields=instagram_business_account&access_token={access_token}"
    try:
        resp = requests.get(url).json()
        return resp.get('instagram_business_account', {}).get('id')
    except Exception as e:
        print(f"⚠️ Failed to get Instagram ID: {e}")
        return None

def post_instagram_photo(ig_id, image_url, caption, access_token):
    """Posts a photo to Instagram."""
    # Step 1: Create Container
    url_create = f"https://graph.facebook.com/v19.0/{ig_id}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': access_token
    }
    resp = requests.post(url_create, data=payload).json()
    creation_id = resp.get('id')
    
    if not creation_id:
        print(f"❌ Failed to create IG Photo Container: {resp}")
        return False
    
    # Step 1.5: Wait for readiness (sometimes required even for photos)
    # Simple sleep or check status
    time.sleep(5) 
    # Optional: Check status like reels if strictly needed, but 5s sleep usually fixes photo race conditions
        
    # Step 2: Publish
    url_publish = f"https://graph.facebook.com/v19.0/{ig_id}/media_publish"
    payload_pub = {
        'creation_id': creation_id,
        'access_token': access_token
    }
    resp_pub = requests.post(url_publish, data=payload_pub).json()
    if 'id' in resp_pub:
        print(f"✅ Posted to Instagram (Photo): {resp_pub['id']}")
        return True
    else:
         print(f"❌ Failed to publish IG Photo: {resp_pub}")
         return False

def post_instagram_reel(ig_id, video_url, caption, access_token):
    """Posts a reel to Instagram."""
    # Step 1: Create Container
    url_create = f"https://graph.facebook.com/v19.0/{ig_id}/media"
    payload = {
        'video_url': video_url,
        'media_type': 'REELS',
        'caption': caption,
        'access_token': access_token
    }
    resp = requests.post(url_create, data=payload).json()
    creation_id = resp.get('id')
    
    if not creation_id:
        print(f"❌ Failed to create IG Reel Container: {resp}")
        return False
        
    # Step 2: Wait for processing (Video takes time)
    print("⏳ Waiting for Reel processing...", end='', flush=True)
    for _ in range(10): # Try for 60 seconds
        time.sleep(6)
        print(".", end='', flush=True)
        status_url = f"https://graph.facebook.com/v19.0/{creation_id}?fields=status_code&access_token={access_token}"
        status_resp = requests.get(status_url).json()
        if status_resp.get('status_code') == 'FINISHED':
            break
        elif status_resp.get('status_code') == 'ERROR':
            print("❌ Processing Error!")
            return False
    print(" Done.")

    # Step 3: Publish
    url_publish = f"https://graph.facebook.com/v19.0/{ig_id}/media_publish"
    payload_pub = {
        'creation_id': creation_id,
        'access_token': access_token
    }
    resp_pub = requests.post(url_publish, data=payload_pub).json()
    if 'id' in resp_pub:
        print(f"✅ Posted to Instagram (Reel): {resp_pub['id']}")
        return True
    else:
         print(f"❌ Failed to publish IG Reel: {resp_pub}")
         return False


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
        # Fallback to config file
        fb_token = config.get("facebook", {}).get("access_token")
    
    
    page_id = config.get("facebook", {}).get("page_id") # Get Page ID from config
    
    if not fb_token or fb_token == "YOUR_ACCESS_TOKEN":
        raise ValueError("FB_TOKEN is missing in environment variables and config.json")
    
    # Attempt to get Page Access Token
    # If the user provided a User Token, we need to exchange it for a Page Token
    # to avoid "publish_actions deprecated" error (posting to user profile)
    # and to properly auth with Instagram.
    if page_id and page_id != "YOUR_PAGE_ID":
        try:
            # 1. Check if token works for the page directly (maybe it is a Page Token)
            # or try to find the page in user's accounts
            accounts_url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={fb_token}"
            resp = requests.get(accounts_url).json()
            
            if 'data' in resp:
                found_page = False
                for page in resp['data']:
                    if page.get('id') == page_id:
                        print(f"✅ Found Page Token for: {page.get('name')}")
                        fb_token = page.get('access_token') # Switch to Page Token
                        found_page = True
                        break
                if not found_page:
                     print("⚠️ Page ID not found in User Accounts. Taking token as is...")
        except Exception as e:
            print(f"⚠️ Failed to exchange token: {e}")

    graph = facebook.GraphAPI(access_token=fb_token)
    
    # Get IG ID early
    ig_id = None
    if page_id and page_id != "YOUR_PAGE_ID":
        ig_id = get_instagram_id(page_id, fb_token)
        if ig_id:
            print(f"📸 Linked Instagram Account ID: {ig_id}")
        else:
            print("⚠️ No linked Instagram account found or Page ID invalid.")

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

    if text_content and image_link and status.lower() != "done":
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
            # 1. Post to Facebook
            image_bytes = BytesIO(response.content)
            graph.put_photo(image=image_bytes, message=item['message'])
            print(f"✅ Posted to Facebook")
            
            # 2. Post to Instagram (if available)
            if ig_id:
                # Determine if it's a video or image based on file extension from URL or content-type?
                # The Drive direct link returns a binary stream, tricky to guess.
                # But headers might help.
                content_type = response.headers.get('Content-Type', '')
                
                # We need a PUBLIC URL for Instagram API (Drive direct link works usually)
                # Note: `get_drive_direct_link` returns a url that redirects to the binary.
                # Instagram API needs a stable URL. The `direct_url` works IF it is publicly accessible.
                # Our upload_to_drive made it public.
                
                if 'video' in content_type:
                    print("🎥 Detected Video content for Instagram...")
                    # For video, try standard direct link first (lh3 might not support video streaming same way)
                    post_instagram_reel(ig_id, direct_url, item['message'], fb_token)
                else:
                    # For images, use lh3 link to avoid redirect/mime-type issues
                    ig_url = get_instagram_compatible_url(item['image'])
                    post_instagram_photo(ig_id, ig_url, item['message'], fb_token)

            # تحديث الحالة في العمود المحدد (1-based index)
            # config["columns"]["status"] is 0-based, so add 1
            status_col_idx = config.get("columns", {}).get("status", 2) + 1
            sh.update_cell(item['row_idx'], status_col_idx, "Done")
            print(f"✅ الحالة محدثة للصف {item['row_idx']}")
        else:
            print(f"❌ فشل تحميل الصورة/الفيديو، كود الاستجابة: {response.status_code}")
            
        time.sleep(10) # انتظار لتجنب الـ Rate Limit
    except Exception as e:
        print(f"❌ خطأ في معالجة الصف {item['row_idx']}: {e}")

print("--- انتهت دورة الأتمتة بنجاح ---")

