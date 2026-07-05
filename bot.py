"""Telegram-бот PetShare Israel: каталог животных и заявки на аренду.

Интерфейс: русский / английский / иврит (i18n.py).
Запуск: ./venv/bin/python bot.py
"""

import logging
from datetime import datetime

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

import config
import sheets
from i18n import LANGS, t

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log", encoding="utf-8")],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CATEGORY_EMOJI = {
    "Собаки": "🐕",
    "Кошки": "🐈",
    "Птицы": "🦜",
    "Грызуны и кролики": "🐇",
    "Экзотика и ферма": "🦙",
}

RISK_EMOJI = {"низкий": "🟢", "средний": "🟡", "высокий": "🔴"}

# Комиссии платформы
OWNER_COMMISSION = 0.20   # 20% с владельца
CLIENT_FEE = 0.10         # 10% сервисный сбор с клиента

# Состояния сценария заявки
REQ_DATE, REQ_PHONE, REQ_CONFIRM = range(3)

# Состояния анкеты владельца
(
    OWN_NAME, OWN_PHONE, OWN_CITY, PET_NAME, PET_CATEGORY, PET_CATEGORY_CUSTOM,
    PET_BREED, PET_AGE, PET_TEMPERAMENT, PET_SKILLS, PET_KIDS,
    PET_PRICE_HOUR, PET_PRICE_EVENT, PET_PHOTO, PET_CONFIRM,
) = range(10, 25)

# Состояния анкеты пет-ситтера
(
    SIT_NAME, SIT_PHONE, SIT_CITY, SIT_ANIMALS, SIT_EXP,
    SIT_COND, SIT_PRICE, SIT_CONFIRM,
) = range(30, 38)

# Состояния заявки на передержку
BRD_PET, BRD_DATES, BRD_CITY, BRD_NOTES, BRD_PHONE, BRD_CONFIRM = range(40, 46)


def L(context):
    """Язык текущего пользователя."""
    return context.user_data.get("lang", "ru")


def user_lang(context, tg_id):
    """Язык другого пользователя по его id (для уведомлений)."""
    try:
        return context.application.user_data.get(int(tg_id), {}).get("lang", "ru")
    except (ValueError, TypeError):
        return "ru"


def parse_price(value):
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return 0


def whatsapp_link(phone):
    """Превращает номер в ссылку wa.me (оставляет только цифры)."""
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    return f"https://wa.me/{digits}" if digits else ""


def compute_client_fee(price):
    """Сервисный сбор клиента."""
    return round(price * CLIENT_FEE)


def language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"lang_set:{code}")]
        for code, label in LANGS.items()
    ])


def main_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_catalog", lang), callback_data="catalog")],
        [InlineKeyboardButton(t("btn_filters", lang), callback_data="filters")],
        [InlineKeyboardButton(t("btn_owner", lang), callback_data="owner_start")],
        [InlineKeyboardButton(t("btn_boarding", lang), callback_data="board_menu")],
        [InlineKeyboardButton(t("btn_about", lang), callback_data="about")],
        [InlineKeyboardButton(t("btn_lang", lang), callback_data="lang")],
    ])


def board_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_give_pet", lang), callback_data="brdreq:")],
        [InlineKeyboardButton(t("btn_be_sitter", lang), callback_data="sitter_form")],
        [InlineKeyboardButton(t("btn_sitters_list", lang), callback_data="sitcard:0")],
        [InlineKeyboardButton(t("btn_menu", lang), callback_data="menu")],
    ])


def format_sitter_card(sitter, position, total, lang):
    return "\n".join([
        f"🤝 <b>{sitter.get('имя', '')}</b> — 📍 {sitter.get('город', '')}",
        "",
        f"🐾 {t('sit_card_takes', lang)}: {sitter.get('животные', '')}",
        f"⭐ {t('sit_card_exp', lang)}: {sitter.get('опыт', '')}",
        f"🏠 {t('sit_card_cond', lang)}: {sitter.get('условия', '')}",
        f"💰 {sitter.get('цена_сутки', '')}₪/{t('sit_card_day', lang)}",
        "",
        t("card_pos", lang, pos=position, total=total),
    ])


def about_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_fill_form", lang), callback_data="owner_start")],
        [InlineKeyboardButton(t("btn_open_catalog", lang), callback_data="catalog")],
        [InlineKeyboardButton(t("btn_menu", lang), callback_data="menu")],
    ])


def catalog_keyboard(lang):
    """Клавиатура выбора категории; None — если каталог пуст."""
    categories = sheets.get_categories()
    if not categories:
        return None
    rows = [
        [InlineKeyboardButton(
            f"{CATEGORY_EMOJI.get(cat, '🐾')} {cat}",
            callback_data=f"card:{cat}:0",
        )]
        for cat in categories
    ]
    rows.append([InlineKeyboardButton(t("btn_menu", lang), callback_data="menu")])
    return InlineKeyboardMarkup(rows)


# ---------- Фильтры ----------

PRICE_CHECKS = {
    "any": None,
    "low": lambda p: p <= 100,
    "high": lambda p: p > 100,
}


def get_filters(context):
    """Текущие фильтры пользователя (по умолчанию — всё)."""
    return {
        "city": context.user_data.get("filt_city", "any"),
        "price": context.user_data.get("filt_price", "any"),
        "kids": context.user_data.get("filt_kids", "any"),
    }


def apply_filters(animals, filt):
    result = []
    for a in animals:
        if filt["city"] != "any" and str(a.get("город", "")).strip() != filt["city"]:
            continue
        price_check = PRICE_CHECKS[filt["price"]]
        if price_check and not price_check(parse_price(a.get("цена_час"))):
            continue
        if filt["kids"] == "да" and str(a.get("можно_детям", "")).strip().lower() != "да":
            continue
        result.append(a)
    return result


