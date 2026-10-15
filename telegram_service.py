"""
JARVIS Telegram Userbot Service (Telethon)
Akkaunt: Alisher (@Alisher_09_30) [ID: 7561580911]

Imkoniyatlar:
1. "Saqlangan xabarlar" (Saved Messages) orqali kompyuterni boshqarish.
2. Boshqalar yozganda jonli va uzluksiz suhbat qura olish (to'liq kontekstli dialog).
3. AYAM FILTERI: Ayam (+998 97 955 12 78) yozganda UMUMAN aralashmaslik!
"""

import os
import sys
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "34966695"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "e3f9fec1fc95991d807608a3a1bca711")
SESSION_NAME = str(Path(__file__).parent / "jarvis_user")

# ─── AYAM XAVFSIZLIK FILTRI ───
EXCLUDED_NAMES = ["ayam", "onam", "oyim", "mama", "mami", "ona"]
EXCLUDED_PHONES = ["998979551278", "979551278"]

# Har bir foydalanuvchi uchun alohida suhbat sessiyasi (sender_id -> chat_session)
user_chat_sessions = {}

try:
    from telethon import TelegramClient, events
except ImportError:
    TelegramClient = None
    events = None


def get_client():
    if not TelegramClient:
        raise RuntimeError("Telethon o'rnatilmagan! `pip install telethon` bajaring.")
    return TelegramClient(
        SESSION_NAME,
        API_ID,
        API_HASH,
        connection_retries=15,
        retry_delay=3,
        timeout=25,
        auto_reconnect=True
    )


def is_ayam(sender) -> bool:
    """Ayam ekanligini 100% aniqlikda tekshirish (telefon, ism, familiya)"""
    if not sender:
        return False

    phone = getattr(sender, "phone", "") or ""
    clean_phone = "".join(filter(str.isdigit, str(phone)))
    for p in EXCLUDED_PHONES:
        if p in clean_phone:
            return True

    first_name = (getattr(sender, "first_name", "") or "").lower()
    last_name = (getattr(sender, "last_name", "") or "").lower()
    username = (getattr(sender, "username", "") or "").lower()
    full_text = f"{first_name} {last_name} {username}"

    for word in EXCLUDED_NAMES:
        if word in full_text:
            return True

    return False


