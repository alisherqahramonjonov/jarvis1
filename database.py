"""
JARVIS Cloud Memory Database (MongoDB Atlas)
cloud.mongodb.com bilan to'liq integratsiya.
Barcha suhbatlar, kontaktlar xotirasi va buyruqlar tarixini bulutda saqlaydi.
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("MONGO_DB_NAME", "jarvis_db")

# Fallback in-memory xotira (agar MongoDB URI kiritilmagan bo'lsa)
_memory_store = {
    "conversations": {},
    "commands": [],
    "settings": {
        "excluded_phones": ["998979551278", "979551278"],
        "excluded_names": ["ayam", "onam", "oyim", "mama", "mami", "ona"]
    }
}

_db = None
_client = None


def get_db():
    global _db, _client
    if _db is not None:
        return _db

    if not MONGO_URI:
        return None

    try:
        from pymongo import MongoClient
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Ping tekshiruvi
        _client.admin.command('ping')
        _db = _client[DB_NAME]
        print("[MongoDB Atlas] Muvaffaqiyatli ulandi! Cloud xotira faol 🟢")
        return _db
    except Exception as e:
        print(f"[MongoDB Atlas Ogohlantirish] Ulanish imkoni bo'lmadi ({e}). In-memory xotiraga o'tildi.")
        return None


def save_message(sender_id: int, sender_name: str, role: str, text: str):
    """Suhbatdosh xabarini MongoDB Atlasga yozish"""
    db = get_db()
    msg_item = {
        "role": role,
        "text": text,
        "timestamp": time.time(),
        "time_str": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    if db is not None:
        try:
            db.conversations.update_one(
                {"sender_id": sender_id},
                {
                    "$set": {"sender_name": sender_name, "last_updated": time.time()},
                    "$push": {"messages": msg_item}
                },
                upsert=True
            )
            return
        except Exception as e:
            print(f"MongoDB save_message xatosi: {e}")

    # Fallback in-memory
    if sender_id not in _memory_store["conversations"]:
        _memory_store["conversations"][sender_id] = {
            "sender_name": sender_name,
            "messages": []
        }
    _memory_store["conversations"][sender_id]["messages"].append(msg_item)


def get_recent_history(sender_id: int, limit: int = 10) -> list:
    """Foydalanuvchining MongoDB'dagi oxirgi suhbat tarixini olish"""
    db = get_db()
    if db is not None:
        try:
            doc = db.conversations.find_one({"sender_id": sender_id})
            if doc and "messages" in doc:
                return doc["messages"][-limit:]
        except Exception as e:
            print(f"MongoDB get_recent_history xatosi: {e}")

    # Fallback in-memory
    if sender_id in _memory_store["conversations"]:
        return _memory_store["conversations"][sender_id]["messages"][-limit:]
    return []


def log_command(user_id: int, command: str, result: str):
    """Alisher tomonidan berilgan buyruqlar tarixini saqlash"""
    db = get_db()
    entry = {
        "user_id": user_id,
        "command": command,
        "result": result[:500],
        "timestamp": time.time(),
        "time_str": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if db is not None:
        try:
            db.commands.insert_one(entry)
            return
        except Exception as e:
            print(f"MongoDB log_command xatosi: {e}")

    _memory_store["commands"].append(entry)


def get_excluded_filters():
    """Ayam va boshqa himoyalangan kontaktlar ro'yxatini olish"""
    db = get_db()
    if db is not None:
        try:
            doc = db.settings.find_one({"type": "filters"})
            if doc:
                return doc.get("excluded_phones", []), doc.get("excluded_names", [])
        except Exception:
            pass
    return _memory_store["settings"]["excluded_phones"], _memory_store["settings"]["excluded_names"]


# ─── In-memory tug'ilgan sanalar (MongoDB yo'q bo'lganda) ───
_birthday_store = {}  # {sender_id: {"day": 15, "month": 10, "year": 2002}}


def save_birthday(sender_id: int, sender_name: str, day: int, month: int, year: int):
    """Suhbatdoshning tug'ilgan sanasini MongoDB yoki xotiraga saqlash"""
    db = get_db()
    entry = {
        "sender_id": sender_id,
        "sender_name": sender_name,
        "birthday": {"day": day, "month": month, "year": year},
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if db is not None:
        try:
            db.birthdays.update_one(
                {"sender_id": sender_id},
                {"$set": entry},
                upsert=True
            )
            return
        except Exception as e:
            print(f"MongoDB save_birthday xatosi: {e}")

    _birthday_store[sender_id] = {"day": day, "month": month, "year": year}


def get_birthday(sender_id: int) -> dict | None:
    """Suhbatdoshning tug'ilgan sanasini olish. None — agar mavjud bo'lmasa."""
    db = get_db()
    if db is not None:
        try:
            doc = db.birthdays.find_one({"sender_id": sender_id})
            if doc and "birthday" in doc:
                return doc["birthday"]
        except Exception as e:
            print(f"MongoDB get_birthday xatosi: {e}")

    return _birthday_store.get(sender_id)


def calculate_age(day: int, month: int, year: int) -> int:
    """Tug'ilgan sanadan hozirgi yoshni hisoblash"""
    import datetime
    today = datetime.date.today()
    age = today.year - year
    if (today.month, today.day) < (month, day):
        age -= 1
    return max(age, 0)

