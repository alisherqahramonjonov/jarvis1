"""
JARVIS — Log tizimi
Har bir buyruq va natija log faylga yoziladi.
"""
import os
import logging
from datetime import datetime


def setup_logger():
    """Log tizimini sozlash. logs/ papkasiga kunlik fayl yozadi."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir, f"jarvis_{datetime.now().strftime('%Y-%m-%d')}.log"
    )

    logger = logging.getLogger("jarvis")
    logger.setLevel(logging.DEBUG)

    # Bir xil handler ikki marta qo'shilmasligi uchun
    if not logger.handlers:
        # Faylga yozish
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)

        # Terminalga faqat ogohlantirishlar
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)

        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


log = setup_logger()
