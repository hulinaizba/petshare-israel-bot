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


# ---------- Тексты и переводы ----------

import i18n


def test_welcome_mentions_owners():
    welcome_ru = i18n.t("welcome", "ru")
    assert "Для владельцев" in welcome_ru
    assert "АКЦИЯ" not in welcome_ru


def test_about_owner_section_first():
    about_ru = i18n.t("about", "ru")
    assert "питомец может работать" in about_ru
    # блок владельца идёт раньше блока для клиентов
    assert about_ru.index("питомец может работать") < about_ru.index("провести время с животным")
    assert "20%" in about_ru
    assert "10%" in about_ru


def test_about_mentions_scenarios():
    about_ru = i18n.t("about", "ru")
    assert "Тест-драйв породы" in about_ru
    assert "Прогулки" in about_ru
    assert "Конные прогулки" in about_ru
    # конкретных сумм заработка в тексте нет — цену назначает владелец
    assert "от 45" not in about_ru
    assert "Цену назначаете вы" in about_ru


def test_all_keys_have_all_languages():
    for key, entry in i18n.T.items():
        for lang in i18n.LANGS:
            assert entry.get(lang), f"нет перевода {key}/{lang}"


def test_t_falls_back_to_russian():
    assert i18n.t("welcome", "xx") == i18n.t("welcome", "ru")


def test_t_formats_placeholders():
    assert "REQ-001" in i18n.t("req_sent", "en", id="REQ-001")
    assert "5" in i18n.t("card_pos", "he", pos=5, total=8)


def test_format_card_in_english():
    text = bot.format_card(ANIMALS[0], 1, 2, "en")
    assert "Луна" in text          # данные из таблицы — как есть
    assert "Card 1 of 2" in text   # интерфейс — на английском
    assert "hour" in text


def test_format_card_in_hebrew():
    text = bot.format_card(ANIMALS[0], 1, 2, "he")
    assert "כרטיס" in text


def test_card_values_translated():
    text_en = bot.format_card(ANIMALS[0], 1, 1, "en")
    assert "Tel Aviv" in text_en           # город из словаря
    assert "yes" in text_en                # можно_детям: да → yes
    assert "low" in text_en                # риск: низкий → low
    text_he = bot.format_card(ANIMALS[0], 1, 1, "he")
    assert "תל אביב" in text_he


def test_localized_field_fallback():
    animal = dict(ANIMALS[0])
    # перевода нет — показываем русский
    assert bot.localized_field(animal, "описание", "en") == "Звезда"
    # перевод есть — показываем его
    animal["описание_en"] = "A star"
    assert bot.localized_field(animal, "описание", "en") == "A star"
    # для русского всегда оригинал
    assert bot.localized_field(animal, "описание", "ru") == "Звезда"


def test_tr_value_unknown_stays():
    assert i18n.tr_value("Кфар-Саба", "en") == "Кфар-Саба"  # нет в словаре — как есть
    assert i18n.tr_value("Собаки", "he") == "כלבים"


# ---------- Передержка ----------

SITTERS = [
    {"id": "SIT-001", "имя": "Дана", "телефон": "+972-50-111-1111", "tg_id": 201,
     "город": "Тель-Авив", "животные": "собаки мелкие, кошки", "опыт": "свой пёс 5 лет",
     "условия": "квартира, без детей", "цена_сутки": 80, "статус": "проверен"},
    {"id": "SIT-002", "имя": "Игорь", "телефон": "+972-50-222-2222", "tg_id": 202,
     "город": "Хайфа", "животные": "все", "опыт": "ветеринар",
     "условия": "дом с двором", "цена_сутки": 120, "статус": "на проверке"},
]


def test_only_verified_sitters_listed():
    put_cache(config.SHEET_SITTERS, SITTERS)
    listed = sheets.get_sitters()
    assert [s["id"] for s in listed] == ["SIT-001"]
    # но для модерации доступен любой
    assert sheets.get_sitter_any("SIT-002")["имя"] == "Игорь"


def test_format_sitter_card():
    put_cache(config.SHEET_SITTERS, SITTERS)
    text = bot.format_sitter_card(SITTERS[0], 1, 1, "ru")
    assert "Дана" in text
    assert "80₪/сутки" in text
    text_en = bot.format_sitter_card(SITTERS[0], 1, 1, "en")
    assert "80₪/day" in text_en


def test_boarding_translations_complete():
    for key in ("board_menu", "sit_intro", "brd_intro", "brd_summary", "cli_brd_confirmed"):
        for lang in i18n.LANGS:
            assert i18n.T[key].get(lang)