def filter_menu(context):
    """Текст и клавиатура экрана фильтров."""
    lang = L(context)
    filt = get_filters(context)
    city_label = t("any_city", lang) if filt["city"] == "any" else filt["city"]
    price_label = t(f"price_{filt['price']}", lang)
    kids_label = t("kids_any", lang) if filt["kids"] == "any" else t("kids_only_yes", lang)
    count = len(apply_filters(sheets.get_animals(), filt))
    text = (
        f"{t('flt_title', lang)}\n\n"
        f"{t('flt_city', lang)}: <b>{city_label}</b>\n"
        f"{t('flt_price', lang)}: <b>{price_label}</b>\n"
        f"{t('flt_kids', lang)}: <b>{kids_label}</b>\n\n"
        f"{t('flt_found', lang, count=count)}"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_flt_city", lang), callback_data="f_city")],
        [InlineKeyboardButton(t("btn_flt_price", lang), callback_data="f_price")],
        [InlineKeyboardButton(t("btn_flt_kids", lang), callback_data="f_kids")],
        [InlineKeyboardButton(t("btn_flt_show", lang, count=count), callback_data="fcard:0")],
        [
            InlineKeyboardButton(t("btn_flt_reset", lang), callback_data="f_reset"),
            InlineKeyboardButton(t("btn_menu", lang), callback_data="menu"),
        ],
    ])
    return text, keyboard


def format_card(animal, position, total, lang="ru"):
    """Собирает текст карточки животного."""
    risk = str(animal.get("уровень_риска", "")).strip()
    lines = [
        f"🐾 <b>{animal.get('имя', '')}</b> — {animal.get('порода', '')}",
        "",
        f"📍 {animal.get('город', '')}   |   {t('card_age', lang)}: {animal.get('возраст', '')}",
        f"💰 {animal.get('цена_час', '')}₪/{t('card_hour', lang)}   |   "
        f"{animal.get('цена_событие', '')}₪/{t('card_event', lang)}",
        f"😊 {t('card_character', lang)}: {animal.get('темперамент', '')}",
        f"⭐ {t('card_skills', lang)}: {animal.get('навыки', '')}",
        f"{RISK_EMOJI.get(risk, '⚪')} {t('card_risk', lang)}: {risk}",
        f"👶 {t('card_kids', lang)}: {animal.get('можно_детям', '')}",
    ]
    if str(animal.get("сопровождение_владельца", "")).strip().lower() == "да":
        lines.append(t("card_accompany", lang))
    description = str(animal.get("описание", "")).strip()
    if description:
        lines += ["", f"<i>{description}</i>"]
    lines += ["", t("card_pos", lang, pos=position, total=total)]
    return "\n".join(lines)


def card_keyboard(category, index, total, animal_id, lang):
    """Кнопки под карточкой: листание и заявка."""
    nav = []
    if total > 1:
        prev_i = (index - 1) % total
        next_i = (index + 1) % total
        nav = [
            InlineKeyboardButton("◀️", callback_data=f"card:{category}:{prev_i}"),
            InlineKeyboardButton(f"{index + 1}/{total}", callback_data="noop"),
            InlineKeyboardButton("▶️", callback_data=f"card:{category}:{next_i}"),
        ]
    rows = []
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(t("btn_request", lang), callback_data=f"request:{animal_id}")])
    rows.append([
        InlineKeyboardButton(t("btn_categories", lang), callback_data="catalog"),
        InlineKeyboardButton(t("btn_menu", lang), callback_data="menu"),
    ])
    return InlineKeyboardMarkup(rows)


# ---------- Команды ----------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "lang" not in context.user_data:
        await update.message.reply_text(
            t("choose_lang_first", "ru"),
            reply_markup=language_keyboard(),
            parse_mode="HTML",
        )
        return
    lang = L(context)
    await update.message.reply_text(
        t("welcome", lang), reply_markup=main_menu_keyboard(lang), parse_mode="HTML"
    )


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        t("choose_lang", L(context)), reply_markup=language_keyboard()
    )


async def cmd_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    keyboard = catalog_keyboard(lang)
    if keyboard is None:
        await update.message.reply_text(t("catalog_empty", lang))
        return
    await update.message.reply_text(t("choose_category", lang), reply_markup=keyboard)


async def cmd_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = filter_menu(context)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    await update.message.reply_text(
        t("about", lang), reply_markup=about_keyboard(lang), parse_mode="HTML"
    )


async def cmd_boarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    await update.message.reply_text(
        t("board_menu", lang), reply_markup=board_menu_keyboard(lang), parse_mode="HTML"
    )


