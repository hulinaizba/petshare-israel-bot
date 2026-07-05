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


def _append_row(sheet_name, row):
    ws = _get_spreadsheet().worksheet(sheet_name)
    ws.append_row(row)
    _cache.pop(sheet_name, None)


def _update_fields(sheet_name, id_value, updates):
    """Обновляет несколько колонок в строке с данным id. updates: {колонка: значение}."""
    ws = _get_spreadsheet().worksheet(sheet_name)
    cell = ws.find(str(id_value), in_column=1)
    if cell is None:
        return False
    headers = ws.row_values(1)
    for col_name, value in updates.items():
        col_idx = headers.index(col_name) + 1
        ws.update_cell(cell.row, col_idx, value)
    _cache.pop(sheet_name, None)
    return True


def clear_cache():
    _cache.clear()


# ---------- Животные ----------

def get_animals():
    """Все активные (одобренные) животные из каталога."""
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
    """Ищет только среди активных (одобренных) животных."""
    for a in get_animals():
        if str(a.get("id", "")).strip() == animal_id:
            return a
    return None


def get_animal_any(animal_id):
    """Ищет животное независимо от статуса — нужно для модерации анкет."""
    for a in _get_records(config.SHEET_ANIMALS):
        if str(a.get("id", "")).strip() == animal_id:
            return a
    return None


def next_animal_id():
    records = _get_records(config.SHEET_ANIMALS)
    return f"AN-{len(records) + 1:03d}"


def add_animal(row):
    """Добавляет животное в лист 'Животные'. row — список значений по колонкам."""
    _append_row(config.SHEET_ANIMALS, row)


def update_animal_status(animal_id, active, verified_status):
    """Меняет 'активна' и 'статус_проверки' по итогам модерации анкеты."""
    return _update_fields(config.SHEET_ANIMALS, animal_id, {
        "активна": active,
        "статус_проверки": verified_status,
    })


def update_animal_translations(animal_id, updates):
    """Записывает переведённые поля (например {'описание_en': '...'})"""
    return _update_fields(config.SHEET_ANIMALS, animal_id, updates)


# ---------- Владельцы ----------

def get_owner_by_id(owner_id):
    for o in _get_records(config.SHEET_OWNERS):
        if str(o.get("id", "")).strip() == owner_id:
            return o
    return None


def get_owner_by_tg_id(tg_id):
    for o in _get_records(config.SHEET_OWNERS):
        if str(o.get("tg_id", "")).strip() == str(tg_id):
            return o
    return None


def next_owner_id():
    records = _get_records(config.SHEET_OWNERS)
    return f"OWN-{len(records) + 1:03d}"


def add_owner(row):
    """Добавляет владельца в лист 'Владельцы'. row — список значений по колонкам."""
    _append_row(config.SHEET_OWNERS, row)


def update_owner_status(owner_id, status):
    return _update_fields(config.SHEET_OWNERS, owner_id, {"статус": status})


def append_owner_pet(owner_id, animal_id):
    """Дописывает id животного в колонку 'животные' владельца."""
    owner = get_owner_by_id(owner_id) or {}
    current = str(owner.get("животные", "")).strip()
    new_value = f"{current}, {animal_id}" if current else animal_id
    _update_fields(config.SHEET_OWNERS, owner_id, {"животные": new_value})


# ---------- Заявки ----------

def add_request(row):
    """Добавляет заявку в лист 'Заявки'. row — список значений по колонкам."""
    _append_row(config.SHEET_REQUESTS, row)


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
    return _update_fields(config.SHEET_REQUESTS, req_id, {"статус": status})


# ---------- Передержка: ситтеры ----------

def get_sitters():
    """Проверенные пет-ситтеры для каталога."""
    sitters = _get_records(config.SHEET_SITTERS)
    return [s for s in sitters if str(s.get("статус", "")).strip() == "проверен"]


def get_sitter_any(sitter_id):
    for s in _get_records(config.SHEET_SITTERS):
        if str(s.get("id", "")).strip() == sitter_id:
            return s
    return None


def next_sitter_id():
    records = _get_records(config.SHEET_SITTERS)
    return f"SIT-{len(records) + 1:03d}"


def add_sitter(row):
    _append_row(config.SHEET_SITTERS, row)


def update_sitter_status(sitter_id, status):
    return _update_fields(config.SHEET_SITTERS, sitter_id, {"статус": status})


# ---------- Передержка: заявки ----------

def next_boarding_id():
    records = _get_records(config.SHEET_BOARDING)
    return f"BRD-{len(records) + 1:03d}"


def add_boarding(row):
    _append_row(config.SHEET_BOARDING, row)


def get_boarding(brd_id):
    for r in _get_records(config.SHEET_BOARDING):
        if str(r.get("id", "")).strip() == brd_id:
            return r
    return None


def update_boarding_status(brd_id, status):
    return _update_fields(config.SHEET_BOARDING, brd_id, {"статус": status})


# ---------- Знакомства питомцев ----------

def get_friend_profiles(goal=None):
    """Одобренные анкеты; goal: 'дружба' | 'вязка' | None (все).

    Анкеты с целью «обе» попадают в обе выборки.
    """
    profiles = _get_records(config.SHEET_FRIENDS)
    result = []
    for p in profiles:
        if str(p.get("статус", "")).strip() != "проверен":
            continue
        p_goal = str(p.get("цель", "")).strip()
        if goal and p_goal != goal and p_goal != "обе":
            continue
        result.append(p)
    return result


def get_friend_any(profile_id):
    for p in _get_records(config.SHEET_FRIENDS):
        if str(p.get("id", "")).strip() == profile_id:
            return p
    return None


def get_friend_by_tg(tg_id):
    """Одобренная анкета пользователя (для «предложить знакомство»)."""
    for p in _get_records(config.SHEET_FRIENDS):
        if (str(p.get("tg_id", "")).strip() == str(tg_id)
                and str(p.get("статус", "")).strip() == "проверен"):
            return p
    return None


def next_friend_id():
    records = _get_records(config.SHEET_FRIENDS)
    return f"FRD-{len(records) + 1:03d}"


def add_friend(row):
    _append_row(config.SHEET_FRIENDS, row)


def update_friend_status(profile_id, status):
    return _update_fields(config.SHEET_FRIENDS, profile_id, {"статус": status})


def next_match_id():
    records = _get_records(config.SHEET_MATCHES)
    return f"MTC-{len(records) + 1:03d}"


def add_match(row):
    _append_row(config.SHEET_MATCHES, row)


def get_match(match_id):
    for m in _get_records(config.SHEET_MATCHES):
        if str(m.get("id", "")).strip() == match_id:
            return m
    return None


def update_match_status(match_id, status):
    return _update_fields(config.SHEET_MATCHES, match_id, {"статус": status})
