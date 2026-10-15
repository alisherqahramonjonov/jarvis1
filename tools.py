"""
JARVIS — Vositalar (Tools)
Kompyuterni boshqarish uchun barcha funksiyalar.
Windows va Mac qo'llab-quvvatlanadi.
"""
import os
import sys
import shutil
import subprocess
import webbrowser
import datetime
import platform as pf

from config import PLATFORM, APP_MAP_WINDOWS, APP_MAP_MAC
from logger import log


# ╔══════════════════════════════════════════════════════════════╗
# ║  DASTUR BOSHQARUVI                                         ║
# ╚══════════════════════════════════════════════════════════════╝

def open_application(app_name: str) -> str:
    """Dasturni ishga tushirish."""
    name = app_name.lower().strip()
    log.info(f"Dastur ochish: {app_name}")

    try:
        if PLATFORM == "Windows":
            exe = APP_MAP_WINDOWS.get(name, name)
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen(exe, shell=True)
            log.info(f"Ochildi: {exe}")
            return f"'{app_name}' dasturi ishga tushirildi."

        elif PLATFORM == "Darwin":
            app = APP_MAP_MAC.get(name, name)
            subprocess.Popen(["open", "-a", app])
            log.info(f"Ochildi: {app}")
            return f"'{app_name}' dasturi ishga tushirildi."

    except Exception as e:
        log.error(f"Dastur ochishda xato: {e}")
        return f"Xatolik: '{app_name}' ochilmadi — {e}"

    return f"Bu OS qo'llab-quvvatlanmaydi: {PLATFORM}"


def close_application(app_name: str) -> str:
    """Dasturni yopish (majburiy)."""
    name = app_name.lower().strip()
    log.info(f"Dastur yopish: {app_name}")

    try:
        if PLATFORM == "Windows":
            exe = APP_MAP_WINDOWS.get(name, name)
            if not exe.endswith(".exe"):
                exe += ".exe"
            r = subprocess.run(
                ["taskkill", "/IM", exe, "/F"],
                capture_output=True, text=True
            )
            if r.returncode == 0:
                return f"'{app_name}' yopildi."
            return f"'{app_name}' topilmadi yoki yopilmadi. {r.stderr.strip()}"

        elif PLATFORM == "Darwin":
            app = APP_MAP_MAC.get(name, name)
            subprocess.run(["pkill", "-f", app])
            return f"'{app_name}' yopildi."

    except Exception as e:
        log.error(f"Dastur yopishda xato: {e}")
        return f"Xatolik: {e}"

    return f"Bu OS qo'llab-quvvatlanmaydi: {PLATFORM}"


# ╔══════════════════════════════════════════════════════════════╗
# ║  FAYL VA PAPKA AMALLARI                                    ║
# ╚══════════════════════════════════════════════════════════════╝

