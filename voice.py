"""
JARVIS — Ovoz tizimi (Voice System)
1. Ovozli javob: Gemini TTS (Tabiiy ovoz) + sounddevice orqali eshittirish.
2. Ovozli buyruq: Mikrofondan yozib olish (sounddevice) + Gemini orqali o'zbekcha matnga aylantirish.
"""
import os
import re
import wave
import time
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from google import genai
from google.genai import types

from logger import log

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

# Ovoz sozlamalari
SAMPLE_RATE_RECORD = 16000  # Mikrofon yozish chastotasi
SAMPLE_RATE_PLAY = 24000    # Gemini TTS chiqarish chastotasi
SILENCE_THRESHOLD = 500     # Ovoz sezuvchanligi (shovqin filtri)


def clean_text_for_speech(text: str) -> str:
    """Matnni ovozda o'qish uchun keraksiz belgilardan tozalash."""
    # Markdown teglari va emojilarni olib tashlash
    t = re.sub(r'[*_#`~\[\]\(\)\{\}\<\>]', ' ', text)
    t = re.sub(r'https?://\S+', 'havola', t)
    t = re.sub(r'[•\-]\s+', ' ', t)
    # Ko'p bo'shliqlarni bittaga keltirish
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def speak(text: str) -> bool:
    """Matnni o'zbek tilida ovoz bilan eshittirish."""
    if not text or not client:
        return False

    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return False

    log.info(f"Ovoz chiqarilmoqda: {clean_text[:60]}")

    try:
        # Gemini 2.5 Flash TTS modeli orqali audio generatsiya
        prompt = f"Please read the following text aloud clearly and naturally: {clean_text}"
        resp = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["AUDIO"]),
        )

        for candidate in resp.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.data:
                        pcm_data = part.inline_data.data
                        audio_array = np.frombuffer(pcm_data, dtype=np.int16)
                        # Dinamik orqali eshittirish
                        sd.play(audio_array, samplerate=SAMPLE_RATE_PLAY)
                        sd.wait()
                        return True

    except Exception as e:
        log.error(f"Gemini TTS xatosi: {e}")

        # Zaxira yo'l: Windows SAPI orqali o'qish (agar internet yoki API xato bersa)
        try:
            import comtypes.client
            speaker = comtypes.client.CreateObject("SAPI.SpVoice")
            speaker.Speak(clean_text)
            return True
        except Exception as se:
            log.error(f"SAPI zaxira xatosi: {se}")

    return False


def record_until_silence(max_duration: float = 8.0, silence_duration: float = 1.3) -> bytes:
    """
    Mikrofondan gapirilgan paytda yozib oladi.
    Gap tugab, sukunat bo'lganda avtomatik to'xtaydi.
    """
    chunk_size = 1024
    chunks = []
    has_speech = False
    silence_chunks = 0
    max_silence_chunks = int((silence_duration * SAMPLE_RATE_RECORD) / chunk_size)
    max_total_chunks = int((max_duration * SAMPLE_RATE_RECORD) / chunk_size)

    with sd.InputStream(samplerate=SAMPLE_RATE_RECORD, channels=1, dtype='int16', blocksize=chunk_size) as stream:
        for _ in range(max_total_chunks):
            chunk, _ = stream.read(chunk_size)
            volume = np.abs(chunk).mean()
            chunks.append(chunk)

            if volume > SILENCE_THRESHOLD:
                has_speech = True
                silence_chunks = 0
            else:
                if has_speech:
                    silence_chunks += 1
                    if silence_chunks >= max_silence_chunks:
                        # Foydalanuvchi gapirib bo'ldi
                        break

    if not has_speech:
        return b""

    audio_data = np.concatenate(chunks, axis=0)
    
    # WAV formatga o'tkazish
    import io
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE_RECORD)
        wf.writeframes(audio_data.tobytes())

    return wav_io.getvalue()


def record_fixed_duration(seconds: float = 5.0) -> bytes:
    """Belgilangan muddat (masalan, 5 soniya) mikrofondan yozib olish."""
    print(f"🎙 Gapiring ({int(seconds)} soniya)...")
    audio = sd.rec(int(seconds * SAMPLE_RATE_RECORD), samplerate=SAMPLE_RATE_RECORD, channels=1, dtype='int16')
    sd.wait()

    import io
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE_RECORD)
        wf.writeframes(audio.tobytes())

    return wav_io.getvalue()


def transcribe_audio(wav_bytes: bytes) -> str:
    """Audio faylni Gemini orqali o'zbek tilidagi matnga aylantirish."""
    if not wav_bytes or not client:
        return ""

    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"),
                "Ushbu audiodagi gapni o'zbek tilida aniq matnga aylantir (transkripsiya qil). "
                "Faqat va faqat aytilgan gapni qaytar. Agar ovozda gap bo'lmasa, 'hech narsa' deb qaytar."
            ]
        )
        text = resp.text.strip()
        if text.lower() in ("hech narsa", "hech narsa yo'q", "gap yo'q", "hech narsa."):
            return ""
        log.info(f"Ovoz tanildi: {text}")
        return text
    except Exception as e:
        log.error(f"Transkripsiya xatosi: {e}")
        return ""


def play_activation_beep():
    """Jarvis eshitishga tayyorligini bildiruvchi qisqa ovozli signal."""
    try:
        t = np.linspace(0, 0.15, int(SAMPLE_RATE_RECORD * 0.15), False)
        # 880Hz yoqimli ohang
        tone = np.sin(880 * t * 2 * np.pi) * 0.3
        sd.play((tone * 32767).astype(np.int16), samplerate=SAMPLE_RATE_RECORD)
        sd.wait()
    except Exception:
        pass
