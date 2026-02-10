import json
import asyncio
import os
import re
from datetime import datetime
from telethon import TelegramClient
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gspread
import shutil


# --- Configuration ---
with open('config.json', 'r') as f:
    config = json.load(f)

# Telegram Config
api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
channel_link = "https://t.me/+WBPaEzSH1tpWtNxI"
session_name = 'anon'

# Google Config
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# --- Google Drive & Sheets Setup ---
def get_google_services():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    
    gc = gspread.authorize(creds)
    sheet = gc.open(config.get("sheet_name", "FINAL_FULL_DATA")).sheet1
    
    return drive_service, sheet

def upload_to_drive(drive_service, file_path, folder_id=None):
    """Uploads a file to Google Drive and returns the webViewLink."""
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]
        
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink, webContentLink').execute()
    
    # Make file public (or accessible to anyone with link) so Facebook/Website can read it
    permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    drive_service.permissions().create(fileId=file.get('id'), body=permission).execute()
    
    return file.get('webContentLink') # Direct download link is better for scripts

def multiply_prices(text, factor=2.0):
    """Multiplies any price found in the text by the given factor."""
    if not text:
        return text

    # Added Arabic keywords for price: سعر, سعره, سعرها, السعر
    currencies = r"(?:EGP|LE|USD|\$|£|€|SAR|AED|سعر|سعره|سعرها|السعر)"
    
    # Helper to calculate new price
    def calculate_new_price(val_str):
        try:
            val = float(val_str.replace(',', ''))
            new_val = val * factor
            return "{:,.0f}".format(new_val) if new_val.is_integer() else "{:,.2f}".format(new_val)
        except ValueError:
            return val_str

    # 1. Prefix Currency: $100, EGP 100
    def replace_prefix(match):
        currency = match.group(1)
        number = match.group(2)
        return f"{currency} {calculate_new_price(number)}"

    pattern_prefix = re.compile(f"({currencies})\s*(\d+(?:,\d{{3}})*(?:\.\d+)?)", re.IGNORECASE)
    text = pattern_prefix.sub(replace_prefix, text)
    
    # 2. Suffix Currency: 100 EGP, 100LE
    def replace_suffix(match):
        number = match.group(1)
        currency = match.group(2)
        return f"{calculate_new_price(number)} {currency}"

    pattern_suffix = re.compile(f"(\d+(?:,\d{{3}})*(?:\.\d+)?)\s*({currencies})", re.IGNORECASE)
    text = pattern_suffix.sub(replace_suffix, text)
    
    return text

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


# --- Telegram Scraper ---
client = TelegramClient(session_name, api_id, api_hash)