def create_file(file_path: str, content: str = "") -> str:
    """Yangi fayl yaratish (yoki ustiga yozish)."""
    try:
        file_path = os.path.expanduser(file_path)
        d = os.path.dirname(file_path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        log.info(f"Fayl yaratildi: {file_path}")
        return f"Fayl yaratildi: {file_path}"
    except Exception as e:
        log.error(f"Fayl yaratishda xato: {e}")
        return f"Xatolik: {e}"


def create_folder(folder_path: str) -> str:
    """Yangi papka yaratish."""
    try:
        folder_path = os.path.expanduser(folder_path)
        os.makedirs(folder_path, exist_ok=True)
        log.info(f"Papka yaratildi: {folder_path}")
        return f"Papka yaratildi: {folder_path}"
    except Exception as e:
        log.error(f"Papka yaratishda xato: {e}")
        return f"Xatolik: {e}"


def list_directory(directory: str = ".") -> str:
    """Papka ichidagi fayl va papkalarni ko'rsatish."""
    try:
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            return f"Papka topilmadi: {directory}"

        items = os.listdir(directory)
        if not items:
            return f"Papka bo'sh: {directory}"

        result_lines = []
        for item in sorted(items)[:100]:
            full = os.path.join(directory, item)
            if os.path.isdir(full):
                result_lines.append(f"  📁 {item}/")
            else:
                size = os.path.getsize(full)
                if size < 1024:
                    s = f"{size} B"
                elif size < 1024 * 1024:
                    s = f"{size // 1024} KB"
                else:
                    s = f"{size // (1024 * 1024)} MB"
                result_lines.append(f"  📄 {item}  ({s})")

        header = f"📂 {directory} — {len(items)} ta element:\n"
        return header + "\n".join(result_lines)
    except Exception as e:
        log.error(f"Papka ko'rishda xato: {e}")
        return f"Xatolik: {e}"


def search_files(directory: str, pattern: str) -> str:
    """Fayl nomi bo'yicha qidirish (rekursiv)."""
    try:
        directory = os.path.expanduser(directory)
        results = []
        for root, dirs, files in os.walk(directory):
            for name in files:
                if pattern.lower() in name.lower():
                    results.append(os.path.join(root, name))
                if len(results) >= 50:
                    break
            if len(results) >= 50:
                break

        if results:
            file_list = "\n".join(f"  • {f}" for f in results)
            return f"'{pattern}' bo'yicha {len(results)} ta fayl topildi:\n{file_list}"
        return f"'{pattern}' bo'yicha hech narsa topilmadi."
    except Exception as e:
        log.error(f"Qidirishda xato: {e}")
        return f"Xatolik: {e}"


def open_file(file_path: str) -> str:
    """Faylni standart dasturda ochish."""
    try:
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(file_path):
            return f"Fayl topilmadi: {file_path}"

        if PLATFORM == "Windows":
            os.startfile(file_path)
        elif PLATFORM == "Darwin":
            subprocess.Popen(["open", file_path])
        else:
            subprocess.Popen(["xdg-open", file_path])

        log.info(f"Fayl ochildi: {file_path}")
        return f"Fayl ochildi: {file_path}"
    except Exception as e:
        log.error(f"Fayl ochishda xato: {e}")
        return f"Xatolik: {e}"


def read_file(file_path: str) -> str:
    """Fayl tarkibini o'qish (max 10 000 belgi)."""
    try:
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(file_path):
            return f"Fayl topilmadi: {file_path}"

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(10_000)

        log.info(f"Fayl o'qildi: {file_path}")
        return f"📄 {file_path} tarkibi:\n\n{content}"
    except Exception as e:
        log.error(f"Fayl o'qishda xato: {e}")
        return f"Xatolik: {e}"


def write_file(file_path: str, content: str) -> str:
    """Mavjud faylga yozish yoki yangi fayl yaratish."""
    return create_file(file_path, content)


def move_file(source: str, destination: str) -> str:
    """Faylni boshqa joyga ko'chirish."""
    try:
        source = os.path.expanduser(source)
        destination = os.path.expanduser(destination)
        if not os.path.exists(source):
            return f"Manba topilmadi: {source}"
        shutil.move(source, destination)
        log.info(f"Ko'chirildi: {source} → {destination}")
        return f"Ko'chirildi: {source} → {destination}"
    except Exception as e:
        log.error(f"Ko'chirishda xato: {e}")
        return f"Xatolik: {e}"


def copy_file(source: str, destination: str) -> str:
    """Faylning nusxasini olish."""
    try:
        source = os.path.expanduser(source)
        destination = os.path.expanduser(destination)
        if not os.path.exists(source):
            return f"Manba topilmadi: {source}"
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            dest_dir = os.path.dirname(destination)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(source, destination)
        log.info(f"Nusxa olindi: {source} → {destination}")
        return f"Nusxa olindi: {source} → {destination}"
    except Exception as e:
        log.error(f"Nusxalashda xato: {e}")
        return f"Xatolik: {e}"


def rename_file(old_path: str, new_name: str) -> str:
    """Fayl yoki papka nomini o'zgartirish."""
    try:
        old_path = os.path.expanduser(old_path)
        if not os.path.exists(old_path):
            return f"Topilmadi: {old_path}"
        directory = os.path.dirname(old_path)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        log.info(f"Nom o'zgartirildi: {old_path} → {new_path}")
        return f"Nom o'zgartirildi: {new_name}"
    except Exception as e:
        log.error(f"Nom o'zgartirishda xato: {e}")
        return f"Xatolik: {e}"


# ╔══════════════════════════════════════════════════════════════╗
# ║  BRAUZER                                                    ║
# ╚══════════════════════════════════════════════════════════════╝

def browser_search(query: str) -> str:
    """Google'da qidirish (brauzer ochiladi)."""
    try:
        import urllib.parse
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        log.info(f"Brauzerda qidirildi: {query}")
        return f"Brauzerda qidirildi: '{query}'"
    except Exception as e:
        log.error(f"Brauzer xatosi: {e}")
        return f"Xatolik: {e}"


def open_url(url: str) -> str:
    """Saytni brauzerda ochish."""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        log.info(f"Sayt ochildi: {url}")
        return f"Sayt ochildi: {url}"
    except Exception as e:
        log.error(f"Sayt ochishda xato: {e}")
        return f"Xatolik: {e}"


def youtube_search(query: str) -> str:
    """YouTube'da qidirish."""
    try:
        import urllib.parse
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(url)
        log.info(f"YouTube qidiruvi: {query}")
        return f"YouTube'da qidirildi: '{query}'"
    except Exception as e:
        log.error(f"YouTube xatosi: {e}")
        return f"Xatolik: {e}"


# ╔══════════════════════════════════════════════════════════════╗
# ║  TERMINAL                                                   ║
# ╚══════════════════════════════════════════════════════════════╝

def run_command(command: str) -> str:
    """Terminal buyrug'ini bajarish."""
    log.info(f"Buyruq: {command}")
    try:
        r = subprocess.run(
            command, shell=True,
            capture_output=True, text=True,
            timeout=30, encoding="utf-8", errors="replace",
        )

        output = ""
        if r.stdout:
            output += r.stdout.strip()
        if r.stderr:
            output += ("\n" if output else "") + r.stderr.strip()
        if not output:
            output = "(Buyruq bajarildi, chiqish yo'q)"

        # Juda uzun bo'lsa, qisqartiramiz
        if len(output) > 5000:
            output = output[:5000] + "\n... (qisqartirildi)"

        log.info(f"Buyruq natijasi (kod {r.returncode}): {output[:200]}")
        return f"Buyruq: {command}\nNatija (kod: {r.returncode}):\n{output}"

    except subprocess.TimeoutExpired:
        log.warning(f"Buyruq vaqti tugadi: {command}")
        return f"Buyruq vaqti tugadi (30s): {command}"
    except Exception as e:
        log.error(f"Buyruq xatosi: {e}")
        return f"Xatolik: {e}"


# ╔══════════════════════════════════════════════════════════════╗
# ║  SKRINSHOT                                                   ║
# ╚══════════════════════════════════════════════════════════════╝

def take_screenshot(save_path: str = "") -> str:
    """Ekran rasmini olish va saqlash."""
    try:
        from PIL import ImageGrab

        if not save_path:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(desktop, f"screenshot_{ts}.png")

        save_path = os.path.expanduser(save_path)
        d = os.path.dirname(save_path)
        if d:
            os.makedirs(d, exist_ok=True)

        screenshot = ImageGrab.grab()
        screenshot.save(save_path)
        log.info(f"Skrinshot saqlandi: {save_path}")
        return f"Skrinshot saqlandi: {save_path}"
    except ImportError:
        return "Xatolik: Pillow kutubxonasi kerak. 'pip install Pillow' bajaring."
    except Exception as e:
        log.error(f"Skrinshot xatosi: {e}")
        return f"Xatolik: {e}"


# ╔══════════════════════════════════════════════════════════════╗
# ║  TIZIM SOZLAMALARI                                          ║
# ╚══════════════════════════════════════════════════════════════╝

def set_volume(level: int) -> str:
    """Ovoz balandligini o'rnatish (0-100)."""
    level = max(0, min(100, level))
    log.info(f"Ovoz: {level}%")

    if PLATFORM == "Windows":
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return f"Ovoz balandligi {level}% ga o'rnatildi."
        except ImportError:
            # Pycaw bo'lmasa, PowerShell bilan urinib ko'ramiz
            try:
                ps = (
                    f'$wshell = New-Object -ComObject WScript.Shell; '
                    f'1..50 | ForEach-Object {{ $wshell.SendKeys([char]174) }}; '
                    f'1..{level // 2} | ForEach-Object {{ $wshell.SendKeys([char]175) }}'
                )
                subprocess.run(
                    ["powershell", "-Command", ps],
                    capture_output=True, timeout=15,
                )
                return f"Ovoz balandligi ~{level}% ga o'rnatildi (taxminiy)."
            except Exception as e:
                return f"Xatolik: {e}"
        except Exception as e:
            return f"Xatolik: {e}"

    elif PLATFORM == "Darwin":
        try:
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {level}"],
                timeout=5,
            )
            return f"Ovoz balandligi {level}% ga o'rnatildi."
        except Exception as e:
            return f"Xatolik: {e}"

    return f"Bu OS qo'llab-quvvatlanmaydi: {PLATFORM}"