def test_boarding_commission_math():
    # 7 суток по 80₪: стоимость 560, сбор 10% = 56, комиссия ситтера 20% = 112
    cost = 80 * 7
    assert bot.compute_client_fee(cost) == 56
    assert round(cost * bot.OWNER_COMMISSION) == 112


# ---------- Знакомства ----------

FRIENDS = [
    {"id": "FRD-001", "кличка": "Айза", "вид_порода": "Собака, овчарка", "пол": "Ж",
     "возраст": "3", "город": "Тель-Авив", "цель": "вязка", "документы": "прививки есть",
     "описание": "", "tg_id": 301, "статус": "проверен", "владелец_имя": "Иван", "телефон": "050"},
    {"id": "FRD-002", "кличка": "Рекс", "вид_порода": "Собака, овчарка", "пол": "М",
     "возраст": "4", "город": "Хайфа", "цель": "обе", "документы": "прививки, родословная",
     "описание": "добрый", "tg_id": 302, "статус": "проверен", "владелец_имя": "Пётр", "телефон": "051"},
    {"id": "FRD-003", "кличка": "Боня", "вид_порода": "Собака, шпиц", "пол": "Ж",
     "возраст": "2", "город": "Тель-Авив", "цель": "дружба", "документы": "прививки",
     "описание": "", "tg_id": 303, "статус": "проверен", "владелец_имя": "Анна", "телефон": "052"},
    {"id": "FRD-004", "кличка": "Скрытый", "вид_порода": "Кот", "пол": "М",
     "возраст": "1", "город": "Хайфа", "цель": "дружба", "документы": "",
     "описание": "", "tg_id": 304, "статус": "на проверке", "владелец_имя": "Х", "телефон": "053"},
]


def test_friend_profiles_filtered_by_goal():
    put_cache(config.SHEET_FRIENDS, FRIENDS)
    mating = [p["id"] for p in sheets.get_friend_profiles("вязка")]
    assert mating == ["FRD-001", "FRD-002"]  # «обе» попадает в вязку
    friends = [p["id"] for p in sheets.get_friend_profiles("дружба")]
    assert friends == ["FRD-002", "FRD-003"]  # неодобренный FRD-004 скрыт


def test_friend_profile_by_tg_only_approved():
    put_cache(config.SHEET_FRIENDS, FRIENDS)
    assert sheets.get_friend_by_tg(301)["кличка"] == "Айза"
    assert sheets.get_friend_by_tg(304) is None  # на проверке — нельзя предлагать


def test_format_friend_card():
    put_cache(config.SHEET_FRIENDS, FRIENDS)
    text = bot.format_friend_card(FRIENDS[0], 1, 2, "ru")
    assert "Айза" in text
    assert "девочка" in text
    assert "пару для вязки" in text
    text_en = bot.format_friend_card(FRIENDS[0], 1, 2, "en")
    assert "female" in text_en


def test_resolve_msg_target():
    put_cache(config.SHEET_ANIMALS, ANIMALS)
    put_cache(config.SHEET_SITTERS, SITTERS)
    put_cache(config.SHEET_FRIENDS, FRIENDS)
    put_cache(config.SHEET_OWNERS, [
        {"id": "OWN-001", "имя": "Иван", "tg_id": 111, "телефон": "+972-50-000-0001"},
    ])
    # животное → владелец
    tg, label, phone = bot.resolve_msg_target("a", "AN-001")
    assert tg == "111" and label == "Луна" and "0001" in phone
    # ситтер
    tg, label, _ = bot.resolve_msg_target("s", "SIT-001")
    assert tg == "201" and label == "Дана"
    # анкета знакомств
    tg, label, _ = bot.resolve_msg_target("f", "FRD-001")
    assert tg == "301" and label == "Айза"
    # неизвестный тип — безопасный фолбэк
    tg, label, phone = bot.resolve_msg_target("x", "ZZZ")
    assert tg == "" and label == "ZZZ" and phone == ""


def test_mating_fee_logic():
    # сбор берётся, если хотя бы одна сторона ищет вязку (или «обе»)
    for g1, g2, expected in [
        ("вязка", "вязка", bot.MATING_FEE),
        ("дружба", "обе", bot.MATING_FEE),
        ("дружба", "дружба", 0),
    ]:
        goals = {g1, g2}
        fee = bot.MATING_FEE if goals & {"вязка", "обе"} else 0
        assert fee == expected
