"""
╔══════════════════════════════════════════════════════════════╗
║                    J.A.R.V.I.S                               ║
║       Shaxsiy AI Yordamchi — Matnli va Ovozli Rejim          ║
║                                                              ║
║  Ishga tushirish:  python main.py                            ║
║  Ovozli buyruq:    "ovoz", "v" yoki shunchaki Enter bosing   ║
║  Doimiy tinglash:  "tingla" (Jarvis so'ziga faollashadi)     ║
║  Chiqish:          "chiqish", "exit"                         ║
╚══════════════════════════════════════════════════════════════╝
"""
import sys
import os
import threading

# Loyiha papkasini Python yo'liga qo'shish
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows konsolida UTF-8 (emojilar va o'zbekcha belgilar) uchun
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

from brain import JarvisBrain
from logger import log
import voice


# ─── Ranglar (terminal uchun) ───

class C:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


BANNER = f"""
{C.CYAN}{C.BOLD}
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
{C.RESET}
{C.DIM}  Shaxsiy AI Yordamchi — v2.0 (Matnli + Ovozli){C.RESET}
{C.YELLOW}  • Yozib buyruq berish: shunchaki matn yozing.{C.RESET}
{C.MAGENTA}  • Ovoz bilan gapirish: 'ovoz' deb yozing yoki shunchaki Enter bosing.{C.RESET}
{C.CYAN}  • Doimiy tinglash (Hotword): 'tingla' deb yozing.{C.RESET}
{C.DIM}  • Ovozli javobni yoqish/o'chirish: 'ovozli javob'.{C.RESET}
"""

EXIT_COMMANDS = {"chiqish", "exit", "quit", "q", "yopil", "to'xta"}


def run_continuous_listening(jarvis, voice_output_state):
    """Orqa fonda 'Jarvis' chaqiruv so'zini doimiy tinglash."""
    print(f"\n{C.MAGENTA}🎙 [Doimiy tinglash rejimi yoqildi] 'Jarvis, ...' deb buyruq bering. To'xtatish uchun Enter bosing.{C.RESET}\n")
    while voice_output_state.get("listening_active", False):
        try:
            # 3 soniyalik bloklarda yozib olish
            audio_bytes = voice.record_until_silence(max_duration=5.0, silence_duration=1.2)
            if not audio_bytes or not voice_output_state.get("listening_active", False):
                continue

            text = voice.transcribe_audio(audio_bytes)
            if not text:
                continue

            # "Jarvis" so'zi bor-yo'qligini tekshirish
            lower_text = text.lower()
            if "jarvis" in lower_text or "джарвис" in lower_text:
                print(f"\n{C.YELLOW}⚡ Jarvis eshitdi: {text}{C.RESET}")
                voice.play_activation_beep()

                # "Jarvis" so'zidan keyingi qismini olish yoki butun matnni jo'natish
                cmd = re_clean_wake_word(text)
                if not cmd:
                    # Agar faqat "Jarvis" degan bo'lsa, javob berib, buyruq kutadi
                    resp = "Eshitaman, buyuring."
                    print(f"{C.GREEN}{C.BOLD}JARVIS:{C.RESET} {resp}")
                    if voice_output_state.get("speak_answers", True):
                        voice.speak(resp)
                    continue

                print(f"{C.DIM}⏳ Bajarayapman...{C.RESET}")
                answer = jarvis.process(cmd)
                print(f"\n{C.GREEN}{C.BOLD}JARVIS:{C.RESET} {answer}\n")

                if voice_output_state.get("speak_answers", True):
                    voice.speak(answer)

        except Exception as e:
            log.error(f"Doimiy tinglashda xato: {e}")
            time.sleep(1)


def re_clean_wake_word(text: str) -> str:
    """'Jarvis' so'zini olib tashlab, toza buyruqni qoldirish."""
    import re
    cleaned = re.sub(r'^(jarvis|джарвис)[,\s]*', '', text, flags=re.IGNORECASE).strip()
    return cleaned if cleaned else text


def handle_voice_input(jarvis, speak_answers: bool):
    """Bitta ovozli buyruqni qabul qilish va bajarish."""
    voice.play_activation_beep()
    print(f"\n{C.MAGENTA}🎙 Mikrofon faol — marhamat, buyruqni ayting...{C.RESET}")

    audio_bytes = voice.record_until_silence(max_duration=8.0, silence_duration=1.3)
    if not audio_bytes:
        print(f"{C.YELLOW}⚠️ Ovoz eshitilmadi.{C.RESET}\n")
        return

    print(f"{C.DIM}🎧 Ovoz tahlil qilinmoqda...{C.RESET}")
    text = voice.transcribe_audio(audio_bytes)

    if not text:
        print(f"{C.YELLOW}⚠️ Gap tushunilmadi yoki bo'sh.{C.RESET}\n")
        return

    print(f"{C.CYAN}{C.BOLD}Siz (Ovoz) ❯ {C.RESET}{text}")
    print(f"{C.DIM}⏳ Bajarayapman...{C.RESET}")

    answer = jarvis.process(text)
    print(f"\n{C.GREEN}{C.BOLD}JARVIS:{C.RESET} {answer}\n")

    if speak_answers:
        voice.speak(answer)


def main():
    """Asosiy dastur tsikli."""
    print(BANNER)

    # .env faylda API kalit borligini tekshirish
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        print(f"{C.RED}❌ GEMINI_API_KEY topilmadi!{C.RESET}")
        print(f"{C.YELLOW}   .env faylni oching va API kalitingizni yozing.{C.RESET}\n")
        return

    # JARVIS miyasini ishga tushirish
    try:
        jarvis = JarvisBrain()
    except Exception as e:
        print(f"{C.RED}❌ JARVIS ishga tushmadi: {e}{C.RESET}")
        return

    print(f"{C.GREEN}✅ JARVIS 2.0 to'liq tayyor. Qani, nima qilamiz?{C.RESET}\n")
    log.info("=" * 50)
    log.info("JARVIS 2.0 sessiyasi boshlandi")
    log.info("=" * 50)

    # Ovoz holati sozlamalari
    voice_state = {
        "speak_answers": True,       # Javoblarni ovoz bilan o'qish (ha/yo'q)
        "listening_active": False,   # Doimiy tinglash
    }

    while True:
        try:
            # Foydalanuvchidan buyruq olish
            prompt_symbol = f"{C.CYAN}{C.BOLD}Siz ❯ {C.RESET}"
            user_input = input(prompt_symbol).strip()

            # Bo'sh qator bosilsa — qulaylik uchun darhol ovozli buyruq rejimiga o'tadi!
            if not user_input:
                handle_voice_input(jarvis, voice_state["speak_answers"])
                continue

            # Chiqish
            if user_input.lower() in EXIT_COMMANDS:
                bye_text = "Bo'pti, ko'rishguncha!"
                print(f"\n{C.GREEN}JARVIS: {bye_text} 👋{C.RESET}\n")
                if voice_state["speak_answers"]:
                    voice.speak(bye_text)
                log.info("Sessiya tugadi (foydalanuvchi chiqdi)")
                break

            # Tarixni tozalash
            if user_input.lower() in ("tozala", "clear", "reset", "yangi"):
                jarvis.reset()
                print(f"{C.GREEN}JARVIS: Tarix tozalandi. Yangidan boshlaymiz.{C.RESET}\n")
                continue

            # Ovozli javobni yoqish / o'chirish
            if user_input.lower() in ("ovozli javob", "ovozni yoq", "ovozni o'chir", "mute", "unmute"):
                voice_state["speak_answers"] = not voice_state["speak_answers"]
                status = "YOQILDI 🔊" if voice_state["speak_answers"] else "O'CHIRILDI 🔇"
                print(f"{C.YELLOW}JARVIS: Ovozli javob berish {status}.{C.RESET}\n")
                continue

            # Bitta ovozli buyruq olish
            if user_input.lower() in ("ovoz", "voice", "v", "gapir", "eshit"):
                handle_voice_input(jarvis, voice_state["speak_answers"])
                continue

            # Doimiy tinglash rejimini yoqish
            if user_input.lower() in ("tingla", "listen", "hotword", "jarvis"):
                voice_state["listening_active"] = True
                t = threading.Thread(target=run_continuous_listening, args=(jarvis, voice_state), daemon=True)
                t.start()
                input(f"{C.DIM}[Doimiy tinglashni to'xtatish uchun Enter bosing]{C.RESET}\n")
                voice_state["listening_active"] = False
                print(f"{C.YELLOW}JARVIS: Doimiy tinglash to'xtatildi.{C.RESET}\n")
                continue

            # Matnli buyruqni bajarish
            print(f"{C.DIM}⏳ Bajarayapman...{C.RESET}")
            answer = jarvis.process(user_input)
            print(f"\n{C.GREEN}{C.BOLD}JARVIS:{C.RESET} {answer}\n")

            # Javobni ovoz bilan o'qish (agar yoqilgan bo'lsa)
            if voice_state["speak_answers"]:
                voice.speak(answer)

        except KeyboardInterrupt:
            print(f"\n\n{C.GREEN}JARVIS: To'xtatildi. Nima qilamiz endi?{C.RESET}\n")
            continue

        except EOFError:
            print(f"\n{C.GREEN}JARVIS: Ko'rishguncha! 👋{C.RESET}\n")
            break

        except Exception as e:
            log.error(f"Kutilmagan xato: {e}")
            print(f"{C.RED}❌ Xatolik: {e}{C.RESET}\n")


if __name__ == "__main__":
    main()
