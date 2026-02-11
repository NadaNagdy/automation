#!/usr/bin/env python3
"""
Quick script to add Ramadan lantern products
"""
import gspread
import json
import os
import shutil

# Configuration
cfile = 'credentials.json'
cfg_file = 'config.json'
img_dir = 'toys/img'

def connect_to_sheets():
    with open(cfg_file, 'r') as f:
        config = json.load(f)
    gc = gspread.service_account(filename=cfile)
    sh = gc.open(config.get("sheet_name", "FINAL_FULL_DATA"))
    return sh

def get_next_id(ws):
    """Get the next available product ID"""
    all_values = ws.get_all_values()
    ids = []
    for row in all_values[1:]:  # Skip header
        if row[0] and row[0].isdigit():
            ids.append(int(row[0]))
    return max(ids) + 1 if ids else 1

def main():
    print("🚀 Adding Ramadan Lanterns...")
    
    sh = connect_to_sheets()
    ws = sh.worksheet("Website Products")
    
    # Get next ID
    next_id = get_next_id(ws)
    print(f"📊 Next available ID: {next_id}")
    
    # Product description
    description = """أشيك وارق فوانيس رمضان 💥 🌙
⬅️ فانوس بوجي علي بساط 👸 
⬅️ أغنية رمضان 🌙
⬅️ أنوار 🌈 3d
⬅️ دوران ٣٦٠ درجة 🔄
⬅️ يعمل بالبطاريات 🔋 🔋"""
    
    # Define products
    products = [
        {"name": "فانوس بوجي علي بساط", "price": "285"},
        {"name": "فانوس طمطم علي بساط", "price": "285"},
        {"name": "فانوس الرجل العجوز علي بساط", "price": "285"}
    ]
    
    # Source image
    source_image = os.path.join(img_dir, "media__1770848249711.jpg")
    
    # Add each product
    for i, product in enumerate(products):
        product_id = next_id + i
        
        # Copy image
        new_img_name = f"{product_id}.jpg"
        new_img_path = os.path.join(img_dir, new_img_name)
        shutil.copy(source_image, new_img_path)
        
        # Prepare row
        # Headers: "ID", "Name", "Price", "Category (Age)", "Image Path", "Description", "Benefits", "Play Guide", "Status"
        row = [
            product_id,
            product["name"],
            product["price"],
            "3y+",  # Age category
            f"img/{new_img_name}",
            description,
            "فانوس رمضان مميز بإضاءة 3D ودوران 360 درجة",
            "يعمل بالبطاريات، مناسب للأطفال من 3 سنوات فما فوق",
            "Active"
        ]
        
        ws.append_row(row)
        print(f"✅ Added: {product['name']} (ID: {product_id})")
    
    print(f"\n✅ Successfully added {len(products)} Ramadan lanterns!")
    print("🔄 Now syncing to website...")
    
    # Sync to website
    os.system("python3 sync_products.py")

if __name__ == "__main__":
    main()
