import json
import asyncio
from telethon import TelegramClient

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
# The session file will be saved as 'anon.session'
client = TelegramClient('anon', api_id, api_hash)

async def main():
    print("Initiating connection...")
    await client.start()
    
    # Print self entry to verify
    me = await client.get_me()
    print(f"✅ Successfully logged in as: {me.first_name} (ID: {me.id})")
    
    # Check channel access
    invite_link = "https://t.me/+WBPaEzSH1tpWtNxI"
    invite_hash = invite_link.split('+')[1]
    
    try:
        from telethon.tl.functions.messages import ImportChatInviteRequest
        print(f"Checking access to {invite_link}...")
        updates = await client(ImportChatInviteRequest(invite_hash))
        print("✅ Joined/Verified channel access.")
    except Exception as e:
        print(f"⚠️  Channel access info: {e}")

    print("--- Login Setup Complete ---")

with client:
    client.loop.run_until_complete(main())
