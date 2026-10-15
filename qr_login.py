import asyncio
import os
import sys
import webbrowser
import urllib.parse
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
PASSWORD = os.getenv("TELEGRAM_PASSWORD", "011209270518")
SESSION_NAME = "jarvis_user"

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"\n[OK] Akkaunt allaqachon ulangan: {me.first_name} (@{me.username}) [ID: {me.id}]")
        await client.disconnect()
        return

    print("\n" + "=" * 50)
    print("   JARVIS TELEGRAM QR-LOGIN ISHGA TUSHDI")
    print("=" * 50)

    qr_path = os.path.abspath("telegram_qr.html")
    first_open = False

    while True:
        try:
            qr = await client.qr_login()
            encoded_url = urllib.parse.quote(qr.url)
            qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={encoded_url}"
            
            html_content = f"""<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="utf-8">
    <title>JARVIS Telegram QR Login</title>
    <style>
        body {{
            background: #020b14;
            color: #00e5ff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }}
        .card {{
            background: rgba(4, 20, 36, 0.95);
            border: 2px solid #00e5ff;
            box-shadow: 0 0 35px rgba(0, 229, 255, 0.45);
            padding: 30px 40px;
            border-radius: 12px;
            text-align: center;
            max-width: 420px;
        }}
        h2 {{ margin: 0 0 10px 0; letter-spacing: 3px; color: #00e5ff; text-shadow: 0 0 10px #00e5ff; }}
        .sub {{ font-size: 13px; color: #78909c; margin-bottom: 20px; }}
        .qr-box {{
            background: #fff;
            padding: 12px;
            border-radius: 8px;
            display: inline-block;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
        }}
        img {{ display: block; }}
        ol {{
            text-align: left;
            color: #e0f7fa;
            font-size: 13px;
            line-height: 1.8;
            margin: 20px 0 10px 0;
            padding-left: 20px;
        }}
        li b {{ color: #00e5ff; }}
        .note {{ font-size: 13px; color: #00e676; margin-top: 15px; font-weight: bold; }}
    </style>
    <script>
        // Har 45 soniyada QR kodni yangilab turish
        setTimeout(() => location.reload(), 45000);
    </script>
</head>
<body>
    <div class="card">
        <h2>⚡ J.A.R.V.I.S TELEGRAM</h2>
        <div class="sub">SMS VA KODLARSIZ TEZKOR ULASH</div>
        <div class="qr-box">
            <img src="{qr_img_url}" alt="Telegram QR Code" width="280" height="280" />
        </div>
        <ol>
            <li>Telefoningizda <b>Telegram</b>'ni oching</li>
            <li><b>Sozlamalar (Настройки)</b> bo'limiga kiring</li>
            <li><b>Qurilmalar (Устройства)</b> bandini tanlang</li>
            <li><b>Qurilmani ulash (Подключить устройство)</b> tugmasini bosing va ushbu QR kodni skanerlang!</li>
        </ol>
        <div class="note">✓ Skanerlashingiz bilan JARVIS avtomatik ulanadi!</div>
    </div>
</body>
</html>
"""
            with open(qr_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            if not first_open:
                webbrowser.open(f"file:///{qr_path}")
                first_open = True
                print("Brauzerda QR kod ochildi. Skanerlash kutilmoqda...")

            # Wait for scan
            user = await qr.wait(timeout=45)
            print(f"\n[OK] QR skanerlandi! Foydalanuvchi: {user.first_name} (@{user.username})")
            break

        except TimeoutError:
            # QR token expired, loop will generate a fresh one
            print("QR kod yangilandi, yangi kod kutilmoqda...")
            continue
        except SessionPasswordNeededError:
            print("\n2FA parol so'ralmoqda, avtomatik kiritilmoqda...")
            user = await client.sign_in(password=PASSWORD)
            print(f"\n[OK] 2FA orqali muvaffaqiyatli ulandi: {user.first_name} (@{user.username})")
            break
        except Exception as e:
            print("Xatolik:", type(e).__name__, e)
            await asyncio.sleep(3)

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"\n★ JARVIS TELEGRAM AKKAUNTGA BIRIKTIRILDI! ★")
        print(f"Foydalanuvchi: {me.first_name} (@{me.username}) ID: {me.id}")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
