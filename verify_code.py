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
HASH = "97380ce35fc94685ce"

async def login_with_code(code):
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    try:
        print(f"Kodni tekshirish: {code} ...")
        user = await client.sign_in(phone=PHONE, code=code, phone_code_hash=HASH)
        print(f"SUCCESS: {user.first_name} (@{user.username}) ID: {user.id}")
    except SessionPasswordNeededError:
        print("2FA parol kiritilmoqda...")
        user = await client.sign_in(password=PASSWORD)
        print(f"SUCCESS_2FA: {user.first_name} (@{user.username}) ID: {user.id}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__} - {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    code = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    if code:
        asyncio.run(login_with_code(code))
    else:
        print("Kod berilmadi!")
