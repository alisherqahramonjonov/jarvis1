"""
JARVIS — Miya (Brain)
Google Gemini API bilan ishlash va Tool Calling orqali buyruqlarni bajarish.
"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import MODEL, SYSTEM_PROMPT, DANGEROUS_KEYWORDS
from logger import log
import tools

# .env fayldan API kalitni yuklash
load_dotenv()


def _is_dangerous(command: str) -> bool:
    """Buyruqda xavfli kalit so'zlar borligini tekshirish."""
    cmd = command.lower()
    return any(kw in cmd for kw in DANGEROUS_KEYWORDS)


def safe_run_command(command: str) -> str:
    """Terminal buyrug'ini xavfsizlik tekshiruvi bilan bajarish."""
    if _is_dangerous(command):
        # Fon rejimi yoki Telegram orqali kelganda input() kutib qotib qolmaslik
        if not sys.stdin or not sys.stdin.isatty():
            log.warning(f"Xavfli buyruq fon rejimida to'xtatildi: {command}")
            return f"⚠️ Xavfsizlik filtri: '{command}' buyrug'i tizimni o'chiradi yoki ma'lumotlarni o'chirib tashlaydi. Telegram orqali qotib qolmaslik uchun avtomatik to'xtatildi."
        print(f"\n⚠️  DIQQAT: Xavfli terminal buyrug'i aniqlandi: {command}")
        confirm = input("   Janob, ushbu buyruqni bajarishga ruxsat berasizmi? [ha/yo'q]: ").strip().lower()
        if confirm not in ("ha", "h", "yes", "y"):
            log.warning(f"Foydalanuvchi buyruqni rad etdi: {command}")
            return "Xavfsizlik: Foydalanuvchi buyruqni bekor qildi."
    return tools.run_command(command)


# Gemini'ga uzatiladigan barcha vositalar ro'yxati
JARVIS_TOOLS = [
    tools.open_application,
    tools.close_application,
    tools.create_file,
    tools.create_folder,
    tools.list_directory,
    tools.search_files,
    tools.open_file,
    tools.read_file,
    tools.write_file,
    tools.move_file,
    tools.copy_file,
    tools.rename_file,
    tools.browser_search,
    tools.open_url,
    tools.youtube_search,
    safe_run_command,
    tools.take_screenshot,
    tools.set_volume,
    tools.set_brightness,
    tools.get_system_info,
    tools.get_current_datetime,
    tools.focus_window,
    tools.type_text,
    tools.press_key,
    tools.press_hotkey,
    tools.click_mouse,
    tools.send_telegram_message,
    tools.write_in_active_window,
]


class JarvisBrain:
    """Google Gemini API orqali suhbat va kompyuterni boshqarish."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY topilmadi!")

        self.client = genai.Client(api_key=api_key)
        self.chat = None
        self._init_chat()
        log.info("JARVIS miyasi (Google Gemini) muvaffaqiyatli ishga tushdi.")

    def _init_chat(self):
        """Chat sessiyasini barcha vositalar bilan ishga tushirish."""
        self.chat = self.client.chats.create(
            model=MODEL,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=JARVIS_TOOLS,
                temperature=0.3,
            )
        )

    def reset(self):
        """Suhbat tarixini tozalash."""
        self._init_chat()
        log.info("Suhbat tarixi tozalandi.")

    def process(self, user_input: str) -> str:
        """
        Foydalanuvchi buyrug'ini qabul qilib, kerakli vositani ishga tushirish
        va natijani qaytarish.
        """
        log.info(f"Foydalanuvchi: {user_input}")

        try:
            response = self.chat.send_message(user_input)
            answer = response.text if response.text else "Bajarildi, janob."
            log.info(f"JARVIS: {answer[:200]}")
            return answer

        except genai.errors.APIError as e:
            log.error(f"Gemini API xatosi: {e}")
            return f"❌ API xatosi: {e.message if hasattr(e, 'message') else e}"
        except Exception as e:
            log.error(f"Kutilmagan xato: {e}")
            return f"❌ Xatolik yuz berdi: {e}"


# Global yagona nusxa (singleton)
_default_brain = None


def get_brain() -> JarvisBrain:
    global _default_brain
    if _default_brain is None:
        _default_brain = JarvisBrain()
    return _default_brain


def ask_jarvis(user_input: str) -> str:
    """Ixtiyoriy moduldan to'g'ridan-to'g'ri JARVIS ga murojaat qilish."""
    return get_brain().process(user_input)

