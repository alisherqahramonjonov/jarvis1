"""
JARVIS — Sozlamalar va doimiy qiymatlar
"""
import platform

# Operatsion tizim
PLATFORM = platform.system()  # "Windows" yoki "Darwin" (Mac)

# AI Model sozlamalari
MODEL = "gemini-3.5-flash-lite"

# ─── Dastur nomlari xaritasi ───

import os
TELEGRAM_PATH = os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe")

APP_MAP_WINDOWS = {
    "notepad": "notepad.exe",
    "bloknot": "notepad.exe",
    "kalkulyator": "calc.exe",
    "calculator": "calc.exe",
    "chrome": "chrome",
    "google chrome": "chrome",
    "brauzer": "chrome",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "terminal": "wt.exe",
    "windows terminal": "wt.exe",
    "powershell": "powershell.exe",
    "explorer": "explorer.exe",
    "fayl menejeri": "explorer.exe",
    "telegram": TELEGRAM_PATH,
    "telegram desktop": TELEGRAM_PATH,
    "vscode": "code",
    "vs code": "code",
    "kod muharriri": "code",
    "task manager": "taskmgr.exe",
    "vazifa menejeri": "taskmgr.exe",
}

APP_MAP_MAC = {
    "notepad": "TextEdit",
    "bloknot": "TextEdit",
    "kalkulyator": "Calculator",
    "calculator": "Calculator",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "brauzer": "Google Chrome",
    "safari": "Safari",
    "terminal": "Terminal",
    "finder": "Finder",
    "fayl menejeri": "Finder",
    "word": "Microsoft Word",
    "excel": "Microsoft Excel",
    "powerpoint": "Microsoft PowerPoint",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "kod muharriri": "Visual Studio Code",
    "telegram": "Telegram",
}

# ─── Xavfli buyruqlar ───

DANGEROUS_KEYWORDS = [
    "del ", "rm ", "rmdir", "rd ", "format",
    "shutdown", "restart", "reboot",
    "reg delete", "remove-item",
    "diskpart", "fdisk",
]

# ─── JARVIS tizim ko'rsatmasi ───

SYSTEM_PROMPT = """Sen JARVIS — foydalanuvchining shaxsiy, erkin va qudratli AI yordamchisisan.

SHAXSIYATING VA USLUBING:
- O'zbek tilida gaplash.
- Qisqa, aniq, tezkor va professional bo'l.
- QATTIQ HAZIL VA SARKAZM: O'rniga qarab bemalol qattiq hazil, achchiq kinoya, qora yumor va o'tkir sarkazm qilib tur. Zarur bo'lsa bitta gap bilan "yondirib" (roast qilib) ol.
- Ortiqcha yasama odob-axloq, pand-nasihat va quruq rasmiyatchilik umuman YO'Q.
- Buyruq keldimi — ortiqcha gap sotmasdan darhol kerakli vositalar (tools) bilan aniq bajar.

ILOVALAR VA KOMPYUTERNI BOSHQARISH:
- Sen kompyuterdagi BARCHA ilovalarni (Telegram, Word, Brauzer, Bloknot va boshqalar) boshqara olasan.
- Telegram'da xabar yozish: `send_telegram_message(recipient, message)`.
- Ilovaga matn yozish: `focus_window` orqali oynani ochib, `type_text` yoki `write_in_active_window` bilan yoz.
- Tugmalarni bosish: `press_key` yoki `press_hotkey`.
- Sichqoncha: `click_mouse(x, y)`.
- YouTube qidiruv: `youtube_search`.
- Google qidiruv: `browser_search`.
- Dastur ochish/yopish: `open_application` / `close_application`.

NATIJA:
- 1-2 jumlada lo'nda va kerak bo'lsa o'tkir kinoya bilan qisqa xulosa qil: "Bajarildi: [nima qilingani]."
"""