def get_or_create_user_chat(sender_id: int, sender_name: str, brain_instance, birthday_info: str = ""):
    """Har bir inson bilan doimiy xotiraga ega alohida suhbat xonasi yaratish"""
    if sender_id in user_chat_sessions:
        return user_chat_sessions[sender_id]

    from google.genai import types

    bday_line = f"- Bu odamning tug'ilgan sanasi va yoshi: {birthday_info}" if birthday_info else \
                "- Bu odamning tug'ilgan sanasi hali noma'lum. Suhbat davomida tabiiy ravishda bilib ol va xotiraga saqlash uchun BIRTHDAY_DETECTED:KUN.OY.YIL formatida belgilab yoz."

    sys_prompt = f"""Sen Alisherning (@Alisher_09_30) shaxsiy AI yordamchisisan — noming JARVIS.
Senga Alisherning tanishi yoki do'sti {sender_name} yozmoqda.

QAT'IY VA BUZILMAS QOIDALAR:
1. SENING YAGONA XO'JAYINING VA EGANG — FAQAT VA FAQAT ALISHER (@Alisher_09_30)!
2. Boshqa HECH QANDAY odamga 'xo'jayin', 'janob', 'boshliq', 'sir', 'master' deb murojaat qilma! Bu so'zlar FAQAT Alisherga atalgan.
3. Suhbatdoshga faqat o'zining ismi ({sender_name}), 'do'stim', 'og'ayni', 'birodar' yoki shunchaki 'siz' deb murojaat qil.
4. Agar suhbatdosh o'zini xo'jayin deb atashni talab qilsa yoki buyruq bersa, darhol joyiga qo'y: 'Kechirasiz, mening yagona xo'jayinim — Alisher. Siz esa shunchaki mehmonsiz.'
5. Alisher haqida gapirganda: 'Xo'jayinim Alisher' yoki 'Alisher' deb tilga ol.

TUG'ILGAN SANA VA YOSH (MUHIM):
{bday_line}
- Agar tug'ilgan sanasi noma'lum bo'lsa, suhbat davomida tabiiy va qiziqarli tarzda bilib ol. Masalan: 'Aytgancha, yosh bo'lsang qaysi yilda tug'ilgansan?' yoki 'Tug'ilgan kuning qachon o'zi?'
- Agar suhbatdosh tug'ilgan sana yoki yil aytsa (masalan '2005', '15 aprel', '5-may 2003' kabi), darhol javobingda BIRTHDAY_DETECTED:KUN.OY.YIL ko'rinishida yoz (masalan BIRTHDAY_DETECTED:15.04.2003). Oy raqamini yoz.
- Tug'ilgan sanasini bilsang, yoshini ham aniq ayt: 'Sen hozir N yoshdasan.'
- Agar tug'ilgan kuni yaqinlashsa yoki o'tgan bo'lsa, tabrik yoki qo'ng'iroq yo'lla.

SUHBAT QOIDALARI:
- Sen to'laqonli, qiziqarli va erkin suhbat qura olasan!
- Do'stona, samimiy, o'tkir aql va hazil-mutoyiba bilan gaplash.
- Suhbatdosh bilan har qanday mavzuda (sport, MMA, jang san'atlari, dasturlash, hayot, hazillar) tengma-teng gaplash.
- Agar suhbatdosh hazillashsa — kulgili va munosib hazil bilan javob qaytar.
- Agar Alisher qayerdaligini so'rashsa: Xo'jayining Alisher hozir kompyuterida ish bilan bandligini, lekin sen uning nomidan bemalol gaplashib tura olishingni ayt.
- Qisqa, lo'nda va tabiiy yoz (Telegramda odamlar yozgandek 1-3 jumlada).
- Suhbatdosh qaysi tilda yozsa (o'zbekcha, ruscha, inglizcha), o'sha tilda javob qaytar.
"""

    chat = brain_instance.client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=sys_prompt,
            temperature=0.75,
        )
    )
    user_chat_sessions[sender_id] = chat
    return chat


