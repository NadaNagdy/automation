import gspread
import facebook
import os
import time
import re
import requests
import pyautogui
import subprocess
# Fail-safe ensuring you can always exit automation by moving mouse to corner
pyautogui.FAILSAFE = True
from io import BytesIO
import pywhatkit
import shutil
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
    try:
        resp = requests.post(url_create, data=payload, timeout=30).json()
    except Exception as e:
        print(f"⚠️ IG Photo Connection Error (Retrying): {e}")
        time.sleep(5)
        try:
            resp = requests.post(url_create, data=payload, timeout=30).json()
        except Exception as e2:
            print(f"❌ IG Photo Failed twice: {e2}")
            return False
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



def post_to_whatsapp_channel(channel_name, channel_link, message, image_path):
    """
    Posts message and image to a WhatsApp Channel using GUI automation.
    Tries opening the channel link first, then falls back to search.
    """
    import webbrowser
    import pyperclip
    import time
    
    print(f"🚀 Posting to WhatsApp Channel: {channel_name}")
    
    # 1. Try opening the Channel Link directly
    # This might open the "View Channel" page which requires a click to "Open in Web"
    # or it might redirect to the channel in the app.
    # Let's try opening it.
    if channel_link:
        print(f"🔗 Opening Channel Link: {channel_link}")
        webbrowser.open(channel_link)
        time.sleep(15) # Wait for page load and potential redirect
        
        # If the link opened the "View Channel" landing page, we might need to click "View in WhatsApp Web"
        # But this is tricky to detect. 
        # Often, if you are logged in, it might just offer to open.
        
        # Let's assume it *might* have worked, but if not, we use the Search Fallback.
        # We can detect if we are in the channel by checking screen? No.
        # We will blindly try to Search as a fallback if the link didn't focus the chat.
        
    # 2. Fallback / Ensure Focus: Search for Channel
    # Even if link opened it, searching for it again is safe and ensures focus.
    
    # Ensure we are on WhatsApp Web tab (Link opening might have opened a new tab)
    # If we opened a new tab, great.
    
    try:
        print("🔍 Ensuring Channel Focus via Search...")
        # Mac: Cmd + Ctrl + / ? Or just '/' if enabled.
        # Web shortcut: Cmd + Alt + / 
        
        pyautogui.hotkey('command', 'option', '/') 
        time.sleep(1)
        
        # 3. Type Channel Name
        pyperclip.copy(channel_name)
        pyautogui.hotkey('command', 'v')
        
        time.sleep(3) # Wait for search results
        
        # 4. Select the Channel
        # Assume it's the first result. Press Down -> Enter
        pyautogui.press('down')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3) # Wait for channel to open
        
        # 5. Send Image (Copy to Clipboard) and Message
        if image_path:
            if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
                 print("⚠️ Image file is missing or empty. Skipping image.")
            else:
                try:
                    # Clear Clipboard first to avoid stale images
                    pyperclip.copy("") 
                    
                    print(f"📸 Copying image to clipboard: {image_path}")
                    # Use AppleScript to copy image to clipboard
                    abs_path = os.path.abspath(image_path)
                    cmd = f'set the clipboard to (read (POSIX file "{abs_path}") as JPEG picture)'
                    subprocess.run(['osascript', '-e', cmd], check=True)
                    
                    time.sleep(1)
                    
                    # Verify clipboard content type? (Hard in python without heavyweight libs)
                    # We trust osascript.
                    
                    # Paste Image
                    pyautogui.hotkey('command', 'v')
                    time.sleep(3) # Wait for image preview to load
                    
                    # Type Caption
                    pyperclip.copy(message)
                    pyautogui.hotkey('command', 'v')
                    time.sleep(1)
                    
                    # Send
                    pyautogui.press('enter')
                    print("✅ Posted to WhatsApp Channel (Image + Text)")
                    
                except Exception as e:
                    print(f"⚠️ Failed to copy/paste image: {e}. Falling back to text.")
                    # Fallback to Text Only
                    pyperclip.copy(message)
                    pyautogui.hotkey('command', 'v')
                    time.sleep(1)
                    pyautogui.press('enter')
        else:
            # Text Only
            pyperclip.copy(message)
            pyautogui.hotkey('command', 'v')
            time.sleep(1)
            pyautogui.press('enter')
            print("✅ Posted to WhatsApp Channel (Text Only)")
             
    except Exception as e:
        print(f"❌ Failed to post to channel: {e}")