def set_brightness(level: int) -> str:
    """Ekran yorqinligini o'rnatish (0-100). Faqat noutbuklarda ishlaydi."""
    level = max(0, min(100, level))
    log.info(f"Yorqinlik: {level}%")

    if PLATFORM == "Windows":
        try:
            ps = (
                f"(Get-WmiObject -Namespace root/WMI "
                f"-Class WmiMonitorBrightnessMethods)"
                f".WmiSetBrightness(1,{level})"
            )
            r = subprocess.run(
                ["powershell", "-Command", ps],
                capture_output=True, text=True, timeout=10,
            )
            if r.returncode == 0:
                return f"Yorqinlik {level}% ga o'rnatildi."
            return f"Xatolik (faqat noutbuklarda ishlaydi): {r.stderr.strip()}"
        except Exception as e:
            return f"Xatolik: {e}"

    elif PLATFORM == "Darwin":
        try:
            brightness = level / 100.0
            subprocess.run(["brightness", str(brightness)], timeout=5)
            return f"Yorqinlik {level}% ga o'rnatildi."
        except Exception as e:
            return f"Xatolik: {e}"

    return f"Bu OS qo'llab-quvvatlanmaydi: {PLATFORM}"


# ╔══════════════════════════════════════════════════════════════╗
# ║  TIZIM MA'LUMOTLARI                                        ║
# ╚══════════════════════════════════════════════════════════════╝