async def cmd_reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс кэша таблицы (только для администратора)."""
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        return
    sheets.clear_cache()
    await update.message.reply_text("♻️ Кэш сброшен, данные перечитаются из таблицы.")


# ---------- Кнопки (общий обработчик) ----------

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    lang = L(context)
    await query.answer()

    if data == "noop":
        return

    if data == "lang":
        await query.edit_message_text(
            t("choose_lang", lang), reply_markup=language_keyboard()
        )
        return

    if data.startswith("lang_set:"):
        new_lang = data.split(":", 1)[1]
        context.user_data["lang"] = new_lang
        await query.edit_message_text(t("lang_set", new_lang))
        await query.message.reply_text(
            t("welcome", new_lang),
            reply_markup=main_menu_keyboard(new_lang),
            parse_mode="HTML",
        )
        return

    if data == "menu":
        await query.edit_message_text(
            t("menu_short", lang), reply_markup=main_menu_keyboard(lang), parse_mode="HTML"
        )
        return

    if data == "about":
        await query.edit_message_text(
            t("about", lang), reply_markup=about_keyboard(lang), parse_mode="HTML"
        )
        return

    if data == "board_menu":
        await query.edit_message_text(
            t("board_menu", lang), reply_markup=board_menu_keyboard(lang), parse_mode="HTML"
        )
        return

    if data.startswith("sitcard:"):
        sitters = sheets.get_sitters()
        if not sitters:
            await query.edit_message_text(
                t("sitters_empty", lang), reply_markup=board_menu_keyboard(lang)
            )
            return
        index = int(data.split(":", 1)[1]) % len(sitters)
        sitter = sitters[index]
        total = len(sitters)
        rows = []
        if total > 1:
            rows.append([
                InlineKeyboardButton("◀️", callback_data=f"sitcard:{(index - 1) % total}"),
                InlineKeyboardButton(f"{index + 1}/{total}", callback_data="noop"),
                InlineKeyboardButton("▶️", callback_data=f"sitcard:{(index + 1) % total}"),
            ])
        rows.append([InlineKeyboardButton(
            t("btn_request_sitter", lang), callback_data=f"brdreq:{sitter.get('id', '')}"
        )])
        rows.append([
            InlineKeyboardButton(t("btn_boarding", lang), callback_data="board_menu"),
            InlineKeyboardButton(t("btn_menu", lang), callback_data="menu"),
        ])
        await query.edit_message_text(
            format_sitter_card(sitter, index + 1, total, lang),
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="HTML",
        )
        return

    if data == "catalog":
        keyboard = catalog_keyboard(lang)
        if keyboard is None:
            await query.edit_message_text(t("catalog_empty", lang))
            return
        await query.edit_message_text(t("choose_category", lang), reply_markup=keyboard)
        return

    if data.startswith("card:"):
        _, category, index_str = data.split(":", 2)
        animals = sheets.get_animals_by_category(category)
        if not animals:
            await query.edit_message_text(t("category_empty", lang))
            return
        index = int(index_str) % len(animals)
        animal = animals[index]
        await query.edit_message_text(
            format_card(animal, index + 1, len(animals), lang),
            reply_markup=card_keyboard(category, index, len(animals), animal.get("id", ""), lang),
            parse_mode="HTML",
        )
        return

    # --- Экраны фильтров ---

    if data == "filters" or data == "f_reset":
        if data == "f_reset":
            for key in ("filt_city", "filt_price", "filt_kids"):
                context.user_data.pop(key, None)
        text, keyboard = filter_menu(context)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data == "f_city":
        cities = []
        for a in sheets.get_animals():
            city = str(a.get("город", "")).strip()
            if city and city not in cities:
                cities.append(city)
        rows = [[InlineKeyboardButton(t("any_city_btn", lang), callback_data="f_city_set:any")]]
        rows += [
            [InlineKeyboardButton(f"📍 {c}", callback_data=f"f_city_set:{c}")]
            for c in sorted(cities)
        ]
        await query.edit_message_text(
            t("choose_city_txt", lang), reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("f_city_set:"):
        context.user_data["filt_city"] = data.split(":", 1)[1]
        text, keyboard = filter_menu(context)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data == "f_price":
        rows = [
            [InlineKeyboardButton(t(f"price_{key}", lang), callback_data=f"f_price_set:{key}")]
            for key in PRICE_CHECKS
        ]
        await query.edit_message_text(
            t("choose_price_txt", lang), reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("f_price_set:"):
        context.user_data["filt_price"] = data.split(":", 1)[1]
        text, keyboard = filter_menu(context)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data == "f_kids":
        current = context.user_data.get("filt_kids", "any")
        context.user_data["filt_kids"] = "да" if current == "any" else "any"
        text, keyboard = filter_menu(context)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data.startswith("fcard:"):
        animals = apply_filters(sheets.get_animals(), get_filters(context))
        if not animals:
            text, keyboard = filter_menu(context)
            await query.edit_message_text(
                t("flt_none", lang) + "\n\n" + text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
            return
        index = int(data.split(":", 1)[1]) % len(animals)
        animal = animals[index]
        total = len(animals)
        rows = []
        if total > 1:
            rows.append([
                InlineKeyboardButton("◀️", callback_data=f"fcard:{(index - 1) % total}"),
                InlineKeyboardButton(f"{index + 1}/{total}", callback_data="noop"),
                InlineKeyboardButton("▶️", callback_data=f"fcard:{(index + 1) % total}"),
            ])
        rows.append([InlineKeyboardButton(
            t("btn_request", lang), callback_data=f"request:{animal.get('id', '')}"
        )])
        rows.append([
            InlineKeyboardButton(t("btn_flt_back", lang), callback_data="filters"),
            InlineKeyboardButton(t("btn_menu", lang), callback_data="menu"),
        ])
        await query.edit_message_text(
            format_card(animal, index + 1, total, lang),
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="HTML",
        )
        return


# ---------- Сценарий заявки ----------

async def request_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Клиент нажал «Оставить заявку» под карточкой."""
    query = update.callback_query
    lang = L(context)
    await query.answer()
    animal_id = query.data.split(":", 1)[1]
    animal = sheets.get_animal_by_id(animal_id)
    if not animal:
        await query.message.reply_text(t("req_unavailable", lang))
        return ConversationHandler.END
    context.user_data["req_animal"] = animal
    await query.message.reply_text(
        t("req_intro", lang, name=animal.get("имя", "")), parse_mode="HTML"
    )
    return REQ_DATE


