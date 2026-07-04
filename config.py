"""Настройки бота PetShare Israel.

Секреты берутся из файла .env (лежит рядом, в git не попадает).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _load_env() -> None:
    """Читает файл .env и кладёт значения в переменные окружения."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env()

# Токен бота от BotFather
BOT_TOKEN = os.environ.get("PETSHARE_BOT_TOKEN", "")

# Telegram ID администратора (ваш ID — туда приходят заявки)
ADMIN_CHAT_ID = int(os.environ.get("PETSHARE_ADMIN_CHAT_ID", "0"))

# Google Sheets
SERVICE_ACCOUNT_FILE = str(BASE_DIR / "service_account.json")
SPREADSHEET_NAME = os.environ.get("PETSHARE_SPREADSHEET_NAME", "PetShare Israel")

# Названия листов в таблице
SHEET_ANIMALS = "Животные"
SHEET_REQUESTS = "Заявки"
SHEET_OWNERS = "Владельцы"