async def main():
    print("🚀 Starting Scraper...")
    drive_service, sheet = get_google_services()
    
    # 1. Get Channel Entity
    # Since we joined, we can find it by Invite Link hash or Dialogue
    invite_hash = channel_link.split('+')[1]
    
    try:
        # Method 1: Try getting entity directly by Link (works if already joined)
        try:
            target_chat = await client.get_entity(channel_link)
            print(f"✅ Found Channel by Link: {target_chat.title} (ID: {target_chat.id})")
        except:
            # Method 2: Iterate dialogs if link lookup fails (sometimes happens with private links)
            print("⚠️ Cloud not resolve link directly, searching dialogs...")
            target_chat = None
            async for dialog in client.iter_dialogs():
                # We can't easily match private invite links to names without checking, 
                # but since we just joined it, it should be the top one or we can print them.
                # For now, let's print the top 5 dialogs and try to guess or ask user?
                # actually, `ImportChatInviteRequest` returns `Updates`.
                pass
            
            # Re-running ImportChatInviteRequest is safe and returns the Chat info
            from telethon.tl.functions.messages import ImportChatInviteRequest
            invite_hash = channel_link.split('+')[1]
            try:
                updates = await client(ImportChatInviteRequest(invite_hash))
                if updates.chats:
                    target_chat = updates.chats[0]
                    print(f"✅ Resolved Channel via Import: {target_chat.title} (ID: {target_chat.id})")
            except Exception as e:
                 # If "User already participant", we still need to find WHICH chat it is.
                 # The error doesn't give us the Chat ID.
                 # Strategy: We assume the user joined it recently.
                 print(f"⚠️  Could not re-import: {e}")
                 print("🔍 Listing top 10 dialogs to find potential match...")
                 async for dialog in client.iter_dialogs(limit=10):
                     print(f" - {dialog.name} (ID: {dialog.id})")
                     # Heuristic: If we can't find it, we might need the user to tell us the EXACT title 
                     # or we just grab the first channel that looks like a product channel?
                     # Let's hope Method 1 worked.
        
        if not target_chat:
            print("❌ Could not resolve channel entity. If you see the channel name above, please update the script with the ID.")
            return

        # 2. Fetch Last N Messages
        # We only want messages with Photos and Text
        print("📥 Fetching recent messages...")
        messages = await client.get_messages(target_chat, limit=5)
        
        for msg in reversed(messages):
            if (msg.photo or msg.video) and msg.text:
                is_video = bool(msg.video)
                media_type = "Video" if is_video else "Photo"
                # 2.5 Validation: Check for Price and Description
                # A valid product must have a price (currency symbol) and description text.
                
                # Check 1: Description Length
                if len(msg.text) < 20:
                    print(f"⚠️ Skipping: Text too short ({len(msg.text)} chars)")
                    continue

                # Check 2: Price Existence
                currencies = r"(?:EGP|LE|USD|\$|£|€|SAR|AED|سعر|سعره|سعرها|السعر)"
                has_price = re.search(f"({currencies})\s*:?\s*(\d+)|(\d+)\s*({currencies})", msg.text, re.IGNORECASE)
                
                if not has_price:
                    print(f"⚠️ Skipping: No valid price found in text.")
                    continue
                
                # Check 3: Video Constraints (Instagram Reels < 15min, < 1GB)
                # Telethon gives us size/duration. Let's be safe and skip huge files.
                if is_video:
                     if msg.file.size > 100 * 1024 * 1024: # 100MB limit for safety
                         print(f"⚠️ Skipping: Video too large ({msg.file.size / 1024 / 1024:.2f} MB)")
                         continue
                
                print(f"------------\nFound valid {media_type}:\n{msg.text[:50]}...")
                
                # 3. Download Media
                path = await msg.download_media(file='downloads/')
                print(f"📸 Downloaded to: {path}")
                
                # 4. Upload to Drive
                drive_folder_id = config.get('drive_folder_id')
                drive_link = "Upload Failed"
                try:
                    if drive_service:
                        print(f"☁️ Uploading to Google Drive (Folder ID: {drive_folder_id})...")
                        drive_link = upload_to_drive(drive_service, path, folder_id=drive_folder_id)
                        print(f"🔗 Drive Link: {drive_link}")
                except Exception as e:
                    print(f"⚠️ Drive Upload Failed: {e}")
                    # Continue without breaking
                
                # 5. Add to Sheet
                # Columns: [Date, Content (FB/Web 2x), ImageLink, Status, Content (WA 1.5x)]
                content_fb_web = multiply_prices(msg.text, factor=2.0)
                content_wa = multiply_prices(msg.text, factor=1.5)
                
                # Extract 2x price for website object
                price_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)', content_fb_web)
                price_2x_val = price_match.group(1) if price_match else "0"

                row_data = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Col 0 (Date)
                    content_fb_web,                               # Col 1 (Content FB/Web)
                    drive_link,                                   # Col 2 (Image)
                    "New",                                        # Col 3 (Status)
                    content_wa                                    # Col 4 (Content WA)
                ]
                
                try:
                    sheet.append_row(row_data)
                    print("✅ Added to Google Sheet")
                except Exception as e:
                    print(f"⚠️ Sheet Append Failed: {e}")
                
                # 6. Update Website (Only if it's an image, or we need to handle video tag?)
                # Current index.html structure expects 'img' property. 
                # If we have a video, we might want to extract a thumbnail or just use a placeholder?
                # For now, let's only update the website if it's an image.
                if not is_video:
                    print("🌐 Updating Website...")
                    update_website(content_fb_web, price_2x_val, path)
                else:
                     print("🌐 Skipping Website Update (Video content not yet supported on site)")
                
                # Cleanup local file (moved cleanup after website update which uses the file)
                if os.path.exists(path):
                    os.remove(path)
                
    except Exception as e:
        print(f"❌ Error: {e}")

with client:
    client.loop.run_until_complete(main())
