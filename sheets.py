"""Работа с Google-таблицей PetShare Israel.

Данные кэшируются на несколько минут, чтобы не дёргать Google на каждый клик.
"""

import logging
import time

import gspread

import config

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 300  # 5 минут

_client = None
_cache = {}  # имя листа -> (время загрузки, список словарей)


def _get_spreadsheet():
    global _client
    if _client is None:
        _client = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
    return _client.open_by_key(config.SPREADSHEET_ID)


def _get_records(sheet_name):
    """Возвращает строки листа как список словарей, с кэшем."""
    now = time.time()
    cached = _cache.get(sheet_name)
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]
    ws = _get_spreadsheet().worksheet(sheet_name)
    records = ws.get_all_records()
    _cache[sheet_name] = (now, records)
    logger.info("Загружен лист '%s': %d строк", sheet_name, len(records))
    return records


def clear_cache():
    _cache.clear()


def get_animals():
    """Все активные животные из каталога."""
    animals = _get_records(config.SHEET_ANIMALS)
    return [a for a in animals if str(a.get("активна", "")).strip().lower() == "да"]


def get_categories():
    """Список категорий, в которых есть активные животные."""
    seen = []
    for a in get_animals():
        cat = str(a.get("категория", "")).strip()
        if cat and cat not in seen:
            seen.append(cat)
    return seen


def get_animals_by_category(category):
    return [a for a in get_animals() if str(a.get("категория", "")).strip() == category]


def get_animal_by_id(animal_id):
    for a in get_animals():
        if str(a.get("id", "")).strip() == animal_id:
            return a
    return None


def get_owner_by_id(owner_id):
    for o in _get_records(config.SHEET_OWNERS):
        if str(o.get("id", "")).strip() == owner_id:
            return o
    return None


def add_request(row):
    """Добавляет заявку в лист 'Заявки'. row — список значений по колонкам."""
    ws = _get_spreadsheet().worksheet(config.SHEET_REQUESTS)
    ws.append_row(row)
    _cache.pop(config.SHEET_REQUESTS, None)


def next_request_id():
    """Генерирует следующий номер заявки вида REQ-001."""
    records = _get_records(config.SHEET_REQUESTS)
    return f"REQ-{len(records) + 1:03d}"


def get_request(req_id):
    """Возвращает заявку по номеру как словарь, или None."""
    for r in _get_records(config.SHEET_REQUESTS):
        if str(r.get("id", "")).strip() == req_id:
            return r
    return None


def update_request_status(req_id, status):
    """Меняет статус заявки в листе 'Заявки'. Возвращает True при успехе."""
    ws = _get_spreadsheet().worksheet(config.SHEET_REQUESTS)
    cell = ws.find(req_id, in_column=1)
    if cell is None:
        return False
    headers = ws.row_values(1)
    status_col = headers.index("статус") + 1
    ws.update_cell(cell.row, status_col, status)
    _cache.pop(config.SHEET_REQUESTS, None)
    return True
