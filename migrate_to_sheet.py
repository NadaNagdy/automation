import re
import json
import gspread
import os
from google.oauth2.service_account import Credentials

# 1. Setup Google Sheets Connection
def connect_to_sheets():
    try:
        if not os.path.exists('credentials.json'):
            print("❌ credentials.json not found!")
            return None
        
        with open('config.json', 'r') as f:
            config = json.load(f)

        gc = gspread.service_account(filename='credentials.json')
        # Open configuration to get sheet name or use default
        sheet_name = config.get("sheet_name", "FINAL_FULL_DATA")
        sh = gc.open(sheet_name)
        return sh
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return None

# 2. Extract Products from HTML
def extract_products_from_html():
    file_path = 'toys/index.html'
    if not os.path.exists(file_path):
        print("❌ toys/index.html not found.")
        return []

    with open(file_path, 'r') as f:
        content = f.read()

    # Regex to find the products array content
    # Look for const products = [ ... ];
    match = re.search(r'const products = \[\s*([\s\S]*?)(\]\s*;)', content)
    
    if not match:
        print("❌ Could not find products array in HTML.")
        return []
    
    products_str = match.group(1)
    
    # regex to parse individual product objects
    # This is a bit tricky because they are JS objects not valid JSON (keys no quotes, backticks for strings)
    # We will try a dirty parser or just evaluate it if we trust it? No eval is unsafe.
    # Let's use regex to split by }, { 
    
    # Better regex to split by objects
    # We look for { at the start of a line or after a comma, and } at the end
    # This is still fragile but better than splitting by "}, {"
    
    # Let's use a pattern that matches { ... } pairs
    # Note: This assumes no nested braces inside the object (which is true for this file)
    product_blocks = re.findall(r'\{[^{}]+\}', products_str)
    
    parsed_products = []
    
    for block in product_blocks:
        p = {}
        
        # ID
        id_match = re.search(r'id:\s*(\d+)', block)
        if id_match: p['id'] = id_match.group(1)
        
        # Name (Double quotes)
        name_match = re.search(r'name:\s*"([^"]+)"', block)
        if name_match: p['name'] = name_match.group(1)
        
        # Price (Number)
        price_match = re.search(r'price:\s*([\d\.]+)', block)
        if price_match: p['price'] = price_match.group(1)
        
        # Age
        age_match = re.search(r'age:\s*"([^"]+)"', block)
        if age_match: p['age'] = age_match.group(1)
        
        # Img
        img_match = re.search(r'img:\s*"([^"]+)"', block)
        if img_match: p['img'] = img_match.group(1)
        
        # Desc (Backticks - multiline)
        desc_match = re.search(r'desc:\s*`([\s\S]+?)`', block)
        if desc_match: p['desc'] = desc_match.group(1).strip()
        
        # Benefits
        ben_match = re.search(r'benefits:\s*"([^"]+)"', block)
        if ben_match: p['benefits'] = ben_match.group(1)
        
        # Play Guide
        play_match = re.search(r'play_guide:\s*"([^"]+)"', block)
        if play_match: p['play_guide'] = play_match.group(1)
        
        if p.get('id'):
            parsed_products.append(p)
            
    return parsed_products

# 3. Upload to Sheets
def migrate_data(sh, products):
    try:
        # Check if "Website Products" worksheet exists, if not create it
        try:
            worksheet = sh.worksheet("Website Products")
            print("ℹ️ 'Website Products' sheet exists. Appending...", end="\n")
            # Optional: Clear it? No, safe append.
        except gspread.exceptions.WorksheetNotFound:
            print("ℹ️ Creating 'Website Products' sheet...")
            worksheet = sh.add_worksheet(title="Website Products", rows=1000, cols=10)
            
            # Add Headers
            headers = ["ID", "Name", "Price", "Category (Age)", "Category (Field)", "Image Path", "Description", "Benefits", "Play Guide", "Status"]
            worksheet.append_row(headers)
            
            # Format headers
            worksheet.format('A1:J1', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})

        # Prepare rows
        rows = []
        existing_ids = set()
        
        # Check existing data to avoid duplicates
        existing_records = worksheet.get_all_records()
        for r in existing_records:
            existing_ids.add(str(r.get('ID')))

        count = 0
        for p in products:
            if str(p.get('id')) in existing_ids:
                continue
                
            row = [
                p.get('id'),
                p.get('name', ''),
                p.get('price', 0),
                p.get('age', ''),
                p.get('category', 'science'),  # Default STEM category
                p.get('img', ''),
                p.get('desc', ''),
                p.get('benefits', ''),
                p.get('play_guide', ''),
                "Active"
            ]
            rows.append(row)
            count += 1
            
        if rows:
            worksheet.append_rows(rows)
            print(f"✅ Migrated {count} products to Google Sheet!")
        else:
            print("✅ No new products to migrate.")
            
    except Exception as e:
        print(f"❌ Migration Failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Migration...")
    sh = connect_to_sheets()
    if sh:
        prods = extract_products_from_html()
        print(f"📦 Found {len(prods)} products in HTML.")
        if prods:
            migrate_data(sh, prods)