def get_system_info() -> str:
    """Kompyuter haqida umumiy ma'lumot."""
    info = (
        f"Tizim ma'lumotlari:\n"
        f"  • OS: {pf.system()} {pf.release()} ({pf.version()})\n"
        f"  • Kompyuter: {pf.node()}\n"
        f"  • Protsessor: {pf.processor()}\n"
        f"  • Arxitektura: {pf.machine()}\n"
        f"  • Python: {pf.python_version()}\n"
        f"  • Foydalanuvchi: {os.environ.get('USERNAME', os.environ.get('USER', '?'))}\n"
        f"  • Uy papkasi: {os.path.expanduser('~')}"
    )
    log.info("Tizim ma'lumotlari so'raldi")
    return info


def get_current_datetime() -> str:
    """Hozirgi sana va vaqtni qaytarish."""
    now = datetime.datetime.now()
    days_uz = {
        "Monday": "Dushanba", "Tuesday": "Seshanba",
        "Wednesday": "Chorshanba", "Thursday": "Payshanba",
        "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba",
    }
    day_name = days_uz.get(now.strftime("%A"), now.strftime("%A"))
    return f"Hozir: {now.strftime('%Y-%m-%d %H:%M:%S')} ({day_name})"


# ╔══════════════════════════════════════════════════════════════╗
# ║  GUI VA ILOVALARNI BOSHQARISH (TELEGRAM, WORD, BRAUZER...) ║
# ╚══════════════════════════════════════════════════════════════╝