# --- Website Helpers ---
def update_website(text, price, image_path):
    """Updates the toys/index.html file with the new product."""
    index_path = 'toys/index.html'
    img_dir = 'toys/img'
    
    # 1. Determine new ID
    if not os.path.exists(index_path):
        print(f"❌ Index file not found at {index_path}")
        return

    with open(index_path, 'r') as f:
        content = f.read()
    
    # Find all IDs to get the max
    ids = [int(m) for m in re.findall(r'id:\s*(\d+)', content)]
    new_id = max(ids) + 1 if ids else 1
    
    # 2. Move and Rename Image
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    new_img_name = f"{new_id}.jpg"
    new_img_path = os.path.join(img_dir, new_img_name)
    try:
        shutil.copy(image_path, new_img_path) 
        print(f"✅ Image saved to {new_img_path}")
    except Exception as e:
        print(f"❌ Failed to save image: {e}")
        return
    
    # 3. Create Product Object
    # Simple extraction of name (first line) and description
    lines = text.split('\n')
    name = lines[0][:50].replace('"', "'").strip() # First line, max 50 chars, escape quotes
    desc = text.replace('"', "'").replace('\n', '\\n').replace('`', "'") # Escape backticks too
    
    # Clean price
    try:
        # Simple heuristic if price is passed as number or string
        price_val = float(str(price).replace(',', '').replace('EGP', '').replace('LE', '').replace(' ', ''))
    except:
        price_val = 0
        
    new_product_js = f"""
            {{
                id: {new_id}, name: "{name}", price: {price_val}, age: "3y+", img: "img/{new_img_name}", desc: `{desc}`, benefits: "منتج جديد", play_guide: "استمتاع وتعلّم"
            }},"""
            
    # 4. Insert into index.html
    insert_pos = content.find('const products = [')
    if insert_pos > -1:
         # Find the opening bracket
         start_bracket = insert_pos + len('const products = [')
         # Insert right after the opening bracket
         new_content = content[:start_bracket] + new_product_js + content[start_bracket:]
         with open(index_path, 'w') as f:
             f.write(new_content)
         print(f"✅ Added to Website: {name} (ID: {new_id})")
    else:
         print("❌ Could not find products array in index.html")


# 2. إعداد الاتصال بجوجل شيت (gspread 6.0.0)
try:
    # Load configuration
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)

    # WhatsApp Config
    wa_target = config.get("whatsapp", {}).get("admin_phone", "")
    wa_channel = config.get("whatsapp", {}).get("channel_name", "") 
    wa_channel_link = config.get("whatsapp", {}).get("channel_link", "")
    
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
COL_WA_CONTENT = config.get("columns", {}).get("whatsapp_content", 4)
BATCH_SIZE = config.get("batch_size", 3)

for i, row in enumerate(all_records[1:], start=2):
    # Ensure row has enough columns
    if len(row) <= max(COL_CONTENT, COL_IMAGE, COL_STATUS):
        continue

    text_content = row[COL_CONTENT].strip()
    image_link = row[COL_IMAGE].strip()
    status = row[COL_STATUS].strip()
    
    # Get WA Content if available, else fallback to text_content
    wa_content = text_content
    if len(row) > COL_WA_CONTENT:
        wa_content = row[COL_WA_CONTENT].strip() or text_content

    if text_content and image_link and status.lower() != "done":
        to_post.append({"row_idx": i, "message": text_content, "wa_message": wa_content, "image": image_link})
    
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
            # Save Image Locally for Website/WhatsApp
            local_image_path = f"temp_image_{item['row_idx']}.jpg"
            with open(local_image_path, 'wb') as f:
                f.write(response.content)
            
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

            # 3. Update Website
            # Extract price from message (simple regex or just pass 0 if not found)
            # Assuming the message contains the price or we just parse it
            try:
                # Try to find a number in the message
                price_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)', item['message'])
                price_val = price_match.group(1) if price_match else 0
                update_website(item['message'], price_val, local_image_path)
            except Exception as e:
                print(f"❌ Failed to update website: {e}")

            # 4. Post to WhatsApp (Admin)
            if wa_target:
                print(f"📱 Sending to WhatsApp Admin: {wa_target}")
                try:
                    wa_msg = f"{item['wa_message']}\n\n{item['image']}"
                    pywhatkit.sendwhatmsg_instantly(wa_target, wa_msg, wait_time=15, tab_close=False) # Keep tab open for next step
                    print("✅ Sent to WhatsApp Admin")
                    time.sleep(5) 
                except Exception as e:
                    print(f"❌ Failed to send to WhatsApp Admin: {e}")

            # 5. Post to WhatsApp Channel
            if wa_channel:
                 try:
                     post_to_whatsapp_channel(wa_channel, wa_channel_link, item['wa_message'], local_image_path)
                 except Exception as e:
                     print(f"❌ Failed to channel post: {e}")

            # Clean up local file
            if os.path.exists(local_image_path):
                os.remove(local_image_path)

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

