"""Telegram-бот PetShare Israel: каталог животных и заявки на аренду.

Интерфейс: русский / английский / иврит (i18n.py).
Запуск: ./venv/bin/python bot.py
"""

import logging
from datetime import datetime

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
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
import i18n
import sheets
from i18n import LANGS, t, tr_value

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
BRD_PET, BRD_DATES, BRD_DAYS, BRD_CITY, BRD_NOTES, BRD_PHONE, BRD_CONFIRM = range(40, 47)

# Состояния анкеты знакомств
(
    FRD_NAME, FRD_PHONE, FRD_CITY, FRD_PETNAME, FRD_BREED, FRD_SEX,
    FRD_AGE, FRD_GOAL, FRD_DOCS, FRD_DESC, FRD_PHOTO, FRD_CONFIRM,
) = range(50, 62)

# Состояние написания сообщения (вопрос, ответ, пожелание)
WRITE_MSG = 70

# Состояния регистрации лошади
(
    HRS_NAME, HRS_PHONE, HRS_HORSENAME, HRS_BREED, HRS_AGE, HRS_CITY,
    HRS_CHARACTER, HRS_BEGINNERS, HRS_PRICE_HOUR, HRS_PRICE_SUNSET,
    HRS_PHOTO, HRS_CONFIRM,
) = range(80, 92)

# Состояния заявки на конную прогулку
RID_TIME, RID_DATE, RID_PEOPLE, RID_EXP, RID_WISHES, RID_PHONE, RID_CONFIRM = range(100, 107)

# Состояния отзыва
REV_PICK, REV_RATE, REV_TEXT = range(110, 113)

# Сервисный сбор за организацию вязки, ₪ (дружба — бесплатно)
MATING_FEE = 50

GOAL_KEYS = {"дружба": "goal_friend", "вязка": "goal_mate", "обе": "goal_both"}
SEX_KEYS = {"М": "sex_male", "Ж": "sex_female"}
SEX_ICONS = {"М": "♂", "Ж": "♀"}


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


# Порядок выбора языка при знакомстве: иврит → русский → английский
LANG_ORDER = [
    ("he", "1️⃣ 🇮🇱 עברית"),
    ("ru", "2️⃣ 🇷🇺 Русский"),
    ("en", "3️⃣ 🇬🇧 English"),
]


def language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"lang_set:{code}")]
        for code, label in LANG_ORDER
    ])


async def safe_edit(query, text, reply_markup=None, parse_mode=None):
    """Правит текст экрана; если предыдущий экран был фото — заменяет сообщение."""
    try:
        if query.message and query.message.photo:
            await query.message.delete()
            await query.message.chat.send_message(
                text, reply_markup=reply_markup, parse_mode=parse_mode
            )
        else:
            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=parse_mode
            )
    except Exception:
        logger.exception("safe_edit: не удалось отредактировать, отправляю новое")
        await query.message.chat.send_message(
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )


async def show_card(query, text, keyboard, photo):
    """Показывает карточку: с фото — как фото с подписью, без — текстом."""
    msg = query.message
    try:
        if photo:
            media = InputMediaPhoto(media=photo, caption=text, parse_mode="HTML")
            if msg.photo:
                await query.edit_message_media(media=media, reply_markup=keyboard)
            else:
                await msg.delete()
                await msg.chat.send_photo(
                    photo, caption=text, parse_mode="HTML", reply_markup=keyboard
                )
        else:
            await safe_edit(query, text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        # битое фото (устаревший file_id/ссылка) — показываем текстом
        logger.exception("show_card: фото не показалось, отправляю текст")
        await safe_edit(query, text, reply_markup=keyboard, parse_mode="HTML")


def rating_line(obj_id):
    """Строка рейтинга «⭐ 4.8 (3)» или пустая, если отзывов нет."""
    avg, count = sheets.get_rating(obj_id)
    return f"⭐ {avg} ({count})" if count else ""


def main_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_catalog", lang), callback_data="catalog")],
        [InlineKeyboardButton(t("btn_filters", lang), callback_data="filters")],
        [InlineKeyboardButton(t("btn_owner", lang), callback_data="owner_start")],
        [InlineKeyboardButton(t("btn_boarding", lang), callback_data="board_menu")],
        [InlineKeyboardButton(t("btn_friends", lang), callback_data="frd_menu")],
        [InlineKeyboardButton(t("btn_horses", lang), callback_data="horses_menu")],
        [InlineKeyboardButton(t("btn_wish", lang), callback_data="wish")],
        [InlineKeyboardButton(t("btn_about", lang), callback_data="about")],
        [InlineKeyboardButton(t("btn_lang", lang), callback_data="lang")],
    ])


def horses_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_ride_book", lang), callback_data="hrscard:0")],
        [InlineKeyboardButton(t("btn_horses_list", lang), callback_data="hrscard:0")],
        [InlineKeyboardButton(t("btn_reg_horse", lang), callback_data="hrs_form")],
        [InlineKeyboardButton(t("btn_menu", lang), callback_data="menu")],
    ])


def format_horse_card(horse, position, total, lang, rating=""):
    title = f"🐴 <b>{horse.get('кличка', '')}</b> — {horse.get('порода', '')}"
    if rating:
        title += f"   {rating}"
    lines = [
        title,
        "",
        f"📍 {tr_value(horse.get('город', ''), lang)}   |   "
        f"{t('card_age', lang)}: {horse.get('возраст', '')}",
        f"😊 {t('card_character', lang)}: {horse.get('характер', '')}",
        f"🔰 {t('hrs_card_beginners', lang)}: {tr_value(horse.get('новичкам', ''), lang)}",
        f"💰 {horse.get('цена_час', '')}₪/{t('hrs_card_hour', lang)}   |   "
        f"🌇 {t('hrs_card_sunset', lang)}: {horse.get('цена_закат', '')}₪",
        t("card_accompany", lang),
        "",
        t("card_pos", lang, pos=position, total=total),
    ]
    return "\n".join(lines)


def friends_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_create_profile", lang), callback_data="frd_form")],
        [InlineKeyboardButton(t("btn_browse_friends", lang), callback_data="frdcard:дружба:0")],
        [InlineKeyboardButton(t("btn_browse_mating", lang), callback_data="frdcard:вязка:0")],
        [InlineKeyboardButton(t("btn_menu", lang), callback_data="menu")],
    ])


def format_friend_card(profile, position, total, lang):
    sex = str(profile.get("пол", "")).strip()
    goal = str(profile.get("цель", "")).strip()
    lines = [
        f"🐾 <b>{profile.get('кличка', '')}</b> — {profile.get('вид_порода', '')}",
        "",
        f"{SEX_ICONS.get(sex, '')} {t('frd_card_sex', lang)}: "
        f"{t(SEX_KEYS.get(sex, 'sex_male'), lang)}   |   "
        f"{t('frd_card_age', lang)}: {profile.get('возраст', '')}",
        f"📍 {tr_value(profile.get('город', ''), lang)}",
        f"🎯 {t('frd_card_goal', lang)}: {t(GOAL_KEYS.get(goal, 'goal_both'), lang)}",
        f"📋 {t('frd_card_docs', lang)}: {profile.get('документы', '')}",
    ]
    desc = str(profile.get("описание", "")).strip()
    if desc:
        lines += ["", f"<i>{desc}</i>"]
    lines += ["", t("card_pos", lang, pos=position, total=total)]
    return "\n".join(lines)


def board_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_give_pet", lang), callback_data="brdreq:")],
        [InlineKeyboardButton(t("btn_be_sitter", lang), callback_data="sitter_form")],
        [InlineKeyboardButton(t("btn_sitters_list", lang), callback_data="sitcard:0")],
        [InlineKeyboardButton(t("btn_menu", lang), callback_data="menu")],
    ])