def focus_window(window_title: str) -> str:
    """Ilova oynasini topib, ekranga faol qilib chiqarish."""
    try:
        import pygetwindow as gw
        import time

        titles = gw.getAllTitles()
        matched = [t for t in titles if window_title.lower() in t.lower() and t.strip()]
        if not matched:
            return f"'{window_title}' nomli oyna topilmadi. Ochiq oynalar: {', '.join(t for t in titles if t.strip())[:150]}"

        win = gw.getWindowsWithTitle(matched[0])[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.5)
        log.info(f"Oyna faollashtirildi: {matched[0]}")
        return f"'{matched[0]}' oynasi ekranga chiqarildi."
    except Exception as e:
        log.error(f"Oyna faollashtirish xatosi: {e}")
        return f"Xatolik: {e}"


def type_text(text: str, press_enter: bool = False) -> str:
    """Hozirgi faol oynaga istalgan tildagi matnni (o'zbek, kirill, emoji) yozish."""
    try:
        import pyautogui
        import pyperclip
        import time

        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "v")
        if press_enter:
            time.sleep(0.2)
            pyautogui.press("enter")
        log.info(f"Matn yozildi: {text[:50]}")
        return f"Matn faol ilovaga yozildi: '{text}'"
    except Exception as e:
        log.error(f"Matn yozish xatosi: {e}")
        return f"Xatolik: {e}"


def press_key(key: str) -> str:
    """Klaviaturadagi tugmani bosish (enter, esc, tab, space, backspace, up, down)."""
    try:
        import pyautogui
        pyautogui.press(key.lower().strip())
        log.info(f"Tugma bosildi: {key}")
        return f"'{key}' tugmasi bosildi."
    except Exception as e:
        log.error(f"Tugma bosish xatosi: {e}")
        return f"Xatolik: {e}"


def press_hotkey(keys: str) -> str:
    """Tugmalar birikmasini bosish (masalan: 'ctrl+c', 'ctrl+v', 'ctrl+a', 'alt+tab', 'ctrl+f', 'ctrl+k')."""
    try:
        import pyautogui
        parts = [k.strip().lower() for k in keys.split("+")]
        pyautogui.hotkey(*parts)
        log.info(f"Hotkey bosildi: {keys}")
        return f"'{keys}' birikmasi bosildi."
    except Exception as e:
        log.error(f"Hotkey xatosi: {e}")
        return f"Xatolik: {e}"


def click_mouse(x: int = -1, y: int = -1) -> str:
    """Sichqonchani ekranda ko'rsatilgan (x, y) nuqtada bosish. Agar kiritilmasa, turgan joyida bosadi."""
    try:
        import pyautogui
        if x >= 0 and y >= 0:
            pyautogui.click(x, y)
            return f"Sichqoncha ({x}, {y}) koordinatasida bosildi."
        else:
            pyautogui.click()
            pos = pyautogui.position()
            return f"Sichqoncha ({pos.x}, {pos.y}) nuqtasida bosildi."
    except Exception as e:
        log.error(f"Sichqoncha bosish xatosi: {e}")
        return f"Xatolik: {e}"