async def request_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    context.user_data["req_date"] = update.message.text.strip()
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(t("btn_send_phone", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(t("req_ask_phone", lang), reply_markup=keyboard)
    return REQ_PHONE


async def request_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
    context.user_data["req_phone"] = phone

    animal = context.user_data["req_animal"]
    price = parse_price(animal.get("цена_событие"))
    client_fee = compute_client_fee(price)
    total = price + client_fee

    summary = t(
        "req_summary", lang,
        name=animal.get("имя", ""), breed=animal.get("порода", ""),
        date=context.user_data["req_date"], phone=phone,
        price=price, fee=client_fee, total=total,
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_req_send", lang), callback_data="req_confirm")],
        [InlineKeyboardButton(t("btn_req_cancel", lang), callback_data="req_cancel")],
    ])
    await update.message.reply_text(summary, reply_markup=keyboard, parse_mode="HTML")
    # Убираем клавиатуру с кнопкой контакта
    await update.message.reply_text("👆", reply_markup=ReplyKeyboardRemove())
    return REQ_CONFIRM


async def request_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()

    if query.data == "req_cancel":
        await query.edit_message_text(t("req_cancelled", lang))
        for key in ("req_animal", "req_date", "req_phone"):
            context.user_data.pop(key, None)
        return ConversationHandler.END

    animal = context.user_data["req_animal"]
    user = update.effective_user
    price = parse_price(animal.get("цена_событие"))
    client_fee = compute_client_fee(price)
    owner_commission = round(price * OWNER_COMMISSION)
    platform_income = client_fee + owner_commission

    req_id = sheets.next_request_id()
    client_name = user.full_name + (f" (@{user.username})" if user.username else "")
    sheets.add_request([
        req_id,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        client_name,
        context.user_data["req_phone"],
        user.id,
        animal.get("id", ""),
        animal.get("имя", ""),
        context.user_data["req_date"],
        "новая",
        "",
        price,
        client_fee,
        owner_commission,
        platform_income,
    ])

    await query.edit_message_text(t("req_sent", lang, id=req_id), parse_mode="HTML")

    # Уведомление администратору (всегда на русском)
    owner = sheets.get_owner_by_id(str(animal.get("владелец_id", "")).strip()) or {}
    admin_text = (
        f"🔔 <b>Новая заявка {req_id}</b>\n\n"
        f"🐾 {animal.get('имя', '')} ({animal.get('порода', '')}, {animal.get('id', '')})\n"
        f"📅 Дата: {context.user_data['req_date']}\n"
        f"👤 Клиент: {client_name}\n"
        f"📱 Телефон: {context.user_data['req_phone']}\n\n"
        f"👨‍💼 Владелец: {owner.get('имя', '—')}, {owner.get('телефон', '—')}\n"
        f"💬 WhatsApp: {owner.get('whatsapp', '—')}\n\n"
        f"💰 Аренда: {price}₪\n"
        f"➕ Сбор с клиента (10%): {client_fee}₪\n"
        f"➖ Комиссия владельца (20%): {owner_commission}₪\n"
        f"<b>Доход платформы: {platform_income}₪</b>"
    )
    admin_rows = [[
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"adm_ok:{req_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"adm_no:{req_id}"),
    ]]
    owner_wa = whatsapp_link(owner.get("whatsapp", ""))
    if owner_wa:
        admin_rows.append([InlineKeyboardButton("💬 WhatsApp владельца", url=owner_wa)])
    try:
        await context.bot.send_message(
            config.ADMIN_CHAT_ID,
            admin_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(admin_rows),
        )
    except Exception:
        logger.exception("Не удалось отправить уведомление администратору")

    for key in ("req_animal", "req_date", "req_phone"):
        context.user_data.pop(key, None)
    return ConversationHandler.END


async def request_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for key in ("req_animal", "req_date", "req_phone"):
        context.user_data.pop(key, None)
    await update.message.reply_text(
        t("req_cancelled", L(context)), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Администратор нажал Подтвердить/Отклонить под заявкой."""
    query = update.callback_query
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        await query.answer("Эта кнопка только для администратора", show_alert=True)
        return
    await query.answer()

    action, req_id = query.data.split(":", 1)
    request = sheets.get_request(req_id)
    if not request:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"Заявка {req_id} не найдена в таблице.")
        return

    if action == "adm_ok":
        new_status, badge = "подтверждена", "✅ ПОДТВЕРЖДЕНА"
    else:
        new_status, badge = "отклонена", "❌ ОТКЛОНЕНА"
    sheets.update_request_status(req_id, new_status)

    # Убираем кнопки и помечаем решение в тексте уведомления
    await query.edit_message_text(
        query.message.text_html + f"\n\n<b>{badge}</b>",
        parse_mode="HTML",
    )

    # Сообщаем клиенту на его языке
    client_id = str(request.get("клиент_tg_id", "")).strip()
    if not client_id.isdigit():
        return
    cli_lang = user_lang(context, client_id)
    animal = sheets.get_animal_by_id(str(request.get("животное_id", "")).strip()) or {}
    owner = sheets.get_owner_by_id(str(animal.get("владелец_id", "")).strip()) or {}
    try:
        if action == "adm_ok":
            keyboard = None
            owner_wa = whatsapp_link(owner.get("whatsapp", ""))
            if owner_wa:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(t("btn_wa_owner", cli_lang), url=owner_wa)]]
                )
            await context.bot.send_message(
                int(client_id),
                t("cli_confirmed", cli_lang, id=req_id,
                  animal=request.get("животное_имя", ""), date=request.get("дата_аренды", "")),
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            await context.bot.send_message(
                int(client_id),
                t("cli_declined", cli_lang, id=req_id),
                parse_mode="HTML",
            )
    except Exception:
        logger.exception("Не удалось уведомить клиента по заявке %s", req_id)


# ---------- Анкета владельца («сдать питомца в аренду») ----------

async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["owner_flow"] = {}
    await query.message.reply_text(t("own_intro", L(context)), parse_mode="HTML")
    return OWN_NAME


async def owner_start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вход в анкету командой /owner."""
    context.user_data["owner_flow"] = {}
    await update.message.reply_text(t("own_intro", L(context)), parse_mode="HTML")
    return OWN_NAME


async def owner_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["name"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_phone", L(context)))
    return OWN_PHONE


async def owner_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["phone"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_city", L(context)))
    return OWN_CITY


async def owner_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["city"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_petname", L(context)))
    return PET_NAME


async def pet_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    context.user_data["owner_flow"]["pet_name"] = update.message.text.strip()
    rows = [
        [InlineKeyboardButton(f"{emoji} {cat}", callback_data=f"pc:{cat}")]
        for cat, emoji in CATEGORY_EMOJI.items()
    ]
    rows.append([InlineKeyboardButton(t("own_other_cat", lang), callback_data="pc:__custom__")])
    await update.message.reply_text(
        t("own_choose_cat", lang), reply_markup=InlineKeyboardMarkup(rows)
    )
    return PET_CATEGORY


async def pet_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()
    category = query.data.split(":", 1)[1]
    if category == "__custom__":
        await query.message.reply_text(t("own_ask_cat_text", lang))
        return PET_CATEGORY_CUSTOM
    context.user_data["owner_flow"]["category"] = category
    await query.message.reply_text(t("own_ask_breed", lang))
    return PET_BREED


async def pet_category_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["category"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_breed", L(context)))
    return PET_BREED


async def pet_breed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = [p.strip() for p in update.message.text.split(",", 1)]
    context.user_data["owner_flow"]["species"] = parts[0]
    context.user_data["owner_flow"]["breed"] = parts[1] if len(parts) > 1 else parts[0]
    await update.message.reply_text(t("own_ask_age", L(context)))
    return PET_AGE


async def pet_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["age"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_temper", L(context)))
    return PET_TEMPERAMENT


async def pet_temperament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["temperament"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_skills", L(context)))
    return PET_SKILLS


async def pet_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    context.user_data["owner_flow"]["skills"] = update.message.text.strip()
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_yes", lang), callback_data="kids:да"),
        InlineKeyboardButton(t("btn_no", lang), callback_data="kids:нет"),
    ]])
    await update.message.reply_text(t("own_ask_kids", lang), reply_markup=keyboard)
    return PET_KIDS


async def pet_kids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["owner_flow"]["kids"] = query.data.split(":", 1)[1]
    await query.message.reply_text(t("own_ask_price_hour", L(context)))
    return PET_PRICE_HOUR


async def pet_price_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["price_hour"] = parse_price(update.message.text)
    await update.message.reply_text(t("own_ask_price_event", L(context)))
    return PET_PRICE_EVENT


async def pet_price_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["price_event"] = parse_price(update.message.text)
    await update.message.reply_text(t("own_ask_photo", L(context)))
    return PET_PHOTO


async def pet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    flow = context.user_data["owner_flow"]
    flow["photo"] = update.message.photo[-1].file_id if update.message.photo else ""

    summary = t(
        "own_summary", lang,
        name=flow["name"], phone=flow["phone"], city=flow["city"],
        pet_name=flow["pet_name"], species=flow["species"], breed=flow["breed"],
        age=flow["age"], category=flow["category"], temperament=flow["temperament"],
        skills=flow["skills"], kids=flow["kids"],
        price_hour=flow["price_hour"], price_event=flow["price_event"],
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_own_send", lang), callback_data="pet_send")],
        [InlineKeyboardButton(t("btn_own_cancel", lang), callback_data="pet_cancel")],
    ])
    if flow["photo"]:
        await update.message.reply_photo(flow["photo"], caption=summary, reply_markup=keyboard)
    else:
        await update.message.reply_text(summary, reply_markup=keyboard)
    return PET_CONFIRM


async def pet_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()

    if query.data == "pet_cancel":
        await query.message.reply_text(t("own_cancelled", lang))
        context.user_data.pop("owner_flow", None)
        return ConversationHandler.END

    flow = context.user_data["owner_flow"]
    user = update.effective_user

    owner = sheets.get_owner_by_tg_id(user.id)
    if owner:
        owner_id = owner.get("id")
    else:
        owner_id = sheets.next_owner_id()
        sheets.add_owner([
            owner_id, flow["name"], flow["phone"], user.id, flow["city"],
            flow["phone"], "", "на проверке",
        ])

    animal_id = sheets.next_animal_id()
    sheets.add_animal([
        animal_id, flow["pet_name"], flow["category"], flow["species"], flow["breed"],
        flow["age"], flow["city"], flow["price_hour"], flow["price_event"],
        flow["temperament"], flow["skills"], flow["kids"], "не указан", "нет",
        flow["photo"], owner_id, "на проверке", "", "нет",
    ])
    sheets.append_owner_pet(owner_id, animal_id)

    await query.message.reply_text(t("own_sent", lang))

    # Уведомление администратору (всегда на русском)
    admin_text = (
        "🔔 <b>Новая анкета владельца</b>\n\n"
        f"👤 {flow['name']}, {flow['phone']}, {flow['city']} (владелец {owner_id})\n\n"
        f"🐾 {flow['pet_name']} — {flow['species']} ({flow['breed']}), {flow['age']} ({animal_id})\n"
        f"📂 Категория: {flow['category']}\n"
        f"😊 Характер: {flow['temperament']}\n"
        f"⭐ Умеет: {flow['skills']}\n"
        f"👶 Можно детям: {flow['kids']}\n"
        f"💰 {flow['price_hour']}₪/час, {flow['price_event']}₪/мероприятие\n\n"
        "⚠️ Проверьте документы (прививки, ветпаспорт) перед одобрением!"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Одобрить", callback_data=f"own_ok:{animal_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"own_no:{animal_id}"),
    ]])
    try:
        if flow["photo"]:
            await context.bot.send_photo(
                config.ADMIN_CHAT_ID, flow["photo"], caption=admin_text,
                parse_mode="HTML", reply_markup=keyboard,
            )
        else:
            await context.bot.send_message(
                config.ADMIN_CHAT_ID, admin_text, parse_mode="HTML", reply_markup=keyboard,
            )
    except Exception:
        logger.exception("Не удалось уведомить администратора об анкете владельца")

    context.user_data.pop("owner_flow", None)
    return ConversationHandler.END


async def owner_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("owner_flow", None)
    await update.message.reply_text(
        t("own_cancelled", L(context)), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def admin_owner_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Администратор одобряет/отклоняет анкету питомца."""
    query = update.callback_query
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        await query.answer("Эта кнопка только для администратора", show_alert=True)
        return
    await query.answer()

    action, animal_id = query.data.split(":", 1)
    animal = sheets.get_animal_any(animal_id)
    if not animal:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if action == "own_ok":
        sheets.update_animal_status(animal_id, "да", "проверено")
        badge = "✅ ОДОБРЕНО"
    else:
        sheets.update_animal_status(animal_id, "нет", "отклонено")
        badge = "❌ ОТКЛОНЕНО"

    if query.message.photo:
        await query.edit_message_caption(
            caption=query.message.caption_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
        )
    else:
        await query.edit_message_text(
            query.message.text_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
        )

    owner = sheets.get_owner_by_id(str(animal.get("владелец_id", "")).strip()) or {}
    owner_tg = str(owner.get("tg_id", "")).strip()
    if not owner_tg.isdigit():
        return
    own_lang = user_lang(context, owner_tg)
    try:
        if action == "own_ok":
            sheets.update_owner_status(owner.get("id", ""), "проверен")
            await context.bot.send_message(
                int(owner_tg), t("own_approved", own_lang, name=animal.get("имя", ""))
            )
        else:
            await context.bot.send_message(
                int(owner_tg), t("own_declined", own_lang, name=animal.get("имя", ""))
            )
    except Exception:
        logger.exception("Не удалось уведомить владельца %s", owner_tg)


# ---------- Анкета пет-ситтера ----------

async def sitter_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["sit_flow"] = {}
    await query.message.reply_text(t("sit_intro", L(context)), parse_mode="HTML")
    return SIT_NAME


async def sitter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sit_flow"]["name"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_phone", L(context)))
    return SIT_PHONE


async def sitter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sit_flow"]["phone"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_city", L(context)))
    return SIT_CITY


async def sitter_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sit_flow"]["city"] = update.message.text.strip()
    await update.message.reply_text(t("sit_ask_animals", L(context)))
    return SIT_ANIMALS


async def sitter_animals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sit_flow"]["animals"] = update.message.text.strip()
    await update.message.reply_text(t("sit_ask_exp", L(context)))
    return SIT_EXP


async def sitter_exp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sit_flow"]["exp"] = update.message.text.strip()
    await update.message.reply_text(t("sit_ask_cond", L(context)))
    return SIT_COND


async def sitter_cond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sit_flow"]["cond"] = update.message.text.strip()
    await update.message.reply_text(t("sit_ask_price", L(context)))
    return SIT_PRICE


async def sitter_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    flow = context.user_data["sit_flow"]
    flow["price"] = parse_price(update.message.text)
    summary = t(
        "sit_summary", lang,
        name=flow["name"], phone=flow["phone"], city=flow["city"],
        animals=flow["animals"], exp=flow["exp"], cond=flow["cond"], price=flow["price"],
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_own_send", lang), callback_data="sit_send")],
        [InlineKeyboardButton(t("btn_own_cancel", lang), callback_data="sit_cancel")],
    ])
    await update.message.reply_text(summary, reply_markup=keyboard)
    return SIT_CONFIRM


async def sitter_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()

    if query.data == "sit_cancel":
        await query.message.reply_text(t("own_cancelled", lang))
        context.user_data.pop("sit_flow", None)
        return ConversationHandler.END

    flow = context.user_data["sit_flow"]
    user = update.effective_user
    sitter_id = sheets.next_sitter_id()
    sheets.add_sitter([
        sitter_id, flow["name"], flow["phone"], user.id, flow["city"],
        flow["animals"], flow["exp"], flow["cond"], flow["price"],
        "на проверке", datetime.now().strftime("%d.%m.%Y %H:%M"),
    ])
    await query.message.reply_text(t("own_sent", lang))

    admin_text = (
        "🔔 <b>Новая анкета пет-ситтера</b>\n\n"
        f"👤 {flow['name']}, {flow['phone']}, {flow['city']} ({sitter_id})\n"
        f"🐾 Берёт: {flow['animals']}\n"
        f"⭐ Опыт: {flow['exp']}\n"
        f"🏠 Условия: {flow['cond']}\n"
        f"💰 {flow['price']}₪/сутки\n\n"
        "⚠️ Созвонитесь и проверьте условия перед одобрением!"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Одобрить", callback_data=f"sit_ok:{sitter_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"sit_no:{sitter_id}"),
    ]])
    try:
        await context.bot.send_message(
            config.ADMIN_CHAT_ID, admin_text, parse_mode="HTML", reply_markup=keyboard
        )
    except Exception:
        logger.exception("Не удалось уведомить администратора об анкете ситтера")

    context.user_data.pop("sit_flow", None)
    return ConversationHandler.END


async def sitter_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("sit_flow", None)
    await update.message.reply_text(
        t("own_cancelled", L(context)), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def admin_sitter_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Администратор одобряет/отклоняет анкету ситтера."""
    query = update.callback_query
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        await query.answer("Эта кнопка только для администратора", show_alert=True)
        return
    await query.answer()

    action, sitter_id = query.data.split(":", 1)
    sitter = sheets.get_sitter_any(sitter_id)
    if not sitter:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if action == "sit_ok":
        sheets.update_sitter_status(sitter_id, "проверен")
        badge = "✅ ОДОБРЕНО"
    else:
        sheets.update_sitter_status(sitter_id, "отклонён")
        badge = "❌ ОТКЛОНЕНО"
    await query.edit_message_text(
        query.message.text_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
    )

    sitter_tg = str(sitter.get("tg_id", "")).strip()
    if not sitter_tg.isdigit():
        return
    sit_lang = user_lang(context, sitter_tg)
    try:
        key = "sit_approved" if action == "sit_ok" else "sit_declined"
        await context.bot.send_message(int(sitter_tg), t(key, sit_lang))
    except Exception:
        logger.exception("Не удалось уведомить ситтера %s", sitter_tg)


# ---------- Заявка на передержку ----------

async def boarding_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()
    sitter_id = query.data.split(":", 1)[1]
    context.user_data["brd_flow"] = {"sitter_id": sitter_id}
    if sitter_id:
        sitter = sheets.get_sitter_any(sitter_id) or {}
        context.user_data["brd_flow"]["sitter_name"] = sitter.get("имя", "")
        text = t("brd_intro_sitter", lang, name=sitter.get("имя", ""))
    else:
        text = t("brd_intro", lang)
    await query.message.reply_text(text, parse_mode="HTML")
    return BRD_PET


async def boarding_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["brd_flow"]["pet"] = update.message.text.strip()
    await update.message.reply_text(t("brd_ask_dates", L(context)), parse_mode="HTML")
    return BRD_DATES


async def boarding_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["brd_flow"]["dates"] = update.message.text.strip()
    await update.message.reply_text(t("brd_ask_city", L(context)))
    return BRD_CITY


async def boarding_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["brd_flow"]["city"] = update.message.text.strip()
    await update.message.reply_text(t("brd_ask_notes", L(context)))
    return BRD_NOTES


async def boarding_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    context.user_data["brd_flow"]["notes"] = update.message.text.strip()
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(t("btn_send_phone", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(t("req_ask_phone", lang), reply_markup=keyboard)
    return BRD_PHONE


async def boarding_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    flow = context.user_data["brd_flow"]
    if update.message.contact:
        flow["phone"] = update.message.contact.phone_number
    else:
        flow["phone"] = update.message.text.strip()

    sitter_line = ""
    if flow.get("sitter_name"):
        sitter_line = t("brd_sitter_line", lang, name=flow["sitter_name"])
    summary = t(
        "brd_summary", lang,
        pet=flow["pet"], dates=flow["dates"], city=flow["city"],
        notes=flow["notes"], phone=flow["phone"], sitter_line=sitter_line,
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_req_send", lang), callback_data="brd_confirm")],
        [InlineKeyboardButton(t("btn_req_cancel", lang), callback_data="brd_cancel")],
    ])
    await update.message.reply_text(summary, reply_markup=keyboard)
    await update.message.reply_text("👆", reply_markup=ReplyKeyboardRemove())
    return BRD_CONFIRM


async def boarding_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()

    if query.data == "brd_cancel":
        await query.edit_message_text(t("req_cancelled", lang))
        context.user_data.pop("brd_flow", None)
        return ConversationHandler.END

    flow = context.user_data["brd_flow"]
    user = update.effective_user
    brd_id = sheets.next_boarding_id()
    client_name = user.full_name + (f" (@{user.username})" if user.username else "")
    sheets.add_boarding([
        brd_id,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        client_name,
        flow["phone"],
        user.id,
        flow["pet"],
        flow["dates"],
        flow["notes"],
        flow["city"],
        flow.get("sitter_id", ""),
        "новая",
        "",
    ])
    await query.edit_message_text(t("brd_sent", lang, id=brd_id), parse_mode="HTML")

    sitter = sheets.get_sitter_any(flow.get("sitter_id", "")) or {}
    sitter_info = (
        f"🤝 Ситтер: {sitter.get('имя', '')}, {sitter.get('телефон', '')} "
        f"({sitter.get('цена_сутки', '')}₪/сутки)\n"
        if sitter else "🤝 Ситтер не выбран — подберите вручную\n"
    )
    admin_text = (
        f"🔔 <b>Новая заявка на передержку {brd_id}</b>\n\n"
        f"👤 Владелец: {client_name}\n"
        f"📱 Телефон: {flow['phone']}\n"
        f"🐾 Питомец: {flow['pet']}\n"
        f"📅 Даты: {flow['dates']}\n"
        f"📍 Город: {flow['city']}\n"
        f"📝 Особенности: {flow['notes']}\n"
        + sitter_info
    )
    admin_rows = [[
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"brd_ok:{brd_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"brd_no:{brd_id}"),
    ]]
    sitter_wa = whatsapp_link(sitter.get("телефон", ""))
    if sitter_wa:
        admin_rows.append([InlineKeyboardButton("💬 WhatsApp ситтера", url=sitter_wa)])
    try:
        await context.bot.send_message(
            config.ADMIN_CHAT_ID, admin_text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(admin_rows),
        )
    except Exception:
        logger.exception("Не удалось уведомить администратора о передержке")

    context.user_data.pop("brd_flow", None)
    return ConversationHandler.END


async def boarding_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("brd_flow", None)
    await update.message.reply_text(
        t("req_cancelled", L(context)), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def admin_boarding_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Администратор подтверждает/отклоняет заявку на передержку."""
    query = update.callback_query
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        await query.answer("Эта кнопка только для администратора", show_alert=True)
        return
    await query.answer()

    action, brd_id = query.data.split(":", 1)
    request = sheets.get_boarding(brd_id)
    if not request:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if action == "brd_ok":
        sheets.update_boarding_status(brd_id, "подтверждена")
        badge = "✅ ПОДТВЕРЖДЕНА"
    else:
        sheets.update_boarding_status(brd_id, "отклонена")
        badge = "❌ ОТКЛОНЕНА"
    await query.edit_message_text(
        query.message.text_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
    )

    client_id = str(request.get("tg_id", "")).strip()
    if not client_id.isdigit():
        return
    cli_lang = user_lang(context, client_id)
    try:
        if action == "brd_ok":
            keyboard = None
            sitter = sheets.get_sitter_any(str(request.get("ситтер_id", "")).strip()) or {}
            sitter_wa = whatsapp_link(sitter.get("телефон", ""))
            if sitter_wa:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(t("btn_wa_sitter", cli_lang), url=sitter_wa)]]
                )
            await context.bot.send_message(
                int(client_id),
                t("cli_brd_confirmed", cli_lang, id=brd_id),
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            await context.bot.send_message(
                int(client_id),
                t("cli_brd_declined", cli_lang, id=brd_id),
                parse_mode="HTML",
            )
    except Exception:
        logger.exception("Не удалось уведомить клиента по передержке %s", brd_id)


async def on_error(update, context):
    logger.exception("Ошибка при обработке апдейта", exc_info=context.error)


async def post_init(app):
    """Заполняет меню команд бота (кнопка «Меню» у поля ввода)."""
    await app.bot.set_my_commands([
        ("start", "🏠 Меню / Menu / תפריט"),
        ("catalog", "🐾 Каталог / Catalog / קטלוג"),
        ("filters", "🔍 Фильтры / Filters / מסננים"),
        ("owner", "💼 Сдать питомца / List your pet / להשכיר"),
        ("boarding", "🏡 Передержка / Boarding / פנסיון"),
        ("language", "🌐 Язык / Language / שפה"),
        ("help", "ℹ️ Как это работает / How it works / איך זה עובד"),
        ("cancel", "❌ Отмена / Cancel / ביטול"),
    ])


def main():
    if not config.BOT_TOKEN:
        raise SystemExit("Не задан PETSHARE_BOT_TOKEN в .env")
    persistence = PicklePersistence(filepath="bot_state.pkl")
    app = (
        Application.builder()
        .token(config.BOT_TOKEN)
        .persistence(persistence)
        .post_init(post_init)
        .build()
    )

    request_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(request_start, pattern=r"^request:")],
        states={
            REQ_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_date)],
            REQ_PHONE: [MessageHandler(
                (filters.TEXT & ~filters.COMMAND) | filters.CONTACT, request_phone
            )],
            REQ_CONFIRM: [CallbackQueryHandler(request_confirm, pattern=r"^req_(confirm|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", request_cancel)],
    )

    owner_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(owner_start, pattern=r"^owner_start$"),
            CommandHandler("owner", owner_start_cmd),
        ],
        states={
            OWN_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, owner_name)],
            OWN_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, owner_phone)],
            OWN_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, owner_city)],
            PET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_name)],
            PET_CATEGORY: [CallbackQueryHandler(pet_category, pattern=r"^pc:")],
            PET_CATEGORY_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_category_custom)],
            PET_BREED: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_breed)],
            PET_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_age)],
            PET_TEMPERAMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_temperament)],
            PET_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_skills)],
            PET_KIDS: [CallbackQueryHandler(pet_kids, pattern=r"^kids:")],
            PET_PRICE_HOUR: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_price_hour)],
            PET_PRICE_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_price_event)],
            PET_PHOTO: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), pet_photo)],
            PET_CONFIRM: [CallbackQueryHandler(pet_confirm, pattern=r"^pet_(send|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", owner_cancel)],
    )

    sitter_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(sitter_start, pattern=r"^sitter_form$")],
        states={
            SIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, sitter_name)],
            SIT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sitter_phone)],
            SIT_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, sitter_city)],
            SIT_ANIMALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, sitter_animals)],
            SIT_EXP: [MessageHandler(filters.TEXT & ~filters.COMMAND, sitter_exp)],
            SIT_COND: [MessageHandler(filters.TEXT & ~filters.COMMAND, sitter_cond)],
            SIT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sitter_price)],
            SIT_CONFIRM: [CallbackQueryHandler(sitter_confirm, pattern=r"^sit_(send|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", sitter_cancel)],
    )

    boarding_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(boarding_start, pattern=r"^brdreq:")],
        states={
            BRD_PET: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding_pet)],
            BRD_DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding_dates)],
            BRD_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding_city)],
            BRD_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding_notes)],
            BRD_PHONE: [MessageHandler(
                (filters.TEXT & ~filters.COMMAND) | filters.CONTACT, boarding_phone
            )],
            BRD_CONFIRM: [CallbackQueryHandler(boarding_confirm, pattern=r"^brd_(confirm|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", boarding_cancel)],
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("catalog", cmd_catalog))
    app.add_handler(CommandHandler("filters", cmd_filters))
    app.add_handler(CommandHandler("boarding", cmd_boarding))
    app.add_handler(CommandHandler("language", cmd_language))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("reload", cmd_reload))
    app.add_handler(request_conv)
    app.add_handler(owner_conv)
    app.add_handler(sitter_conv)
    app.add_handler(boarding_conv)
    app.add_handler(CallbackQueryHandler(admin_decision, pattern=r"^adm_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_owner_decision, pattern=r"^own_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_sitter_decision, pattern=r"^sit_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_boarding_decision, pattern=r"^brd_(ok|no):"))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_error_handler(on_error)
    logger.info("Бот PetShare Israel запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
