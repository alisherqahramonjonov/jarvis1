"""
╔══════════════════════════════════════════════════════════════╗
║               J.A.R.V.I.S HOLOGRAPHIC HUD APP                ║
║          Futuristik Iron Man Sci-Fi Interfeysi               ║
║                                                              ║
║  Ishga tushirish:  python app.py                             ║
╚══════════════════════════════════════════════════════════════╝
"""
import os
import sys
import threading
import webview
import psutil

# Loyiha papkasini yo'lga qo'shish
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain import JarvisBrain
from logger import log
import voice
import tools


class JarvisHudApi:
    """JavaScript (HUD) va Python o'rtasidagi ikki tomonlama ko'prik."""

    def __init__(self):
        self.jarvis = None
        try:
            self.jarvis = JarvisBrain()
            log.info("HUD uchun JARVIS miyasi yuklandi.")
        except Exception as e:
            log.error(f"HUD miyasini yuklashda xato: {e}")

    def send_command(self, cmd: str) -> str:
        """Matnli buyruqni qabul qilib, bajarish va ovoz chiqarish."""
        if not cmd or not self.jarvis:
            return "Buyruq topilmadi yoki tizim faol emas."

        log.info(f"HUD buyrug'i: {cmd}")
        answer = self.jarvis.process(cmd)

        # Ovozli javobni alohida oqimda eshittirish (interfeys qotib qolmasligi uchun)
        threading.Thread(target=voice.speak, args=(answer,), daemon=True).start()

        return answer

    def record_voice(self) -> dict:
        """Mikrofondan ovozni yozib olib, transkripsiya qilish va buyruqni bajarish."""
        if not self.jarvis:
            return {"recognized_text": "", "answer": "Tizim tayyor emas."}

        # 1. Tovushli signal
        voice.play_activation_beep()

        # 2. Mikrofondan yozib olish (gap to'xtaguncha)
        wav_bytes = voice.record_until_silence(max_duration=7.0, silence_duration=1.2)
        if not wav_bytes:
            return {"recognized_text": "(Ovoz eshitilmadi)", "answer": "Janob, hech narsa eshitilmadi."}

        # 3. Matnga aylantirish
        text = voice.transcribe_audio(wav_bytes)
        if not text:
            return {"recognized_text": "(Tushunarsiz audio)", "answer": "Gapingizni tushunolmadim, qaytadan ayting."}

        # 4. Buyruqni bajarish
        answer = self.jarvis.process(text)

        # 5. Ovozli javob
        threading.Thread(target=voice.speak, args=(answer,), daemon=True).start()

        return {
            "recognized_text": text,
            "answer": answer
        }

    def get_system_stats(self) -> dict:
        """Real vaqtda kompyuter resurslarini (CPU, RAM, Disk) qaytarish."""
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk_obj = psutil.disk_usage("C:")
            disk_percent = disk_obj.percent

            # GB ko'rinishida hisoblash
            used_gb = round(disk_obj.used / (1024 ** 3), 1)
            total_gb = round(disk_obj.total / (1024 ** 3), 1)

            return {
                "cpu": cpu,
                "ram": ram,
                "disk": disk_percent,
                "storage_text": f"{used_gb} / {total_gb} GB"
            }
        except Exception as e:
            return {"cpu": 20, "ram": 50, "disk": 40, "storage_text": "261 / 293 GB"}

    def quick_action(self, action_name: str) -> str:
        """Tezkor tugmalar amallarini bajarish."""
        log.info(f"Tezkor amal: {action_name}")
        act = action_name.lower().strip()

        if "youtube" in act:
            tools.browser_search("https://www.youtube.com")
            return "YouTube brauzerda ochildi."
        elif "telegram" in act:
            tools.open_application("telegram")
            return "Telegram dasturi ishga tushirildi."
        elif "skrinshot" in act:
            path = tools.take_screenshot()
            return f"Skrinshot olindi: {path}"
        elif "bloknot" in act:
            tools.open_application("notepad")
            return "Bloknot ochildi."
        elif "musiqa" in act:
            tools.youtube_search("yaxshi qo'shiqlar")
            return "YouTube musiqa qidiruvi ochildi."
        elif "50%" in act:
            tools.set_volume(50)
            return "Ovoz balandligi 50% ga o'rnatildi."
        else:
            return f"Amal bajarildi: {action_name}"


def main():
    ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")
    index_path = os.path.join(ui_dir, "index.html")

    api = JarvisHudApi()

    # PyWebView oynasi
    window = webview.create_window(
        title="J.A.R.V.I.S — Holographic System Interface",
        url=index_path,
        js_api=api,
        width=1280,
        height=740,
        min_size=(960, 580),
        background_color="#020b14",
    )

    webview.start(debug=False)


if __name__ == "__main__":
    main()
