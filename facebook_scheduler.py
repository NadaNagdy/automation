import schedule
import time
import os
import json
import subprocess
from datetime import datetime

# Load Config
with open('config.json', 'r') as f:
    config = json.load(f)

user_schedule = config.get("facebook", {}).get("schedule", ["09:00", "14:00", "20:00"])

def run_facebook_poster():
    print(f"⏰ Triggering Facebook Poster at {datetime.now().strftime('%H:%M:%S')}...")
    try:
        # Run script.py using the same python interpreter
        result = subprocess.run(['python3', 'script.py'], capture_output=True, text=True)
        print("--- Poster Output ---")
        print(result.stdout)
        if result.stderr:
            print("--- Poster Errors ---")
            print(result.stderr)
        print("---------------------")
    except Exception as e:
        print(f"❌ Failed to run script: {e}")

print(f"🚀 Starting Facebook Scheduler...")
print(f"📅 Scheduled times: {user_schedule}")

# Schedule jobs
for time_str in user_schedule:
    schedule.every().day.at(time_str).do(run_facebook_poster)

# Loop
while True:
    schedule.run_pending()
    time.sleep(60) # Check every minute
