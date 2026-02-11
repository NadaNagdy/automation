#!/usr/bin/env python3
"""
Script to add Ramadan lantern products to the website
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

def get_next_id(ws):
    """Get the next available product ID"""
    all_values = ws.get_all_values()
    ids = []
    for row in all_values[1:]:  # Skip header
        if row[0] and row[0].isdigit():
            ids.append(int(row[0]))
    return max(ids) + 1 if ids else 1

def remove_products_without_images(ws):
    """Remove products that don't have images"""
    print("\n🗑️ Removing products without images...")
    all_values = ws.get_all_values()
    
    rows_to_delete = []
    for i, row in enumerate(all_values[1:], start=2):  # Skip header, start from row 2
        if len(row) >= 5:
            image_path = row[4]  # Image Path column
            product_id = row[0]
            name = row[1]
            
            # Check if image path is empty or product has no name
            if (not image_path or image_path.strip() == '') or (not name or name.strip() == ''):
                rows_to_delete.append((i, product_id, name))
    
    if not rows_to_delete:
        print("✅ No products without images found")
        return 0
    
    # Print what will be deleted
    for row_num, pid, pname in rows_to_delete:
        print(f"  Will delete Row {row_num}: ID={pid}, Name={pname}")
    
    # Delete rows in reverse order in a single batch
    # Group consecutive rows for efficient deletion
    if rows_to_delete:
        for row_num, pid, pname in reversed(rows_to_delete):
            ws.delete_rows(row_num, row_num)
    
    deleted_count = len(rows_to_delete)
    print(f"✅ Removed {deleted_count} products without images")
    return deleted_count

def add_ramadan_lanterns(ws, next_id):
    """Add the 3 Ramadan lantern products"""
    print("\n🌙 Adding Ramadan lantern products...")
    
    # Product description from user
    description = """أشيك وارق فوانيس رمضان 💥 🌙
فانوس بوجي علي بساط 
فانوس طمطم علي بساط
فانوس الرجل العجوز علي بساط 
⬅️ فانوس بوجي علي بساط 👸 
⬅️ أغنية رمضان 🌙
⬅️ أنوار 🌈 3d
⬅️ دوران ٣٦٠ درجة 🔄
⬅️ يعمل بالبطاريات 🔋 🔋"""
    
    # Define the 3 products
    products = [
        {
            "name": "فانوس بوجي علي بساط",
            "price": "285",
            "age": "3y+",
        },
        {
            "name": "فانوس طمطم علي بساط",
            "price": "285",
            "age": "3y+",
        },
        {
            "name": "فانوس الرجل العجوز علي بساط",
            "price": "285",
            "age": "3y+",
        }
    ]
    
    # Copy the uploaded image to create 3 versions
    source_image = os.path.join(img_dir, "media__1770848249711.jpg")
    
    if not os.path.exists(source_image):
        print(f"❌ Source image not found: {source_image}")
        return 0
    
    added_count = 0
    for i, product in enumerate(products):
        product_id = next_id + i
        
        # Copy image with new ID
        new_img_name = f"{product_id}.jpg"
        new_img_path = os.path.join(img_dir, new_img_name)
        shutil.copy(source_image, new_img_path)
        print(f"  ✅ Image saved: {new_img_name}")
        
        # Prepare row
        # Headers: "ID", "Name", "Price", "Category (Age)", "Image Path", "Description", "Benefits", "Play Guide", "Status"
        row = [
            product_id,
            product["name"],
            product["price"],
            product["age"],
            f"img/{new_img_name}",
            description,
            "فانوس رمضان مميز بإضاءة 3D ودوران 360 درجة",
            "يعمل بالبطاريات، مناسب للأطفال من 3 سنوات فما فوق",
            "Active"
        ]
        
        ws.append_row(row)
        print(f"  ✅ Added: {product['name']} (ID: {product_id})")
        added_count += 1
    
    return added_count

def main():
    print("🚀 Starting Ramadan Lanterns Addition Script...")
    
    # Connect to Google Sheets
    sh = connect_to_sheets()
    if not sh:
        return
    
    try:
        ws = sh.worksheet("Website Products")
    except Exception as e:
        print(f"❌ Failed to access 'Website Products' sheet: {e}")
        return
    
    # Step 1: Remove products without images
    remove_products_without_images(ws)
    
    # Step 2: Get next available ID
    next_id = get_next_id(ws)
    print(f"\n📊 Next available ID: {next_id}")
    
    # Step 3: Add Ramadan lanterns
    added = add_ramadan_lanterns(ws, next_id)
    
    print(f"\n✅ Successfully added {added} Ramadan lantern products!")
    print("\n🔄 Now run: python3 sync_products.py to sync to website")

if __name__ == "__main__":
    main()