def format_sitter_card(sitter, position, total, lang, rating=""):
    title = f"🤝 <b>{sitter.get('имя', '')}</b> — 📍 {tr_value(sitter.get('город', ''), lang)}"
    if rating:
        title += f"   {rating}"
    return "\n".join([
        title,
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
            f"{CATEGORY_EMOJI.get(cat, '🐾')} {tr_value(cat, lang)}",
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
    city_label = t("any_city", lang) if filt["city"] == "any" else tr_value(filt["city"], lang)
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


def localized_field(animal, field, lang):
    """Значение свободного поля на языке пользователя.

    Берёт колонку вида 'описание_en'; если она пустая — исходную русскую.
    """
    if lang != "ru":
        translated = str(animal.get(f"{field}_{lang}", "")).strip()
        if translated:
            return translated
    return str(animal.get(field, "")).strip()


def format_card(animal, position, total, lang="ru", rating=""):
    """Собирает текст карточки животного."""
    risk = str(animal.get("уровень_риска", "")).strip()
    title = f"🐾 <b>{animal.get('имя', '')}</b> — {animal.get('порода', '')}"
    if rating:
        title += f"   {rating}"
    lines = [
        title,
        "",
        f"📍 {tr_value(animal.get('город', ''), lang)}   |   "
        f"{t('card_age', lang)}: {animal.get('возраст', '')}",
        f"💰 {animal.get('цена_час', '')}₪/{t('card_hour', lang)}   |   "
        f"{animal.get('цена_событие', '')}₪/{t('card_event', lang)}",
        f"😊 {t('card_character', lang)}: {localized_field(animal, 'темперамент', lang)}",
        f"⭐ {t('card_skills', lang)}: {localized_field(animal, 'навыки', lang)}",
        f"{RISK_EMOJI.get(risk, '⚪')} {t('card_risk', lang)}: {tr_value(risk, lang)}",
        f"👶 {t('card_kids', lang)}: {tr_value(animal.get('можно_детям', ''), lang)}",
    ]
    if str(animal.get("сопровождение_владельца", "")).strip().lower() == "да":
        lines.append(t("card_accompany", lang))
    description = localized_field(animal, "описание", lang)
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
    rows.append([InlineKeyboardButton(t("btn_ask", lang), callback_data=f"msg:a:{animal_id}")])
    rows.append([
        InlineKeyboardButton(t("btn_categories", lang), callback_data="catalog"),
        InlineKeyboardButton(t("btn_menu", lang), callback_data="menu"),
    ])
    return InlineKeyboardMarkup(rows)


# ---------- Команды ----------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "lang" not in context.user_data:
        # Крупные анимированные эмодзи — «живое» первое касание
        try:
            await update.message.reply_text("🐶")
        except Exception:
            pass
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


async def cmd_friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    await update.message.reply_text(
        t("frd_menu", lang, mating_fee=MATING_FEE),
        reply_markup=friends_menu_keyboard(lang),
        parse_mode="HTML",
    )


async def cmd_horses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    await update.message.reply_text(
        t("horses_menu", lang), reply_markup=horses_menu_keyboard(lang), parse_mode="HTML"
    )


async def cmd_my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Личный кабинет: все заявки пользователя со статусами."""
    lang = L(context)
    uid = update.effective_user.id
    sections = [
        ("my_rentals", config.SHEET_REQUESTS, "клиент_tg_id",
         lambda r: f"{r.get('id')} — {r.get('животное_имя', '')}, {r.get('дата_аренды', '')}"),
        ("my_boardings", config.SHEET_BOARDING, "tg_id",
         lambda r: f"{r.get('id')} — {r.get('питомец', '')}, {r.get('даты', '')}"),
        ("my_rides", config.SHEET_RIDES, "tg_id",
         lambda r: f"{r.get('id')} — {r.get('кличка', '')}, {r.get('дата', '')}"),
        ("my_matches", config.SHEET_MATCHES, "кто_tg",
         lambda r: f"{r.get('id')} — {r.get('кто_кличка', '')} 💘 {r.get('кого_кличка', '')}"),
    ]
    blocks = []
    for title_key, sheet_name, tg_field, line_fn in sections:
        rows = sheets.get_requests_by_tg(sheet_name, tg_field, uid)
        if not rows:
            continue
        lines = [f"<b>{t(title_key, lang)}</b>"]
        for r in rows[-5:]:  # последние 5 в каждой категории
            status = tr_value(str(r.get("статус", "")).strip(), lang)
            lines.append(f"  {line_fn(r)} — <i>{status}</i>")
        blocks.append("\n".join(lines))
    if not blocks:
        await update.message.reply_text(
            t("my_empty", lang), reply_markup=main_menu_keyboard(lang)
        )
        return
    await update.message.reply_text(
        t("my_title", lang) + "\n\n" + "\n\n".join(blocks), parse_mode="HTML"
    )


# ---------- Отзывы ----------

def reviewable_items(uid):
    """Подтверждённые сделки пользователя: (заявка_id, объект_id, подпись)."""
    items = []
    for r in sheets.get_requests_by_tg(config.SHEET_REQUESTS, "клиент_tg_id", uid):
        if str(r.get("статус", "")).strip() == "подтверждена":
            items.append((r.get("id"), r.get("животное_id"), f"🐾 {r.get('животное_имя', '')}"))
    for r in sheets.get_requests_by_tg(config.SHEET_BOARDING, "tg_id", uid):
        if str(r.get("статус", "")).strip() == "подтверждена" and str(r.get("ситтер_id", "")).strip():
            sitter = sheets.get_sitter_any(str(r.get("ситтер_id")).strip()) or {}
            items.append((r.get("id"), r.get("ситтер_id"), f"🏡 {sitter.get('имя', '')}"))
    for r in sheets.get_requests_by_tg(config.SHEET_RIDES, "tg_id", uid):
        if str(r.get("статус", "")).strip() == "подтверждена":
            items.append((r.get("id"), r.get("лошадь_id"), f"🐴 {r.get('кличка', '')}"))
    return items[-8:]


async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    items = reviewable_items(update.effective_user.id)
    if not items:
        await update.message.reply_text(t("review_none", lang))
        return ConversationHandler.END
    rows = [
        [InlineKeyboardButton(f"{label} ({req_id})", callback_data=f"rpick:{req_id}:{obj_id}")]
        for req_id, obj_id, label in items
    ]
    await update.message.reply_text(
        t("review_pick", lang), reply_markup=InlineKeyboardMarkup(rows), parse_mode="HTML"
    )
    return REV_PICK


async def review_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()
    _, req_id, obj_id = query.data.split(":", 2)
    context.user_data["rev_flow"] = {"req_id": req_id, "obj_id": obj_id}
    rows = [[InlineKeyboardButton("⭐" * n, callback_data=f"rstar:{n}")] for n in range(5, 0, -1)]
    await query.message.reply_text(
        t("review_rate", lang), reply_markup=InlineKeyboardMarkup(rows)
    )
    return REV_RATE


async def review_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["rev_flow"]["rating"] = int(query.data.split(":", 1)[1])
    await query.message.reply_text(t("review_text", L(context)))
    return REV_TEXT


async def review_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    flow = context.user_data.get("rev_flow") or {}
    user = update.effective_user
    rev_id = sheets.next_review_id()
    sheets.add_review([
        rev_id,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        user.full_name,
        user.id,
        flow.get("req_id", ""),
        flow.get("obj_id", ""),
        flow.get("rating", 0),
        update.message.text.strip(),
    ])
    await update.message.reply_text(t("review_saved", lang))
    try:
        await context.bot.send_message(
            config.ADMIN_CHAT_ID,
            f"⭐ <b>Новый отзыв {rev_id}</b>: {'⭐' * flow.get('rating', 0)}\n"
            f"👤 {user.full_name} по заявке {flow.get('req_id', '')} "
            f"({flow.get('obj_id', '')}):\n\n{update.message.text.strip()}",
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Не отправлен отзыв администратору")
    context.user_data.pop("rev_flow", None)
    return ConversationHandler.END


async def review_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("rev_flow", None)
    await update.message.reply_text(
        t("req_cancelled", L(context)), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cmd_reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс кэша таблицы (только для администратора)."""
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        return
    sheets.clear_cache()
    await update.message.reply_text("♻️ Кэш сброшен, данные перечитаются из таблицы.")


TRANSLATE_FIELDS = ("темперамент", "навыки", "описание")


async def cmd_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Автоперевод карточек на en/he (только для администратора).

    Переводит только пустые колонки *_en / *_he — уже заполненные не трогает.
    """
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        return
    from deep_translator import GoogleTranslator

    await update.message.reply_text("🌐 Перевожу карточки, это может занять минуту...")
    translators = {
        "en": GoogleTranslator(source="ru", target="en"),
        "he": GoogleTranslator(source="ru", target="iw"),
    }
    sheets.clear_cache()
    done, errors = 0, 0
    for animal in sheets._get_records(config.SHEET_ANIMALS):
        animal_id = str(animal.get("id", "")).strip()
        if not animal_id:
            continue
        updates = {}
        for field in TRANSLATE_FIELDS:
            source = str(animal.get(field, "")).strip()
            if not source:
                continue
            for lang_code, translator in translators.items():
                column = f"{field}_{lang_code}"
                if str(animal.get(column, "")).strip():
                    continue  # уже переведено
                try:
                    updates[column] = translator.translate(source)
                except Exception:
                    logger.exception("Не перевёлся %s/%s", animal_id, column)
                    errors += 1
        if updates:
            sheets.update_animal_translations(animal_id, updates)
            done += 1
    sheets.clear_cache()
    msg = f"✅ Готово: обновлено карточек — {done}."
    if errors:
        msg += f" Ошибок перевода: {errors} (эти поля покажутся по-русски)."
    await update.message.reply_text(msg)


# ---------- Кнопки (общий обработчик) ----------

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    lang = L(context)
    await query.answer()

    if data == "noop":
        return

    if data == "lang":
        await safe_edit(query,
            t("choose_lang", lang), reply_markup=language_keyboard()
        )
        return

    if data.startswith("lang_set:"):
        new_lang = data.split(":", 1)[1]
        context.user_data["lang"] = new_lang
        await safe_edit(query,t("lang_set", new_lang))
        await query.message.reply_text(
            t("welcome", new_lang),
            reply_markup=main_menu_keyboard(new_lang),
            parse_mode="HTML",
        )
        return

    if data == "menu":
        await safe_edit(query,
            t("menu_short", lang), reply_markup=main_menu_keyboard(lang), parse_mode="HTML"
        )
        return

    if data == "about":
        await safe_edit(query,
            t("about", lang), reply_markup=about_keyboard(lang), parse_mode="HTML"
        )
        return

    if data == "board_menu":
        await safe_edit(query,
            t("board_menu", lang), reply_markup=board_menu_keyboard(lang), parse_mode="HTML"
        )
        return

    if data == "horses_menu":
        await safe_edit(query,
            t("horses_menu", lang), reply_markup=horses_menu_keyboard(lang), parse_mode="HTML"
        )
        return

    if data.startswith("hrscard:"):
        horses = sheets.get_horses()
        if not horses:
            await safe_edit(query,
                t("horses_empty", lang), reply_markup=horses_menu_keyboard(lang)
            )
            return
        index = int(data.split(":", 1)[1]) % len(horses)
        horse = horses[index]
        total = len(horses)
        rows = []
        if total > 1:
            rows.append([
                InlineKeyboardButton("◀️", callback_data=f"hrscard:{(index - 1) % total}"),
                InlineKeyboardButton(f"{index + 1}/{total}", callback_data="noop"),
                InlineKeyboardButton("▶️", callback_data=f"hrscard:{(index + 1) % total}"),
            ])
        rows.append([InlineKeyboardButton(
            t("btn_book_this", lang), callback_data=f"ridebook:{horse.get('id', '')}"
        )])
        rows.append([InlineKeyboardButton(
            t("btn_ask", lang), callback_data=f"msg:h:{horse.get('id', '')}"
        )])
        rows.append([
            InlineKeyboardButton(t("btn_horses", lang), callback_data="horses_menu"),
            InlineKeyboardButton(t("btn_menu", lang), callback_data="menu"),
        ])
        await show_card(
            query,
            format_horse_card(horse, index + 1, total, lang,
                              rating=rating_line(horse.get("id", ""))),
            InlineKeyboardMarkup(rows),
            str(horse.get("фото", "")).strip(),
        )
        return

    if data == "frd_menu":
        await safe_edit(query,
            t("frd_menu", lang, mating_fee=MATING_FEE),
            reply_markup=friends_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if data.startswith("frdcard:"):
        _, goal, index_str = data.split(":", 2)
        profiles = sheets.get_friend_profiles(goal)
        if not profiles:
            await safe_edit(query,
                t("frd_empty", lang), reply_markup=friends_menu_keyboard(lang)
            )
            return
        index = int(index_str) % len(profiles)
        profile = profiles[index]
        total = len(profiles)
        rows = []
        if total > 1:
            rows.append([
                InlineKeyboardButton("◀️", callback_data=f"frdcard:{goal}:{(index - 1) % total}"),
                InlineKeyboardButton(f"{index + 1}/{total}", callback_data="noop"),
                InlineKeyboardButton("▶️", callback_data=f"frdcard:{goal}:{(index + 1) % total}"),
            ])
        rows.append([InlineKeyboardButton(
            t("btn_propose", lang), callback_data=f"propose:{profile.get('id', '')}"
        )])
        rows.append([InlineKeyboardButton(
            t("btn_ask", lang), callback_data=f"msg:f:{profile.get('id', '')}"
        )])
        rows.append([
            InlineKeyboardButton(t("btn_friends", lang), callback_data="frd_menu"),
            InlineKeyboardButton(t("btn_menu", lang), callback_data="menu"),
        ])
        await show_card(
            query,
            format_friend_card(profile, index + 1, total, lang),
            InlineKeyboardMarkup(rows),
            str(profile.get("фото", "")).strip(),
        )
        return

    if data.startswith("propose:"):
        target_id = data.split(":", 1)[1]
        target = sheets.get_friend_any(target_id)
        my_profile = sheets.get_friend_by_tg(update.effective_user.id)
        if not my_profile:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(t("btn_create_profile", lang), callback_data="frd_form")],
                [InlineKeyboardButton(t("btn_friends", lang), callback_data="frd_menu")],
            ])
            await query.message.reply_text(t("frd_need_profile", lang), reply_markup=keyboard)
            return
        if not target:
            await query.message.reply_text(t("frd_empty", lang))
            return
        if str(my_profile.get("id", "")).strip() == str(target.get("id", "")).strip():
            await query.message.reply_text(t("cant_self", lang))
            return

        # Сбор берём, если хотя бы одна сторона ищет вязку
        goals = {str(my_profile.get("цель", "")).strip(), str(target.get("цель", "")).strip()}
        is_mating = bool(goals & {"вязка", "обе"})
        fee = MATING_FEE if is_mating else 0

        match_id = sheets.next_match_id()
        sheets.add_match([
            match_id,
            datetime.now().strftime("%d.%m.%Y %H:%M"),
            my_profile.get("id", ""),
            my_profile.get("кличка", ""),
            update.effective_user.id,
            target.get("id", ""),
            target.get("кличка", ""),
            "новая",
            fee,
        ])
        text = t("propose_sent", lang, id=match_id)
        if fee:
            text += "\n\n" + t("mating_fee_note", lang, fee=fee)
        await query.message.reply_text(text, parse_mode="HTML")

        admin_text = (
            f"🔔 <b>Заявка на знакомство {match_id}</b>\n\n"
            f"🐾 Кто: {my_profile.get('кличка', '')} ({my_profile.get('вид_порода', '')}, "
            f"{my_profile.get('пол', '')}, {my_profile.get('id', '')})\n"
            f"   Владелец: {my_profile.get('владелец_имя', '')}, {my_profile.get('телефон', '')}\n"
            f"   📋 {my_profile.get('документы', '')}\n\n"
            f"💘 К кому: {target.get('кличка', '')} ({target.get('вид_порода', '')}, "
            f"{target.get('пол', '')}, {target.get('id', '')})\n"
            f"   Владелец: {target.get('владелец_имя', '')}, {target.get('телефон', '')}\n"
            f"   📋 {target.get('документы', '')}\n\n"
            + (f"💳 Сбор за вязку: {fee}₪\n" if fee else "🤝 Дружеское знакомство (без сбора)\n")
            + "\n⚠️ Проверьте документы и совместимость (порода, возраст)!"
        )
        admin_rows = [[
            InlineKeyboardButton("✅ Одобрить", callback_data=f"mtc_ok:{match_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"mtc_no:{match_id}"),
        ]]
        wa1 = whatsapp_link(my_profile.get("телефон", ""))
        wa2 = whatsapp_link(target.get("телефон", ""))
        wa_row = []
        if wa1:
            wa_row.append(InlineKeyboardButton("💬 WA инициатора", url=wa1))
        if wa2:
            wa_row.append(InlineKeyboardButton("💬 WA второго", url=wa2))
        if wa_row:
            admin_rows.append(wa_row)
        try:
            await context.bot.send_message(
                config.ADMIN_CHAT_ID, admin_text, parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(admin_rows),
            )
        except Exception:
            logger.exception("Не удалось уведомить администратора о знакомстве")
        return

    if data.startswith("sitcard:"):
        sitters = sheets.get_sitters()
        if not sitters:
            await safe_edit(query,
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
        rows.append([InlineKeyboardButton(
            t("btn_ask", lang), callback_data=f"msg:s:{sitter.get('id', '')}"
        )])
        rows.append([
            InlineKeyboardButton(t("btn_boarding", lang), callback_data="board_menu"),
            InlineKeyboardButton(t("btn_menu", lang), callback_data="menu"),
        ])
        await safe_edit(
            query,
            format_sitter_card(sitter, index + 1, total, lang,
                               rating=rating_line(sitter.get("id", ""))),
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="HTML",
        )
        return

    if data == "catalog":
        keyboard = catalog_keyboard(lang)
        if keyboard is None:
            await safe_edit(query,t("catalog_empty", lang))
            return
        await safe_edit(query,t("choose_category", lang), reply_markup=keyboard)
        return

    if data.startswith("card:"):
        _, category, index_str = data.split(":", 2)
        animals = sheets.get_animals_by_category(category)
        if not animals:
            await safe_edit(query,t("category_empty", lang))
            return
        index = int(index_str) % len(animals)
        animal = animals[index]
        await show_card(
            query,
            format_card(animal, index + 1, len(animals), lang,
                        rating=rating_line(animal.get("id", ""))),
            card_keyboard(category, index, len(animals), animal.get("id", ""), lang),
            str(animal.get("фото_url", "")).strip(),
        )
        return

    # --- Экраны фильтров ---

    if data == "filters" or data == "f_reset":
        if data == "f_reset":
            for key in ("filt_city", "filt_price", "filt_kids"):
                context.user_data.pop(key, None)
        text, keyboard = filter_menu(context)
        await safe_edit(query,text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data == "f_city":
        cities = []
        for a in sheets.get_animals():
            city = str(a.get("город", "")).strip()
            if city and city not in cities:
                cities.append(city)
        rows = [[InlineKeyboardButton(t("any_city_btn", lang), callback_data="f_city_set:any")]]
        rows += [
            [InlineKeyboardButton(f"📍 {tr_value(c, lang)}", callback_data=f"f_city_set:{c}")]
            for c in sorted(cities)
        ]
        await safe_edit(query,
            t("choose_city_txt", lang), reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("f_city_set:"):
        context.user_data["filt_city"] = data.split(":", 1)[1]
        text, keyboard = filter_menu(context)
        await safe_edit(query,text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data == "f_price":
        rows = [
            [InlineKeyboardButton(t(f"price_{key}", lang), callback_data=f"f_price_set:{key}")]
            for key in PRICE_CHECKS
        ]
        await safe_edit(query,
            t("choose_price_txt", lang), reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("f_price_set:"):
        context.user_data["filt_price"] = data.split(":", 1)[1]
        text, keyboard = filter_menu(context)
        await safe_edit(query,text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data == "f_kids":
        current = context.user_data.get("filt_kids", "any")
        context.user_data["filt_kids"] = "да" if current == "any" else "any"
        text, keyboard = filter_menu(context)
        await safe_edit(query,text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data.startswith("fcard:"):
        animals = apply_filters(sheets.get_animals(), get_filters(context))
        if not animals:
            text, keyboard = filter_menu(context)
            await safe_edit(query,
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
        await show_card(
            query,
            format_card(animal, index + 1, total, lang,
                        rating=rating_line(animal.get("id", ""))),
            InlineKeyboardMarkup(rows),
            str(animal.get("фото_url", "")).strip(),
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
        await safe_edit(query,t("req_cancelled", lang))
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

    await safe_edit(query,t("req_sent", lang, id=req_id), parse_mode="HTML")

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
    await safe_edit(query,
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
        await safe_edit(query,
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
    await safe_edit(query,
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
    await update.message.reply_text(t("brd_ask_days", L(context)))
    return BRD_DAYS


async def boarding_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["brd_flow"]["days"] = parse_price(update.message.text)
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

    # Расчёт стоимости и сбора, если выбран конкретный ситтер
    sitter = sheets.get_sitter_any(flow.get("sitter_id", "")) or {}
    rate = parse_price(sitter.get("цена_сутки"))
    days = flow.get("days", 0)
    if rate and days:
        cost = rate * days
        fee = compute_client_fee(cost)
        summary += "\n\n" + t(
            "brd_cost_block", lang,
            days=days, rate=rate, cost=cost, fee=fee, total=cost + fee,
        )
    else:
        summary += "\n\n" + t("brd_cost_later", lang)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_req_send", lang), callback_data="brd_confirm")],
        [InlineKeyboardButton(t("btn_req_cancel", lang), callback_data="brd_cancel")],
    ])
    await update.message.reply_text(summary, reply_markup=keyboard, parse_mode="HTML")
    await update.message.reply_text("👆", reply_markup=ReplyKeyboardRemove())
    return BRD_CONFIRM


async def boarding_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()

    if query.data == "brd_cancel":
        await safe_edit(query,t("req_cancelled", lang))
        context.user_data.pop("brd_flow", None)
        return ConversationHandler.END

    flow = context.user_data["brd_flow"]
    user = update.effective_user
    brd_id = sheets.next_boarding_id()
    client_name = user.full_name + (f" (@{user.username})" if user.username else "")

    sitter = sheets.get_sitter_any(flow.get("sitter_id", "")) or {}
    rate = parse_price(sitter.get("цена_сутки"))
    days = flow.get("days", 0)
    cost = rate * days if rate and days else 0
    client_fee = compute_client_fee(cost)
    sitter_commission = round(cost * OWNER_COMMISSION)
    platform_income = client_fee + sitter_commission

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
        days,
        rate,
        cost,
        client_fee,
        sitter_commission,
        platform_income,
    ])
    await safe_edit(query,t("brd_sent", lang, id=brd_id), parse_mode="HTML")

    sitter_info = (
        f"🤝 Ситтер: {sitter.get('имя', '')}, {sitter.get('телефон', '')} "
        f"({sitter.get('цена_сутки', '')}₪/сутки)\n"
        if sitter else "🤝 Ситтер не выбран — подберите вручную\n"
    )
    if cost:
        money_info = (
            f"\n💰 {days} сут. × {rate}₪ = {cost}₪\n"
            f"➕ Сбор с клиента (10%): {client_fee}₪\n"
            f"➖ Комиссия ситтера (20%): {sitter_commission}₪\n"
            f"<b>Доход платформы: {platform_income}₪</b>\n"
        )
    else:
        money_info = f"\n💰 Суток: {days or '—'}. Стоимость посчитайте после подбора ситтера.\n"
    admin_text = (
        f"🔔 <b>Новая заявка на передержку {brd_id}</b>\n\n"
        f"👤 Владелец: {client_name}\n"
        f"📱 Телефон: {flow['phone']}\n"
        f"🐾 Питомец: {flow['pet']}\n"
        f"📅 Даты: {flow['dates']}\n"
        f"📍 Город: {flow['city']}\n"
        f"📝 Особенности: {flow['notes']}\n"
        + sitter_info + money_info
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
    await safe_edit(query,
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


# ---------- Анкета знакомств ----------

async def friend_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["frd_flow"] = {}
    await query.message.reply_text(t("frd_intro", L(context)), parse_mode="HTML")
    return FRD_NAME


async def friend_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["frd_flow"]["name"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_phone", L(context)))
    return FRD_PHONE


async def friend_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["frd_flow"]["phone"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_city", L(context)))
    return FRD_CITY


async def friend_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["frd_flow"]["city"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_petname", L(context)))
    return FRD_PETNAME


async def friend_petname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["frd_flow"]["pet_name"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_breed", L(context)))
    return FRD_BREED


async def friend_breed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    context.user_data["frd_flow"]["breed"] = update.message.text.strip()
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_male", lang), callback_data="fsex:М"),
        InlineKeyboardButton(t("btn_female", lang), callback_data="fsex:Ж"),
    ]])
    await update.message.reply_text(t("frd_ask_sex", lang), reply_markup=keyboard)
    return FRD_SEX


async def friend_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["frd_flow"]["sex"] = query.data.split(":", 1)[1]
    await query.message.reply_text(t("own_ask_age", L(context)))
    return FRD_AGE


async def friend_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    context.user_data["frd_flow"]["age"] = update.message.text.strip()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_goal_friend", lang), callback_data="fgoal:дружба")],
        [InlineKeyboardButton(t("btn_goal_mate", lang), callback_data="fgoal:вязка")],
        [InlineKeyboardButton(t("btn_goal_both", lang), callback_data="fgoal:обе")],
    ])
    await update.message.reply_text(t("frd_ask_goal", lang), reply_markup=keyboard)
    return FRD_GOAL


async def friend_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["frd_flow"]["goal"] = query.data.split(":", 1)[1]
    await query.message.reply_text(t("frd_ask_docs", L(context)), parse_mode="HTML")
    return FRD_DOCS


async def friend_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["frd_flow"]["docs"] = update.message.text.strip()
    await update.message.reply_text(t("frd_ask_desc", L(context)))
    return FRD_DESC


async def friend_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["frd_flow"]["desc"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_photo", L(context)))
    return FRD_PHOTO


async def friend_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    flow = context.user_data["frd_flow"]
    flow["photo"] = update.message.photo[-1].file_id if update.message.photo else ""

    summary = t(
        "frd_summary", lang,
        name=flow["name"], phone=flow["phone"], city=flow["city"],
        pet_name=flow["pet_name"], breed=flow["breed"],
        sex_icon=SEX_ICONS.get(flow["sex"], ""), sex=t(SEX_KEYS[flow["sex"]], lang),
        age=flow["age"], goal=t(GOAL_KEYS[flow["goal"]], lang),
        docs=flow["docs"], desc=flow["desc"],
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_own_send", lang), callback_data="frd_send")],
        [InlineKeyboardButton(t("btn_own_cancel", lang), callback_data="frd_cancel")],
    ])
    if flow["photo"]:
        await update.message.reply_photo(flow["photo"], caption=summary, reply_markup=keyboard)
    else:
        await update.message.reply_text(summary, reply_markup=keyboard)
    return FRD_CONFIRM


async def friend_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()

    if query.data == "frd_cancel":
        await query.message.reply_text(t("own_cancelled", lang))
        context.user_data.pop("frd_flow", None)
        return ConversationHandler.END

    flow = context.user_data["frd_flow"]
    user = update.effective_user
    profile_id = sheets.next_friend_id()
    sheets.add_friend([
        profile_id,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        flow["name"], flow["phone"], user.id, flow["city"],
        flow["pet_name"], flow["breed"], flow["sex"], flow["age"],
        flow["goal"], flow["docs"], flow["desc"], flow["photo"],
        "на проверке",
    ])
    await query.message.reply_text(t("own_sent", lang))

    admin_text = (
        "🔔 <b>Новая анкета знакомств</b>\n\n"
        f"👤 {flow['name']}, {flow['phone']}, {flow['city']} ({profile_id})\n\n"
        f"🐾 {flow['pet_name']} — {flow['breed']}\n"
        f"{SEX_ICONS.get(flow['sex'], '')} Пол: {flow['sex']}   |   Возраст: {flow['age']}\n"
        f"🎯 Цель: {flow['goal']}\n"
        f"📋 Документы: {flow['docs']}\n"
        f"📝 {flow['desc']}\n\n"
        "⚠️ Для вязки проверьте родословную и ветсправки!"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Одобрить", callback_data=f"frd_ok:{profile_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"frd_no:{profile_id}"),
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
        logger.exception("Не удалось уведомить администратора об анкете знакомств")

    context.user_data.pop("frd_flow", None)
    return ConversationHandler.END


async def friend_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("frd_flow", None)
    await update.message.reply_text(
        t("own_cancelled", L(context)), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def admin_friend_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Администратор одобряет/отклоняет анкету знакомств."""
    query = update.callback_query
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        await query.answer("Эта кнопка только для администратора", show_alert=True)
        return
    await query.answer()

    action, profile_id = query.data.split(":", 1)
    profile = sheets.get_friend_any(profile_id)
    if not profile:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if action == "frd_ok":
        sheets.update_friend_status(profile_id, "проверен")
        badge = "✅ ОДОБРЕНО"
    else:
        sheets.update_friend_status(profile_id, "отклонена")
        badge = "❌ ОТКЛОНЕНО"

    if query.message.photo:
        await query.edit_message_caption(
            caption=query.message.caption_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
        )
    else:
        await safe_edit(query,
            query.message.text_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
        )

    owner_tg = str(profile.get("tg_id", "")).strip()
    if not owner_tg.isdigit():
        return
    own_lang = user_lang(context, owner_tg)
    try:
        key = "frd_approved" if action == "frd_ok" else "frd_declined"
        await context.bot.send_message(
            int(owner_tg), t(key, own_lang, name=profile.get("кличка", ""))
        )
    except Exception:
        logger.exception("Не удалось уведомить владельца анкеты %s", owner_tg)


async def admin_match_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Администратор одобряет/отклоняет заявку на знакомство."""
    query = update.callback_query
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        await query.answer("Эта кнопка только для администратора", show_alert=True)
        return
    await query.answer()

    action, match_id = query.data.split(":", 1)
    match = sheets.get_match(match_id)
    if not match:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if action == "mtc_ok":
        sheets.update_match_status(match_id, "одобрена")
        badge = "✅ ОДОБРЕНО"
    else:
        sheets.update_match_status(match_id, "отклонена")
        badge = "❌ ОТКЛОНЕНО"
    await safe_edit(query,
        query.message.text_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
    )

    who = sheets.get_friend_any(str(match.get("кто_id", "")).strip()) or {}
    target = sheets.get_friend_any(str(match.get("кого_id", "")).strip()) or {}

    async def notify(profile, other):
        tg = str(profile.get("tg_id", "")).strip()
        if not tg.isdigit():
            return
        lng = user_lang(context, tg)
        if action == "mtc_ok":
            keyboard = None
            wa = whatsapp_link(other.get("телефон", ""))
            if wa:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(t("btn_wa_owner", lng), url=wa)]]
                )
            await context.bot.send_message(
                int(tg),
                t("mtc_confirmed", lng, id=match_id,
                  pet1=profile.get("кличка", ""), pet2=other.get("кличка", "")),
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            await context.bot.send_message(
                int(tg), t("mtc_declined", lng, id=match_id), parse_mode="HTML"
            )

    try:
        await notify(who, target)
        # второму владельцу сообщаем только при одобрении
        if action == "mtc_ok":
            await notify(target, who)
    except Exception:
        logger.exception("Не удалось уведомить участников знакомства %s", match_id)


# ---------- Сообщения через бота ----------

def resolve_msg_target(kind, obj_id):
    """Куда доставить сообщение: (tg_id, подпись, телефон для WhatsApp).

    kind: 'a' — животное (пишем владельцу), 's' — ситтер, 'f' — анкета знакомств.
    """
    if kind == "a":
        animal = sheets.get_animal_any(obj_id) or {}
        owner = sheets.get_owner_by_id(str(animal.get("владелец_id", "")).strip()) or {}
        return (
            str(owner.get("tg_id", "")).strip(),
            str(animal.get("имя", "")).strip() or obj_id,
            owner.get("телефон", ""),
        )
    if kind == "s":
        sitter = sheets.get_sitter_any(obj_id) or {}
        return (
            str(sitter.get("tg_id", "")).strip(),
            str(sitter.get("имя", "")).strip() or obj_id,
            sitter.get("телефон", ""),
        )
    if kind == "f":
        profile = sheets.get_friend_any(obj_id) or {}
        return (
            str(profile.get("tg_id", "")).strip(),
            str(profile.get("кличка", "")).strip() or obj_id,
            profile.get("телефон", ""),
        )
    if kind == "h":
        horse = sheets.get_horse_any(obj_id) or {}
        return (
            str(horse.get("tg_id", "")).strip(),
            str(horse.get("кличка", "")).strip() or obj_id,
            horse.get("телефон", ""),
        )
    return "", obj_id, ""


async def msg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка «Задать вопрос» на карточке."""
    query = update.callback_query
    lang = L(context)
    await query.answer()
    _, kind, obj_id = query.data.split(":", 2)
    target_tg, label, phone = resolve_msg_target(kind, obj_id)
    context.user_data["msg_ctx"] = {
        "target_tg": target_tg, "label": label, "phone": phone, "kind": "вопрос",
    }
    await query.message.reply_text(t("ask_intro", lang, name=label), parse_mode="HTML")
    return WRITE_MSG


async def reply_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка «Ответить» под входящим сообщением."""
    query = update.callback_query
    lang = L(context)
    await query.answer()
    target_tg = query.data.split(":", 1)[1]
    context.user_data["msg_ctx"] = {
        "target_tg": target_tg, "label": t("reply_label", lang),
        "phone": "", "kind": "ответ",
    }
    await query.message.reply_text(t("reply_intro", lang))
    return WRITE_MSG


async def wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка «Не нашли? Напишите нам»."""
    query = update.callback_query
    lang = L(context)
    await query.answer()
    context.user_data["msg_ctx"] = {
        "target_tg": str(config.ADMIN_CHAT_ID), "label": "пожелание",
        "phone": "", "kind": "пожелание",
    }
    await query.message.reply_text(t("wish_intro", lang))
    return WRITE_MSG


async def msg_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пользователь написал текст сообщения — доставляем."""
    lang = L(context)
    ctx = context.user_data.get("msg_ctx") or {}
    user = update.effective_user
    text = update.message.text.strip()
    from_name = user.full_name + (f" (@{user.username})" if user.username else "")

    msg_id = sheets.next_message_id()
    sheets.add_message([
        msg_id,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        from_name,
        user.id,
        ctx.get("target_tg", ""),
        ctx.get("label", ""),
        text,
        ctx.get("kind", ""),
    ])

    target_tg = str(ctx.get("target_tg", "")).strip()
    delivered = False
    if target_tg.isdigit() and int(target_tg) != user.id:
        to_lang = user_lang(context, target_tg)
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(t("btn_reply", to_lang), callback_data=f"wrt:{user.id}")]]
        )
        try:
            await context.bot.send_message(
                int(target_tg),
                t("incoming_msg", to_lang, label=ctx.get("label", ""), text=text),
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            delivered = True
        except Exception:
            logger.exception("Не доставлено сообщение %s адресату %s", msg_id, target_tg)

    # Копия администратору (если он не отправитель и не получатель)
    if user.id != config.ADMIN_CHAT_ID and target_tg != str(config.ADMIN_CHAT_ID):
        note = "" if delivered else "\n⚠️ У адресата нет Telegram — передайте через WhatsApp!"
        admin_rows = []
        wa = whatsapp_link(ctx.get("phone", ""))
        if wa and not delivered:
            admin_rows.append([InlineKeyboardButton("💬 WhatsApp адресата", url=wa)])
        try:
            await context.bot.send_message(
                config.ADMIN_CHAT_ID,
                f"💬 <b>{msg_id}</b> {from_name} → «{ctx.get('label', '')}»:\n\n{text}{note}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(admin_rows) if admin_rows else None,
            )
        except Exception:
            logger.exception("Не отправлена копия сообщения %s администратору", msg_id)

    key = "wish_sent" if ctx.get("kind") == "пожелание" else "msg_sent"
    await update.message.reply_text(t(key, lang))
    context.user_data.pop("msg_ctx", None)
    return ConversationHandler.END


async def msg_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("msg_ctx", None)
    await update.message.reply_text(
        t("req_cancelled", L(context)), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ---------- Регистрация лошади ----------

async def horse_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["hrs_flow"] = {}
    await query.message.reply_text(t("hrs_intro", L(context)), parse_mode="HTML")
    return HRS_NAME


async def horse_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hrs_flow"]["name"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_phone", L(context)))
    return HRS_PHONE


async def horse_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hrs_flow"]["phone"] = update.message.text.strip()
    await update.message.reply_text(t("hrs_ask_horsename", L(context)))
    return HRS_HORSENAME


async def horse_horsename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hrs_flow"]["horse_name"] = update.message.text.strip()
    await update.message.reply_text(t("hrs_ask_breed", L(context)))
    return HRS_BREED


async def horse_breed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hrs_flow"]["breed"] = update.message.text.strip()
    await update.message.reply_text(t("own_ask_age", L(context)))
    return HRS_AGE


async def horse_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hrs_flow"]["age"] = update.message.text.strip()
    await update.message.reply_text(t("hrs_ask_city", L(context)))
    return HRS_CITY


async def horse_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hrs_flow"]["city"] = update.message.text.strip()
    await update.message.reply_text(t("hrs_ask_character", L(context)))
    return HRS_CHARACTER


async def horse_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    context.user_data["hrs_flow"]["character"] = update.message.text.strip()
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_yes", lang), callback_data="hb:да"),
        InlineKeyboardButton(t("btn_no", lang), callback_data="hb:нет"),
    ]])
    await update.message.reply_text(t("hrs_ask_beginners", lang), reply_markup=keyboard)
    return HRS_BEGINNERS


async def horse_beginners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["hrs_flow"]["beginners"] = query.data.split(":", 1)[1]
    await query.message.reply_text(t("hrs_ask_price_hour", L(context)))
    return HRS_PRICE_HOUR


async def horse_price_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hrs_flow"]["price_hour"] = parse_price(update.message.text)
    await update.message.reply_text(t("hrs_ask_price_sunset", L(context)))
    return HRS_PRICE_SUNSET


async def horse_price_sunset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hrs_flow"]["price_sunset"] = parse_price(update.message.text)
    await update.message.reply_text(t("own_ask_photo", L(context)))
    return HRS_PHOTO


async def horse_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    flow = context.user_data["hrs_flow"]
    flow["photo"] = update.message.photo[-1].file_id if update.message.photo else ""

    summary = t(
        "hrs_summary", lang,
        name=flow["name"], phone=flow["phone"], horse_name=flow["horse_name"],
        breed=flow["breed"], age=flow["age"], city=flow["city"],
        character=flow["character"], beginners=tr_value(flow["beginners"], lang),
        price_hour=flow["price_hour"], price_sunset=flow["price_sunset"],
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_own_send", lang), callback_data="hrs_send")],
        [InlineKeyboardButton(t("btn_own_cancel", lang), callback_data="hrs_cancel")],
    ])
    if flow["photo"]:
        await update.message.reply_photo(flow["photo"], caption=summary, reply_markup=keyboard)
    else:
        await update.message.reply_text(summary, reply_markup=keyboard)
    return HRS_CONFIRM


async def horse_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()

    if query.data == "hrs_cancel":
        await query.message.reply_text(t("own_cancelled", lang))
        context.user_data.pop("hrs_flow", None)
        return ConversationHandler.END

    flow = context.user_data["hrs_flow"]
    user = update.effective_user
    horse_id = sheets.next_horse_id()
    sheets.add_horse([
        horse_id,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        flow["name"], flow["phone"], user.id,
        flow["horse_name"], flow["breed"], flow["age"], flow["city"],
        flow["character"], flow["beginners"],
        flow["price_hour"], flow["price_sunset"], flow["photo"],
        "на проверке",
    ])
    await query.message.reply_text(t("own_sent", lang))

    admin_text = (
        "🔔 <b>Новая лошадь на проверку</b>\n\n"
        f"👤 {flow['name']}, {flow['phone']} ({horse_id})\n"
        f"🐴 {flow['horse_name']} — {flow['breed']}, {flow['age']}\n"
        f"📍 {flow['city']}\n"
        f"😊 {flow['character']}\n"
        f"🔰 Новичкам: {flow['beginners']}\n"
        f"💰 {flow['price_hour']}₪/час | 🌇 {flow['price_sunset']}₪\n\n"
        "⚠️ Проверьте условия содержания и безопасность прогулок!"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Одобрить", callback_data=f"hrs_ok:{horse_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"hrs_no:{horse_id}"),
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
        logger.exception("Не удалось уведомить администратора о лошади")

    context.user_data.pop("hrs_flow", None)
    return ConversationHandler.END


async def horse_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("hrs_flow", None)
    await update.message.reply_text(
        t("own_cancelled", L(context)), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def admin_horse_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Администратор одобряет/отклоняет лошадь."""
    query = update.callback_query
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        await query.answer("Эта кнопка только для администратора", show_alert=True)
        return
    await query.answer()

    action, horse_id = query.data.split(":", 1)
    horse = sheets.get_horse_any(horse_id)
    if not horse:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if action == "hrs_ok":
        sheets.update_horse_status(horse_id, "проверен")
        badge = "✅ ОДОБРЕНО"
    else:
        sheets.update_horse_status(horse_id, "отклонена")
        badge = "❌ ОТКЛОНЕНО"

    if query.message.photo:
        await query.edit_message_caption(
            caption=query.message.caption_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
        )
    else:
        await safe_edit(query,
            query.message.text_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
        )

    owner_tg = str(horse.get("tg_id", "")).strip()
    if not owner_tg.isdigit():
        return
    own_lang = user_lang(context, owner_tg)
    try:
        key = "hrs_approved" if action == "hrs_ok" else "hrs_declined"
        await context.bot.send_message(
            int(owner_tg), t(key, own_lang, name=horse.get("кличка", ""))
        )
    except Exception:
        logger.exception("Не удалось уведомить владельца лошади %s", owner_tg)


# ---------- Заявка на конную прогулку ----------

async def ride_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()
    horse_id = query.data.split(":", 1)[1]
    horse = sheets.get_horse_any(horse_id)
    if not horse:
        await query.message.reply_text(t("horses_empty", lang))
        return ConversationHandler.END
    context.user_data["rid_flow"] = {"horse_id": horse_id, "horse": horse.get("кличка", "")}
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("btn_dawn", lang), callback_data="tod:рассвет"),
            InlineKeyboardButton(t("btn_day", lang), callback_data="tod:день"),
        ],
        [
            InlineKeyboardButton(t("btn_sunset", lang), callback_data="tod:закат"),
            InlineKeyboardButton(t("btn_evening", lang), callback_data="tod:вечер"),
        ],
    ])
    await query.message.reply_text(
        t("rid_ask_time", lang, name=horse.get("кличка", "")), reply_markup=keyboard
    )
    return RID_TIME


