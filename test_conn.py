import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def main():
    client = TelegramClient("jarvis_user", API_ID, API_HASH, connection_retries=10, timeout=20)
    await client.connect()
    is_auth = await client.is_user_authorized()
    print("IS_AUTH:", is_auth)
    if is_auth:
        me = await client.get_me()
        print(f"CONNECTED_AS: {me.first_name} (@{me.username}) ID: {me.id}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
