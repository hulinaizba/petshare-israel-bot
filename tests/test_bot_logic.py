"""Тесты чистой логики бота: цены, комиссии, фильтры, карточки, ссылки."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bot
import config
import sheets


class FakeContext:
    def __init__(self, user_data=None):
        self.user_data = user_data or {}


ANIMALS = [
    {"id": "AN-001", "имя": "Луна", "категория": "Собаки", "порода": "Шпиц",
     "город": "Тель-Авив", "цена_час": 60, "цена_событие": 250,
     "можно_детям": "да", "уровень_риска": "низкий", "активна": "да",
     "темперамент": "дружелюбная", "навыки": "фото", "возраст": 2,
     "сопровождение_владельца": "нет", "описание": "Звезда", "владелец_id": "OWN-001"},
    {"id": "AN-002", "имя": "Омар", "категория": "Экзотика и ферма", "порода": "Верблюд",
     "город": "Юг", "цена_час": 400, "цена_событие": 1500,
     "можно_детям": "нет", "уровень_риска": "высокий", "активна": "да",
     "темперамент": "спокойный", "навыки": "фото", "возраст": 9,
     "сопровождение_владельца": "да", "описание": "", "владелец_id": "OWN-002"},
    {"id": "AN-003", "имя": "Скрытый", "категория": "Собаки", "порода": "Дог",
     "город": "Тель-Авив", "цена_час": 50, "цена_событие": 200,
     "можно_детям": "да", "уровень_риска": "низкий", "активна": "нет",
     "темперамент": "", "навыки": "", "возраст": 1,
     "сопровождение_владельца": "нет", "описание": "", "владелец_id": "OWN-001"},
]

REQUESTS = [
    {"id": "REQ-001", "клиент_tg_id": 111, "статус": "новая"},
]


def put_cache(sheet_name, records):
    sheets._cache[sheet_name] = (time.time(), records)


def setup_function(_):
    sheets.clear_cache()
    put_cache(config.SHEET_ANIMALS, ANIMALS)
    put_cache(config.SHEET_REQUESTS, REQUESTS)


# ---------- Цены и комиссии ----------

def test_parse_price():
    assert bot.parse_price("250") == 250
    assert bot.parse_price(" 60 ") == 60
    assert bot.parse_price("дорого") == 0
    assert bot.parse_price(None) == 0


def test_client_fee():
    assert bot.compute_client_fee(250) == 25


def test_owner_commission_rate():
    assert round(250 * bot.OWNER_COMMISSION) == 50


# ---------- WhatsApp ----------

def test_whatsapp_link():
    assert bot.whatsapp_link("+972-50-000-0001") == "https://wa.me/972500000001"
    assert bot.whatsapp_link("") == ""
    assert bot.whatsapp_link("нет") == ""


# ---------- Каталог и фильтры ----------

def test_inactive_animals_hidden():
    ids = [a["id"] for a in sheets.get_animals()]
    assert "AN-003" not in ids
    assert len(ids) == 2


def test_get_animal_by_id_only_active():
    assert sheets.get_animal_by_id("AN-001")["имя"] == "Луна"
    assert sheets.get_animal_by_id("AN-003") is None
    assert sheets.get_animal_any("AN-003")["имя"] == "Скрытый"


def test_filter_by_city():
    ctx = FakeContext({"filt_city": "Тель-Авив"})
    result = bot.apply_filters(sheets.get_animals(), bot.get_filters(ctx))
    assert [a["id"] for a in result] == ["AN-001"]


def test_filter_by_price_low():
    ctx = FakeContext({"filt_price": "low"})
    result = bot.apply_filters(sheets.get_animals(), bot.get_filters(ctx))
    assert [a["id"] for a in result] == ["AN-001"]


def test_filter_by_kids():
    ctx = FakeContext({"filt_kids": "да"})
    result = bot.apply_filters(sheets.get_animals(), bot.get_filters(ctx))
    assert [a["id"] for a in result] == ["AN-001"]


def test_filters_empty_result():
    ctx = FakeContext({"filt_city": "Хайфа"})
    result = bot.apply_filters(sheets.get_animals(), bot.get_filters(ctx))
    assert result == []


def test_no_filters_returns_all_active():
    ctx = FakeContext()
    result = bot.apply_filters(sheets.get_animals(), bot.get_filters(ctx))
    assert len(result) == 2


# ---------- Карточка ----------

def test_format_card_contains_key_fields():
    text = bot.format_card(ANIMALS[0], 1, 2)
    assert "Луна" in text
    assert "Тель-Авив" in text
    assert "60₪/час" in text
    assert "Карточка 1 из 2" in text


def test_format_card_accompaniment_shown():
    text = bot.format_card(ANIMALS[1], 1, 1)
    assert "сопровождением владельца" in text


def test_format_card_no_accompaniment_for_safe():
    text = bot.format_card(ANIMALS[0], 1, 1)
    assert "сопровождением владельца" not in text


# ---------- Приветствие ----------

def test_welcome_mentions_owners():
    assert "Для владельцев" in bot.WELCOME_TEXT
    assert "АКЦИЯ" not in bot.WELCOME_TEXT