async def ride_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["rid_flow"]["tod"] = query.data.split(":", 1)[1]
    await query.message.reply_text(t("rid_ask_date", L(context)), parse_mode="HTML")
    return RID_DATE


async def ride_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["rid_flow"]["date"] = update.message.text.strip()
    await update.message.reply_text(t("rid_ask_people", L(context)))
    return RID_PEOPLE


async def ride_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    people = parse_price(update.message.text)
    context.user_data["rid_flow"]["people"] = max(people, 1)
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_beginner", lang), callback_data="rexp:новичок"),
        InlineKeyboardButton(t("btn_experienced", lang), callback_data="rexp:опытный"),
    ]])
    await update.message.reply_text(t("rid_ask_exp", lang), reply_markup=keyboard)
    return RID_EXP


async def ride_exp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["rid_flow"]["exp"] = query.data.split(":", 1)[1]
    await query.message.reply_text(t("rid_ask_wishes", L(context)))
    return RID_WISHES


async def ride_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    context.user_data["rid_flow"]["wishes"] = update.message.text.strip()
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(t("btn_send_phone", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(t("req_ask_phone", lang), reply_markup=keyboard)
    return RID_PHONE


def ride_price(flow):
    """Цена с человека: закат/рассвет — по закатному тарифу."""
    horse = sheets.get_horse_any(flow.get("horse_id", "")) or {}
    if flow.get("tod") in ("закат", "рассвет"):
        return parse_price(horse.get("цена_закат")) or parse_price(horse.get("цена_час"))
    return parse_price(horse.get("цена_час"))


async def ride_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    flow = context.user_data["rid_flow"]
    if update.message.contact:
        flow["phone"] = update.message.contact.phone_number
    else:
        flow["phone"] = update.message.text.strip()

    price = ride_price(flow)
    people = flow["people"]
    cost = price * people
    fee = compute_client_fee(cost)

    summary = t(
        "rid_summary", lang,
        horse=flow["horse"], tod=t(f"tod_{flow['tod']}", lang), date=flow["date"],
        people=people, exp=t(f"exp_{flow['exp']}", lang), wishes=flow["wishes"],
        phone=flow["phone"], price=price, cost=cost, fee=fee, total=cost + fee,
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_req_send", lang), callback_data="rid_confirm")],
        [InlineKeyboardButton(t("btn_req_cancel", lang), callback_data="rid_cancel")],
    ])
    await update.message.reply_text(summary, reply_markup=keyboard, parse_mode="HTML")
    await update.message.reply_text("👆", reply_markup=ReplyKeyboardRemove())
    return RID_CONFIRM


async def ride_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = L(context)
    await query.answer()

    if query.data == "rid_cancel":
        await safe_edit(query,t("req_cancelled", lang))
        context.user_data.pop("rid_flow", None)
        return ConversationHandler.END

    flow = context.user_data["rid_flow"]
    user = update.effective_user
    price = ride_price(flow)
    people = flow["people"]
    cost = price * people
    client_fee = compute_client_fee(cost)
    owner_commission = round(cost * OWNER_COMMISSION)
    platform_income = client_fee + owner_commission

    ride_id = sheets.next_ride_id()
    client_name = user.full_name + (f" (@{user.username})" if user.username else "")
    sheets.add_ride([
        ride_id,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        client_name,
        flow["phone"],
        user.id,
        flow["horse_id"],
        flow["horse"],
        flow["tod"],
        flow["date"],
        people,
        flow["exp"],
        flow["wishes"],
        price,
        cost,
        client_fee,
        owner_commission,
        platform_income,
        "новая",
    ])
    await safe_edit(query,t("rid_sent", lang, id=ride_id), parse_mode="HTML")

    horse = sheets.get_horse_any(flow["horse_id"]) or {}
    admin_text = (
        f"🔔 <b>Новая заявка на прогулку {ride_id}</b>\n\n"
        f"🐴 {flow['horse']} ({flow['horse_id']}), владелец: {horse.get('владелец_имя', '—')}, "
        f"{horse.get('телефон', '—')}\n"
        f"👤 Клиент: {client_name}, {flow['phone']}\n"
        f"🕐 {flow['tod']}, {flow['date']}\n"
        f"👥 Человек: {people} ({flow['exp']})\n"
        f"📝 Пожелания: {flow['wishes']}\n\n"
        f"💰 {people} × {price}₪ = {cost}₪\n"
        f"➕ Сбор с клиента (10%): {client_fee}₪\n"
        f"➖ Комиссия владельца (20%): {owner_commission}₪\n"
        f"<b>Доход платформы: {platform_income}₪</b>"
    )
    admin_rows = [[
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"rid_ok:{ride_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"rid_no:{ride_id}"),
    ]]
    horse_wa = whatsapp_link(horse.get("телефон", ""))
    if horse_wa:
        admin_rows.append([InlineKeyboardButton("💬 WhatsApp владельца", url=horse_wa)])
    try:
        await context.bot.send_message(
            config.ADMIN_CHAT_ID, admin_text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(admin_rows),
        )
    except Exception:
        logger.exception("Не удалось уведомить администратора о прогулке")

    context.user_data.pop("rid_flow", None)
    return ConversationHandler.END


async def ride_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("rid_flow", None)
    await update.message.reply_text(
        t("req_cancelled", L(context)), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def admin_ride_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Администратор подтверждает/отклоняет конную прогулку."""
    query = update.callback_query
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        await query.answer("Эта кнопка только для администратора", show_alert=True)
        return
    await query.answer()

    action, ride_id = query.data.split(":", 1)
    ride = sheets.get_ride(ride_id)
    if not ride:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if action == "rid_ok":
        sheets.update_ride_status(ride_id, "подтверждена")
        badge = "✅ ПОДТВЕРЖДЕНА"
    else:
        sheets.update_ride_status(ride_id, "отклонена")
        badge = "❌ ОТКЛОНЕНА"
    await safe_edit(query,
        query.message.text_html + f"\n\n<b>{badge}</b>", parse_mode="HTML"
    )

    client_id = str(ride.get("tg_id", "")).strip()
    if not client_id.isdigit():
        return
    cli_lang = user_lang(context, client_id)
    horse = sheets.get_horse_any(str(ride.get("лошадь_id", "")).strip()) or {}
    try:
        if action == "rid_ok":
            keyboard = None
            horse_wa = whatsapp_link(horse.get("телефон", ""))
            if horse_wa:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(t("btn_wa_owner", cli_lang), url=horse_wa)]]
                )
            tod = str(ride.get("время_суток", "")).strip()
            tod_label = t(f"tod_{tod}", cli_lang) if f"tod_{tod}" in i18n.T else tod
            await context.bot.send_message(
                int(client_id),
                t("cli_rid_confirmed", cli_lang, id=ride_id,
                  horse=ride.get("кличка", ""), date=ride.get("дата", ""), tod=tod_label),
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            await context.bot.send_message(
                int(client_id),
                t("cli_rid_declined", cli_lang, id=ride_id),
                parse_mode="HTML",
            )
    except Exception:
        logger.exception("Не удалось уведомить клиента по прогулке %s", ride_id)


async def use_buttons_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пользователь написал текст там, где ждём нажатие кнопки."""
    await update.message.reply_text(t("use_buttons", L(context)))
    # состояние не меняем — остаёмся на том же шаге


async def global_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/cancel вне анкет — показываем меню."""
    lang = L(context)
    await update.message.reply_text(
        t("nothing_to_cancel", lang),
        reply_markup=main_menu_keyboard(lang),
    )


async def fallback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Любое сообщение, которое не поймал ни один сценарий."""
    if "lang" not in context.user_data:
        await update.message.reply_text(
            t("choose_lang_first", "ru"),
            reply_markup=language_keyboard(),
            parse_mode="HTML",
        )
        return
    lang = L(context)
    await update.message.reply_text(
        t("fallback_msg", lang),
        reply_markup=main_menu_keyboard(lang),
    )


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
        ("friends", "💞 Знакомства / Matchmaking / היכרויות"),
        ("horses", "🐴 Конные прогулки / Horse rides / רכיבה"),
        ("my", "📋 Мои заявки / My requests / הבקשות שלי"),
        ("review", "⭐ Оставить отзыв / Leave a review / ביקורת"),
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
            REQ_CONFIRM: [
                CallbackQueryHandler(request_confirm, pattern=r"^req_(confirm|cancel)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
        },
        fallbacks=[CommandHandler("cancel", request_cancel)],
        conversation_timeout=1800,
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
            PET_CATEGORY: [
                CallbackQueryHandler(pet_category, pattern=r"^pc:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
            PET_CATEGORY_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_category_custom)],
            PET_BREED: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_breed)],
            PET_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_age)],
            PET_TEMPERAMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_temperament)],
            PET_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_skills)],
            PET_KIDS: [
                CallbackQueryHandler(pet_kids, pattern=r"^kids:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
            PET_PRICE_HOUR: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_price_hour)],
            PET_PRICE_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, pet_price_event)],
            PET_PHOTO: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), pet_photo)],
            PET_CONFIRM: [
                CallbackQueryHandler(pet_confirm, pattern=r"^pet_(send|cancel)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
        },
        fallbacks=[CommandHandler("cancel", owner_cancel)],
        conversation_timeout=1800,
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
            SIT_CONFIRM: [
                CallbackQueryHandler(sitter_confirm, pattern=r"^sit_(send|cancel)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
        },
        fallbacks=[CommandHandler("cancel", sitter_cancel)],
        conversation_timeout=1800,
    )

    boarding_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(boarding_start, pattern=r"^brdreq:")],
        states={
            BRD_PET: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding_pet)],
            BRD_DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding_dates)],
            BRD_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding_days)],
            BRD_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding_city)],
            BRD_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding_notes)],
            BRD_PHONE: [MessageHandler(
                (filters.TEXT & ~filters.COMMAND) | filters.CONTACT, boarding_phone
            )],
            BRD_CONFIRM: [
                CallbackQueryHandler(boarding_confirm, pattern=r"^brd_(confirm|cancel)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
        },
        fallbacks=[CommandHandler("cancel", boarding_cancel)],
        conversation_timeout=1800,
    )

    friend_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(friend_start, pattern=r"^frd_form$")],
        states={
            FRD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_name)],
            FRD_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_phone)],
            FRD_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_city)],
            FRD_PETNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_petname)],
            FRD_BREED: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_breed)],
            FRD_SEX: [
                CallbackQueryHandler(friend_sex, pattern=r"^fsex:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
            FRD_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_age)],
            FRD_GOAL: [
                CallbackQueryHandler(friend_goal, pattern=r"^fgoal:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
            FRD_DOCS: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_docs)],
            FRD_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_desc)],
            FRD_PHOTO: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), friend_photo)],
            FRD_CONFIRM: [
                CallbackQueryHandler(friend_confirm, pattern=r"^frd_(send|cancel)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
        },
        fallbacks=[CommandHandler("cancel", friend_cancel)],
        conversation_timeout=1800,
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("catalog", cmd_catalog))
    app.add_handler(CommandHandler("filters", cmd_filters))
    app.add_handler(CommandHandler("boarding", cmd_boarding))
    app.add_handler(CommandHandler("friends", cmd_friends))
    app.add_handler(CommandHandler("horses", cmd_horses))
    app.add_handler(CommandHandler("my", cmd_my))
    app.add_handler(CommandHandler("language", cmd_language))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("reload", cmd_reload))
    app.add_handler(CommandHandler("translate", cmd_translate))
    message_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(msg_start, pattern=r"^msg:"),
            CallbackQueryHandler(reply_start, pattern=r"^wrt:"),
            CallbackQueryHandler(wish_start, pattern=r"^wish$"),
        ],
        states={
            WRITE_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_text)],
        },
        fallbacks=[CommandHandler("cancel", msg_cancel)],
        conversation_timeout=1800,
    )

    horse_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(horse_start, pattern=r"^hrs_form$")],
        states={
            HRS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, horse_name)],
            HRS_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, horse_phone)],
            HRS_HORSENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, horse_horsename)],
            HRS_BREED: [MessageHandler(filters.TEXT & ~filters.COMMAND, horse_breed)],
            HRS_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, horse_age)],
            HRS_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, horse_city)],
            HRS_CHARACTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, horse_character)],
            HRS_BEGINNERS: [
                CallbackQueryHandler(horse_beginners, pattern=r"^hb:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
            HRS_PRICE_HOUR: [MessageHandler(filters.TEXT & ~filters.COMMAND, horse_price_hour)],
            HRS_PRICE_SUNSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, horse_price_sunset)],
            HRS_PHOTO: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), horse_photo)],
            HRS_CONFIRM: [
                CallbackQueryHandler(horse_confirm, pattern=r"^hrs_(send|cancel)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
        },
        fallbacks=[CommandHandler("cancel", horse_cancel)],
        conversation_timeout=1800,
    )

    ride_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ride_start, pattern=r"^ridebook:")],
        states={
            RID_TIME: [
                CallbackQueryHandler(ride_time, pattern=r"^tod:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
            RID_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ride_date)],
            RID_PEOPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ride_people)],
            RID_EXP: [
                CallbackQueryHandler(ride_exp, pattern=r"^rexp:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
            RID_WISHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ride_wishes)],
            RID_PHONE: [MessageHandler(
                (filters.TEXT & ~filters.COMMAND) | filters.CONTACT, ride_phone
            )],
            RID_CONFIRM: [
                CallbackQueryHandler(ride_confirm, pattern=r"^rid_(confirm|cancel)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
        },
        fallbacks=[CommandHandler("cancel", ride_cancel)],
        conversation_timeout=1800,
    )

    review_conv = ConversationHandler(
        entry_points=[CommandHandler("review", review_start)],
        states={
            REV_PICK: [
                CallbackQueryHandler(review_pick, pattern=r"^rpick:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
            REV_RATE: [
                CallbackQueryHandler(review_rate, pattern=r"^rstar:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, use_buttons_reply),
            ],
            REV_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_text)],
        },
        fallbacks=[CommandHandler("cancel", review_cancel)],
        conversation_timeout=1800,
    )

    app.add_handler(request_conv)
    app.add_handler(owner_conv)
    app.add_handler(sitter_conv)
    app.add_handler(boarding_conv)
    app.add_handler(friend_conv)
    app.add_handler(horse_conv)
    app.add_handler(ride_conv)
    app.add_handler(message_conv)
    app.add_handler(review_conv)
    app.add_handler(CallbackQueryHandler(admin_decision, pattern=r"^adm_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_owner_decision, pattern=r"^own_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_sitter_decision, pattern=r"^sit_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_boarding_decision, pattern=r"^brd_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_friend_decision, pattern=r"^frd_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_match_decision, pattern=r"^mtc_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_horse_decision, pattern=r"^hrs_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_ride_decision, pattern=r"^rid_(ok|no):"))
    app.add_handler(CallbackQueryHandler(on_callback))
    # Страховка: /cancel вне анкет и любое непонятое сообщение — всегда есть ответ
    app.add_handler(CommandHandler("cancel", global_cancel))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, fallback_message))
    app.add_error_handler(on_error)
    logger.info("Бот PetShare Israel запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
