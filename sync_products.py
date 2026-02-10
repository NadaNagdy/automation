import gspread
import json
import os
import shutil
from google.oauth2.service_account import Credentials

# Configuration
cfile = 'credentials.json'
cfg_file = 'config.json'
output_js = 'toys/products.js'
img_dir = 'toys/img'

def connect_to_sheets():
    try:
        if not os.path.exists(cfile):
            print(f"❌ {cfile} not found!")
            return None
        
        with open(cfg_file, 'r') as f:
            config = json.load(f)

        gc = gspread.service_account(filename=cfile)
        sheet_name = config.get("sheet_name", "FINAL_FULL_DATA")
        sh = gc.open(sheet_name)
        return sh
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return None

def get_next_id(records):
    ids = [int(r['ID']) for r in records if str(r['ID']).isdigit()]
    return max(ids) + 1 if ids else 1

def add_product(name, price, desc, image_source_path):
    print(f"🚀 Adding new product: {name}")
    sh = connect_to_sheets()
    if not sh: return False

    try:
        worksheet = sh.worksheet("Website Products")
        records = worksheet.get_all_records()
        
        new_id = get_next_id(records)
        
        # Move Image
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            
        new_img_name = f"{new_id}.jpg"
        new_img_path = os.path.join(img_dir, new_img_name)
        shutil.copy(image_source_path, new_img_path)
        print(f"✅ Image saved to {new_img_path}")
        
        # Prepare Row
        # Headers: "ID", "Name", "Price", "Category (Age)", "Image Path", "Description", "Benefits", "Play Guide", "Status"
        row = [
            new_id,
            name[:50], # Truncate name if too long?
            price,
            "3y+", # Default age
            f"img/{new_img_name}",
            desc,
            "منتج جديد", # Default benefits
            "استمتاع وتعلّم", # Default play guide
            "Active"
        ]
        
        worksheet.append_row(row)
        print(f"✅ Added metadata to Google Sheet with ID: {new_id}")
        
        # Sync immediately
        sync_products_logic(sh) 
        return True
        
    except Exception as e:
        print(f"❌ Failed to add product: {e}")
        return False

def sync_products_logic(sh=None):
    if not sh:
        sh = connect_to_sheets()
        if not sh: return

    try:
        worksheet = sh.worksheet("Website Products")
        records = worksheet.get_all_records()
    except gspread.exceptions.WorksheetNotFound:
        print("❌ 'Website Products' sheet not found.")
        return
    except Exception as e:
        print(f"❌ Failed to read data: {e}")
        return

    products = []
    
    for r in records:
        status = str(r.get("Status", "Active")).strip().lower()
        if status in ["inactive", "hidden", "delete", "deleted"]:
            continue
            
        try:
            p = {
                "id": r.get("ID"),
                "name": str(r.get("Name", "")),
                "price": r.get("Price", 0),
                "age": str(r.get("Category (Age)", "")),
                "img": str(r.get("Image Path", "")),
                "desc": str(r.get("Description", "")),
                "benefits": str(r.get("Benefits", "")),
                "play_guide": str(r.get("Play Guide", ""))
            }
            if not p['id'] or not p['name']: continue
            products.append(p)
        except Exception as e:
            print(f"⚠️ Skipping row due to error: {e}")

    js_content = "const products = [\n"
    for p in products:
        desc_escaped = p['desc'].replace('`', '\\`')
        js_content += "    {\n"
        js_content += f"        id: {p['id']},\n"
        js_content += f"        name: {json.dumps(p['name'], ensure_ascii=False)},\n"
        js_content += f"        price: {p['price']},\n"
        js_content += f"        age: {json.dumps(p['age'], ensure_ascii=False)},\n"
        js_content += f"        img: {json.dumps(p['img'], ensure_ascii=False)},\n"
        js_content += f"        desc: `{desc_escaped}`,\n"
        js_content += f"        benefits: {json.dumps(p['benefits'], ensure_ascii=False)},\n"
        js_content += f"        play_guide: {json.dumps(p['play_guide'], ensure_ascii=False)}\n"
        js_content += "    },\n"
    js_content += "];\n"
    
    with open(output_js, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"✅ Successfully synced {len(products)} products to {output_js}")

def sync_products():
    print("🚀 Starting Product Sync...")
    sync_products_logic()

if __name__ == "__main__":
    sync_products()