def send_telegram_message(recipient: str, message: str) -> str:
    """Telegram ilovasida ko'rsatilgan kontaktga (yoki guruhga) xabar yozish va yuborish."""
    try:
        import time
        import pyautogui
        import pyperclip
        import pygetwindow as gw

        log.info(f"Telegramda xabar yuborilmoqda: {recipient} -> {message}")

        # 1. Telegram oynasini topish yoki ochish
        telegram_windows = [w for w in gw.getAllWindows() if "telegram" in w.title.lower()]
        target_win = None

        if telegram_windows:
            target_win = telegram_windows[0]
            if target_win.isMinimized:
                target_win.restore()
            target_win.activate()
            time.sleep(1.0)
        else:
            open_application("telegram")
            # Telegram ochilishini kutamiz (10 soniyagacha)
            for _ in range(20):
                time.sleep(0.5)
                wins = [w for w in gw.getAllWindows() if "telegram" in w.title.lower()]
                if wins:
                    target_win = wins[0]
                    if target_win.isMinimized:
                        target_win.restore()
                    target_win.activate()
                    time.sleep(1.0)
                    break

        # Xavfsizlik: oyna faolligini tekshirish
        active = gw.getActiveWindow()
        if not active or "telegram" not in active.title.lower():
            if target_win:
                try:
                    target_win.activate()
                    time.sleep(1.0)
                except Exception:
                    pass
            active = gw.getActiveWindow()

        if not active or "telegram" not in active.title.lower():
            return "Telegram dasturi ekranda ochilmadi yoki faollashmadi. Iltimos, Telegram ilovasi o'rnatilganini tekshiring."

        time.sleep(0.5)

        # 2. Qidiruvni ochish (Ctrl+K yoki Esc -> Ctrl+F)
        pyautogui.press("esc")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "k")
        time.sleep(0.5)

        # 3. Qabul qiluvchi ismini kiritish va ochish
        clean_recipient = recipient.strip()
        pyperclip.copy(clean_recipient)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1.5)  # Qidiruv ro'yxati chiqishini kutish
        pyautogui.press("enter")
        time.sleep(0.8)

        # 4. Xabarni yozish va yuborish
        if message:
            pyperclip.copy(message)
            time.sleep(0.2)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.3)
            pyautogui.press("enter")
            log.info(f"Telegram xabari muvaffaqiyatli yuborildi: {clean_recipient}")
            return f"Telegram'da '{clean_recipient}' chatiga xabar muvaffaqiyatli yuborildi: '{message}'"
        else:
            return f"Telegram'da '{clean_recipient}' chati ochildi."

    except Exception as e:
        log.error(f"Telegram xabarida xatolik: {e}")
        return f"Xatolik: {e}"


def write_in_active_window(text: str, press_enter: bool = True) -> str:
    """Hozirgi faol oynaga (Telegram, Word, Brauzer, Bloknot va boshqalar) matn kiritish."""
    return type_text(text, press_enter=press_enter)


# ╔══════════════════════════════════════════════════════════════╗
# ║  VOSITALAR RO'YXATI                                        ║
# ╚══════════════════════════════════════════════════════════════╝

TOOL_FUNCTIONS = {
    "open_application": open_application,
    "close_application": close_application,
    "create_file": create_file,
    "create_folder": create_folder,
    "list_directory": list_directory,
    "search_files": search_files,
    "open_file": open_file,
    "read_file": read_file,
    "write_file": write_file,
    "move_file": move_file,
    "copy_file": copy_file,
    "rename_file": rename_file,
    "browser_search": browser_search,
    "open_url": open_url,
    "youtube_search": youtube_search,
    "run_command": run_command,
    "take_screenshot": take_screenshot,
    "set_volume": set_volume,
    "set_brightness": set_brightness,
    "get_system_info": get_system_info,
    "get_current_datetime": get_current_datetime,
    "focus_window": focus_window,
    "type_text": type_text,
    "press_key": press_key,
    "press_hotkey": press_hotkey,
    "click_mouse": click_mouse,
    "send_telegram_message": send_telegram_message,
    "write_in_active_window": write_in_active_window,
}
