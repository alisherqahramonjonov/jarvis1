import asyncio
import os
import sys
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "34966695"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "e3f9fec1fc95991d807608a3a1bca711")
PHONE = os.getenv("TELEGRAM_PHONE", "+998773230998")
PASSWORD = os.getenv("TELEGRAM_PASSWORD", "011209270518")
SESSION_NAME = "jarvis_user"

CODE = "34554"

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"SUCCESS_ALREADY_AUTH: {me.first_name} (@{me.username}) ID: {me.id}")
        await client.disconnect()
        return

    # Try signing in with the code
    try:
        # Check if code works directly
        user = await client.sign_in(PHONE, code=CODE)
        print(f"SUCCESS_SIGNED_IN: {user.first_name} (@{user.username})")
    except SessionPasswordNeededError:
        print("2FA password needed, submitting password...")
        user = await client.sign_in(password=PASSWORD)
        print(f"SUCCESS_2FA_SIGNED_IN: {user.first_name} (@{user.username})")
    except Exception as e:
        print(f"ERROR: {type(e).__name__} - {e}")
        # If hash is missing, send code request again
        print("Sending fresh code request...")
        sent = await client.send_code_request(PHONE)
        print(f"NEW_CODE_SENT, phone_code_hash: {sent.phone_code_hash}")
    
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"FINAL_OK: {me.first_name} (@{me.username}) ID: {me.id}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
