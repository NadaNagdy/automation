import pywhatkit
import gspread
import json
import time
from datetime import datetime

# Load Config
with open('config.json', 'r') as f:
    config = json.load(f)

# Google Sheets Setup
gc = gspread.service_account(filename='credentials.json')
sheet = gc.open(config.get("sheet_name", "FINAL_FULL_DATA")).sheet1

def main():
    print("🚀 Starting WhatsApp Sync...")
    
    # Get all records
    rows = sheet.get_all_values()
    
    # Headers are usually row 1, so data starts at row 2 (index 1)
    # But let's check headers
    headers = rows[0] if rows else []
    
    # Iterate through rows
    # We will look for Status = "New" (Column 3, index 3)
    # But wait, config says status index is 3 (so 4th column, 0-indexed is 3)
    # Let's use the config status index
    status_idx = config.get("status_column_index", 3)
    wa_content_idx = config.get("columns", {}).get("whatsapp_content", 4)
    image_idx = config.get("columns", {}).get("image", 2)
    
    # pywhatkit needs a phone number or Group ID
    # Using the admin_phone from config as default
    target = config.get("whatsapp", {}).get("admin_phone", "")
    
    if not target:
        target = input("Enter Target Phone (with country code +20...) or Group ID: ")
    else:
        print(f"📱 sending to configured target: {target}")
    
    for i, row in enumerate(rows):
        if i == 0: continue # Skip header
        
        if len(row) > status_idx and row[status_idx] == "New":
            print(f"Processing Row {i+1}...")
            
            content = row[wa_content_idx] if len(row) > wa_content_idx else ""
            img_link = row[image_idx] if len(row) > image_idx else ""
            
            # Since pywhatkit sends messages via browser, it cannot easily attach an image from a URL 
            # without downloading it first.
            # But the scraper already downloaded it... and deleted it.
            # So we might need to rely on the text content or re-download.
            
            # Actually, `sendwhats_image` takes a local path.
            # `sendwhatmsg` takes text.
            
            # Strategy: Just send the text (Content 1.5x) + Link to Image?
            # Or re-download the image?
            # Let's send text first as it is simpler.
            
            message = f"{content}\n\n{img_link}"
            
            try:
                # Send message instantly (wait time 15s to load, 5s to close tab? pywhatkit defaults are high)
                # This opens a browser tab.
                pywhatkit.sendwhatmsg_instantly(target, message, wait_time=20, tab_close=True)
                print("✅ Message sent!")
                
                # Update Status
                sheet.update_cell(i+1, status_idx+1, "Posted")
                print("✅ Status updated to Posted")
                
                time.sleep(5) # Wait a bit before next
                
            except Exception as e:
                print(f"❌ Failed to send: {e}")

if __name__ == "__main__":
    main()