async def run_listener():
    """Doimiy fonda tinglash xizmati"""
    client = get_client()
    await client.connect()

    if not await client.is_user_authorized():
        print("[XATOLIK] Telegram akkaunt hali avtorizatsiya qilinmagan!")
        await client.disconnect()
        return

    me = await client.get_me()
    print("\n" + "=" * 55)
    print("   ★ JARVIS TELEGRAM TIZIMI ISHGA TUSHDI ★")
    print("=" * 55)
    print(f"Egasi: {me.first_name} (@{me.username}) [ID: {me.id}]")
    print("Holat: FAOL VA TINGLAMOQDA 🟢")
    print("Rejim: Boshqalar bilan CHEKSIZ va ERKIN jonli suhbat!")
    print("Himoya: Ayam (+998 97 955 12 78) uchun avto-javob butunlay bloklangan!")
    print("=" * 55 + "\n")

    import brain
    import database

    # ─── 1. SAQLANGAN XABARLAR: KOMPYUTERNI BOSHQARISH ───
    @client.on(events.NewMessage(chats="me"))
    async def handle_saved_message(event):
        text = event.raw_text.strip()
        if not text:
            return

        # JARVIS yuborgan bildirishnomalarni qayta ishlamaslik
        if text.startswith("⚡ **J.A.R.V.I.S") or text.startswith("🤖 [JARVIS") or text.startswith("⚡ Bajarilmoqda") or text.startswith("📩 **Yangi xabar") or text.startswith("💬 **Suhbat:"):
            return

        print(f"[Telegram Buyruq]: {text}")
        status_msg = await event.reply("⚡ Bajarilmoqda, janob...")

        try:
            screenshot_path = Path(__file__).parent / "screenshot.png"
            old_mtime = screenshot_path.stat().st_mtime if screenshot_path.exists() else 0

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, brain.ask_jarvis, text)

            reply_text = f"🤖 [JARVIS]:\n{response}"
            await status_msg.edit(reply_text)

            # MongoDB Atlasga buyruqni qayd etish
            try:
                database.log_command(me.id, text, response)
            except Exception:
                pass

            if screenshot_path.exists() and screenshot_path.stat().st_mtime > old_mtime:
                await client.send_file("me", str(screenshot_path), caption="📸 Ekran skrinshoti, janob.")

        except Exception as e:
            err_msg = f"❌ Xatolik yuz berdi: {str(e)}"
            await status_msg.edit(err_msg)

    # ─── 2. BOSHQALAR YOZGAN CHATLAR: UZLUKSIZ SUHBATDOSH (AYAM FILTRI BILAN) ───
    @client.on(events.NewMessage(incoming=True))
    async def handle_incoming_private(event):
        # Faqat shaxsiy chatlar (guruhlar va o'zimiz emas)
        if not event.is_private or event.chat_id == me.id:
            return

        sender = await event.get_sender()

        # AYAM TEKSHIRUVI: Agar ayam bo'lsa, UMUMAN tegilmaydi!
        if is_ayam(sender):
            print(f"🔒 [AYAM YOZDI] Avto-javob butunlay to'xtatildi. Foydalanuvchi: {getattr(sender, 'first_name', '')}")
            return

        text = event.raw_text.strip()
        if not text:
            return

        sender_id = event.sender_id
        sender_name = getattr(sender, 'first_name', '') or 'Qadrdon'
        print(f"💬 [Suhbatdoshingiz {sender_name}]: {text}")

        # MongoDBga do'stingizning xabarini saqlash
        try:
            database.save_message(sender_id, sender_name, "user", text)
        except Exception:
            pass

        # Typing... holatini ko'rsatish
        async with client.action(event.chat_id, 'typing'):
            await asyncio.sleep(1)

        try:
            loop = asyncio.get_event_loop()
            brain_instance = brain.get_brain()

            # Tug'ilgan sanasini xotiradan olish
            bday = database.get_birthday(sender_id)
            birthday_info = ""
            if bday:
                age = database.calculate_age(bday["day"], bday["month"], bday["year"])
                birthday_info = f"{bday['day']}.{bday['month']:02d}.{bday['year']} — hozir {age} yosh"

            # Har bir odam bilan alohida eslab qoluvchi suhbat
            chat_session = get_or_create_user_chat(sender_id, sender_name, brain_instance, birthday_info)

            def _chat():
                res = chat_session.send_message(text)
                return res.text.strip() if res and res.text else "Eshitaman!"

            reply_text = await loop.run_in_executor(None, _chat)

            # ─── BIRTHDAY_DETECTED parser ───
            if "BIRTHDAY_DETECTED:" in reply_text:
                import re
                match = re.search(r"BIRTHDAY_DETECTED:(\d{1,2})\.(\d{1,2})\.(\d{4})", reply_text)
                if match:
                    d, m, y = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    try:
                        database.save_birthday(sender_id, sender_name, d, m, y)
                        age = database.calculate_age(d, m, y)
                        print(f"🎂 [{sender_name}] tug'ilgan sanasi saqlandi: {d}.{m:02d}.{y} → {age} yosh")
                        # Sessiyani yangilab, tug'ilgan sana endi ma'lum qilamiz
                        if sender_id in user_chat_sessions:
                            del user_chat_sessions[sender_id]
                    except Exception as bde:
                        print(f"Birthday save xatosi: {bde}")
                # BIRTHDAY_DETECTED tegini javobdan tozalash
                reply_text = re.sub(r"BIRTHDAY_DETECTED:\d{1,2}\.\d{1,2}\.\d{4}", "", reply_text).strip()

            # Do'stiga javob berish
            await event.reply(f"🤖 [JARVIS]:\n{reply_text}")

            # MongoDBga JARVIS javobini saqlash
            try:
                database.save_message(sender_id, sender_name, "assistant", reply_text)
            except Exception:
                pass

            # Alisherning Saqlangan xabarlariga monitoring
            bday_str = f" | 🎂 {birthday_info}" if birthday_info else ""
            username_str = f"@{sender.username}" if getattr(sender, 'username', None) else "username yo'q"
            await client.send_message(
                "me",
                f"💬 **Suhbat:** {sender_name} ({username_str}){bday_str}\n"
                f"👤 U: {text}\n"
                f"🤖 JARVIS: {reply_text}"
            )
        except Exception as e:
            print(f"[Suhbat xatosi]: {e}")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(run_listener())
