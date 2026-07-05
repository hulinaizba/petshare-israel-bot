"""Telegram-бот PetShare Israel: каталог животных и заявки на аренду.

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
    filters,
)

import config
import sheets

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


def parse_price(value):
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return 0


def whatsapp_link(phone):
    """Превращает номер в ссылку wa.me (оставляет только цифры)."""
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    return f"https://wa.me/{digits}" if digits else ""


def compute_client_fee(price, first_time):
    """Сервисный сбор клиента; для первой аренды — 0 (промо)."""
    return 0 if first_time else round(price * CLIENT_FEE)


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🐾 Каталог животных", callback_data="catalog")],
        [InlineKeyboardButton("🔍 Подбор по фильтрам", callback_data="filters")],
        [InlineKeyboardButton("💼 Сдать питомца в аренду", callback_data="owner_start")],
        [InlineKeyboardButton("ℹ️ Как это работает", callback_data="about")],
    ])


# ---------- Фильтры ----------

PRICE_OPTIONS = {
    "any": ("любая", None),
    "low": ("до 100₪/час", lambda p: p <= 100),
    "high": ("от 100₪/час", lambda p: p > 100),
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
        price_check = PRICE_OPTIONS[filt["price"]][1]
        if price_check and not price_check(parse_price(a.get("цена_час"))):
            continue
        if filt["kids"] == "да" and str(a.get("можно_детям", "")).strip().lower() != "да":
            continue
        result.append(a)
    return result


def filter_menu(context):
    """Текст и клавиатура экрана фильтров."""
    filt = get_filters(context)
    city_label = "любой" if filt["city"] == "any" else filt["city"]
    price_label = PRICE_OPTIONS[filt["price"]][0]
    kids_label = "не важно" if filt["kids"] == "any" else "только да"
    count = len(apply_filters(sheets.get_animals(), filt))
    text = (
        "🔍 <b>Подбор по фильтрам</b>\n\n"
        f"📍 Город: <b>{city_label}</b>\n"
        f"💰 Цена: <b>{price_label}</b>\n"
        f"👶 Можно детям: <b>{kids_label}</b>\n\n"
        f"Найдено животных: <b>{count}</b>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Выбрать город", callback_data="f_city")],
        [InlineKeyboardButton("💰 Выбрать цену", callback_data="f_price")],
        [InlineKeyboardButton("👶 Можно детям: да/не важно", callback_data="f_kids")],
        [InlineKeyboardButton(f"✅ Показать ({count})", callback_data="fcard:0")],
        [
            InlineKeyboardButton("♻️ Сбросить", callback_data="f_reset"),
            InlineKeyboardButton("🏠 Меню", callback_data="menu"),
        ],
    ])
    return text, keyboard


def format_card(animal, position, total):
    """Собирает текст карточки животного."""
    risk = str(animal.get("уровень_риска", "")).strip()
    lines = [
        f"🐾 <b>{animal.get('имя', '')}</b> — {animal.get('порода', '')}",
        "",
        f"📍 {animal.get('город', '')}   |   возраст: {animal.get('возраст', '')}",
        f"💰 {animal.get('цена_час', '')}₪/час   |   {animal.get('цена_событие', '')}₪/мероприятие",
        f"😊 Характер: {animal.get('темперамент', '')}",
        f"⭐ Умеет: {animal.get('навыки', '')}",
        f"{RISK_EMOJI.get(risk, '⚪')} Уровень риска: {risk}",
        f"👶 Можно детям: {animal.get('можно_детям', '')}",
    ]
    if str(animal.get("сопровождение_владельца", "")).strip().lower() == "да":
        lines.append("👤 Только с сопровождением владельца")
    description = str(animal.get("описание", "")).strip()
    if description:
        lines += ["", f"<i>{description}</i>"]
    lines += ["", f"Карточка {position} из {total}"]
    return "\n".join(lines)


def card_keyboard(category, index, total, animal_id):
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
    rows.append([InlineKeyboardButton("📩 Оставить заявку", callback_data=f"request:{animal_id}")])
    rows.append([
        InlineKeyboardButton("🔙 Категории", callback_data="catalog"),
        InlineKeyboardButton("🏠 Меню", callback_data="menu"),
    ])
    return InlineKeyboardMarkup(rows)


WELCOME_TEXT = (
    "🐾 <b>PetShare Israel</b>\n"
    "<i>Животные, которые делают события незабываемыми</i>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "📸 Фотосессия с альпакой? Корги на дне рождения?\n"
    "Хаски для рекламной съёмки? — всё здесь!\n\n"
    "✨ <b>Для вас:</b>\n"
    "🔹 Проверенные животные с документами\n"
    "🔹 Сопровождение владельца и инструкции\n"
    "🔹 Заявка за 2 минуты прямо в боте\n\n"
    "💼 <b>Для владельцев питомцев:</b>\n"
    "Ваш любимец может «работать» и приносить доход в дом —\n"
    "от 45₪/час за фотосессии и праздники. Анкета — 3 минуты!\n\n"
    "🎁 <b>АКЦИЯ:</b> новым клиентам первая аренда —\n"
    "<b>без сервисного сбора 10%!</b>\n"
    "━━━━━━━━━━━━━━━━━━"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_TEXT, reply_markup=main_menu_keyboard(), parse_mode="HTML"
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "noop":
        return

    if data == "menu":
        await query.edit_message_text(
            "🐾 <b>PetShare Israel</b>\n\nВыберите, с чего начнём:",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    if data == "about":
        text = (
            "ℹ️ <b>Как это работает</b>\n\n"
            "1️⃣ Выбираете животное в каталоге\n"
            "2️⃣ Оставляете заявку прямо в боте\n"
            "3️⃣ Владелец подтверждает дату и время\n"
            "4️⃣ Встречаетесь и наслаждаетесь 🐾\n\n"
            "📋 У всех животных есть ветеринарные документы.\n"
            "🛡 Для крупных и экзотических животных — обязательное\n"
            "сопровождение владельца.\n\n"
            f"💳 К цене аренды добавляется сервисный сбор {int(CLIENT_FEE * 100)}%."
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🐾 Открыть каталог", callback_data="catalog")],
            [InlineKeyboardButton("🏠 Меню", callback_data="menu")],
        ])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data == "catalog":
        categories = sheets.get_categories()
        if not categories:
            await query.edit_message_text("Каталог пока пуст, загляните позже 🐾")
            return
        rows = [
            [InlineKeyboardButton(
                f"{CATEGORY_EMOJI.get(cat, '🐾')} {cat}",
                callback_data=f"card:{cat}:0",
            )]
            for cat in categories
        ]
        rows.append([InlineKeyboardButton("🏠 Меню", callback_data="menu")])
        await query.edit_message_text(
            "Выберите категорию:", reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("card:"):
        _, category, index_str = data.split(":", 2)
        animals = sheets.get_animals_by_category(category)
        if not animals:
            await query.edit_message_text("В этой категории пока нет животных 🐾")
            return
        index = int(index_str) % len(animals)
        animal = animals[index]
        await query.edit_message_text(
            format_card(animal, index + 1, len(animals)),
            reply_markup=card_keyboard(category, index, len(animals), animal.get("id", "")),
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
        rows = [[InlineKeyboardButton("Любой город", callback_data="f_city_set:any")]]
        rows += [
            [InlineKeyboardButton(f"📍 {c}", callback_data=f"f_city_set:{c}")]
            for c in sorted(cities)
        ]
        await query.edit_message_text(
            "Выберите город:", reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("f_city_set:"):
        context.user_data["filt_city"] = data.split(":", 1)[1]
        text, keyboard = filter_menu(context)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if data == "f_price":
        rows = [
            [InlineKeyboardButton(label, callback_data=f"f_price_set:{key}")]
            for key, (label, _) in PRICE_OPTIONS.items()
        ]
        await query.edit_message_text(
            "Выберите диапазон цены:", reply_markup=InlineKeyboardMarkup(rows)
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
                "По этим фильтрам ничего не нашлось 🐾\n\n" + text,
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
            "📩 Оставить заявку", callback_data=f"request:{animal.get('id', '')}"
        )])
        rows.append([
            InlineKeyboardButton("🔍 Фильтры", callback_data="filters"),
            InlineKeyboardButton("🏠 Меню", callback_data="menu"),
        ])
        await query.edit_message_text(
            format_card(animal, index + 1, total),
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="HTML",
        )
        return


# ---------- Сценарий заявки ----------

async def request_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Клиент нажал «Оставить заявку» под карточкой."""
    query = update.callback_query
    await query.answer()
    animal_id = query.data.split(":", 1)[1]
    animal = sheets.get_animal_by_id(animal_id)
    if not animal:
        await query.message.reply_text("Это животное сейчас недоступно 🐾")
        return ConversationHandler.END
    context.user_data["req_animal"] = animal
    await query.message.reply_text(
        f"📩 Заявка на «{animal.get('имя', '')}»\n\n"
        "На какую дату и время хотите арендовать?\n"
        "Например: <i>12.07 в 16:00</i>\n\n"
        "Отменить заявку — /cancel",
        parse_mode="HTML",
    )
    return REQ_DATE


async def request_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["req_date"] = update.message.text.strip()
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Отправить мой номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(
        "Отлично! Теперь оставьте номер телефона для связи —\n"
        "нажмите кнопку ниже или напишите номер вручную:",
        reply_markup=keyboard,
    )
    return REQ_PHONE


async def request_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
    context.user_data["req_phone"] = phone

    animal = context.user_data["req_animal"]
    price = parse_price(animal.get("цена_событие"))
    first_time = not sheets.client_has_requests(update.effective_user.id)
    context.user_data["req_first_time"] = first_time
    client_fee = compute_client_fee(price, first_time)
    total = price + client_fee

    if first_time:
        fee_line = "🎁 Сервисный сбор: <b>0₪</b> (акция для новых клиентов!)"
    else:
        fee_line = f"➕ Сервисный сбор ({int(CLIENT_FEE * 100)}%): {client_fee}₪"
    summary = (
        "Проверьте заявку:\n\n"
        f"🐾 Животное: <b>{animal.get('имя', '')}</b> ({animal.get('порода', '')})\n"
        f"📅 Дата: {context.user_data['req_date']}\n"
        f"📱 Телефон: {phone}\n\n"
        f"💰 Аренда: {price}₪\n"
        f"{fee_line}\n"
        f"<b>Итого: {total}₪</b>\n\n"
        "Оплата — после подтверждения владельцем."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Отправить заявку", callback_data="req_confirm")],
        [InlineKeyboardButton("❌ Отменить", callback_data="req_cancel")],
    ])
    await update.message.reply_text(
        summary, reply_markup=keyboard, parse_mode="HTML",
    )
    # Убираем клавиатуру с кнопкой контакта
    await update.message.reply_text("👆", reply_markup=ReplyKeyboardRemove())
    return REQ_CONFIRM


async def request_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "req_cancel":
        await query.edit_message_text("Заявка отменена. Возвращайтесь в каталог 🐾")
        context.user_data.clear()
        return ConversationHandler.END

    animal = context.user_data["req_animal"]
    user = update.effective_user
    price = parse_price(animal.get("цена_событие"))
    first_time = context.user_data.get("req_first_time", False)
    client_fee = compute_client_fee(price, first_time)
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
        "промо: первая аренда без сбора" if first_time else "",
        price,
        client_fee,
        owner_commission,
        platform_income,
    ])

    await query.edit_message_text(
        f"✅ Заявка <b>{req_id}</b> отправлена!\n\n"
        "Мы свяжемся с вами для подтверждения даты.\n"
        "Спасибо, что выбрали PetShare Israel 🐾",
        parse_mode="HTML",
    )

    # Уведомление администратору
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
        f"➕ Сбор с клиента (10%): {client_fee}₪"
        + (" 🎁 промо\n" if first_time else "\n") +
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

    context.user_data.clear()
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

    # Сообщаем клиенту
    client_id = str(request.get("клиент_tg_id", "")).strip()
    if not client_id.isdigit():
        return
    animal = sheets.get_animal_by_id(str(request.get("животное_id", "")).strip()) or {}
    owner = sheets.get_owner_by_id(str(animal.get("владелец_id", "")).strip()) or {}
    try:
        if action == "adm_ok":
            keyboard = None
            owner_wa = whatsapp_link(owner.get("whatsapp", ""))
            if owner_wa:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("💬 Написать владельцу в WhatsApp", url=owner_wa)]]
                )
            await context.bot.send_message(
                int(client_id),
                f"🎉 Ваша заявка <b>{req_id}</b> подтверждена!\n\n"
                f"🐾 {request.get('животное_имя', '')}\n"
                f"📅 {request.get('дата_аренды', '')}\n\n"
                "Свяжитесь с владельцем, чтобы договориться о деталях:",
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            await context.bot.send_message(
                int(client_id),
                f"😔 К сожалению, заявка <b>{req_id}</b> отклонена — "
                "выбранная дата недоступна.\n\n"
                "Загляните в каталог: возможно, подойдёт другое животное 🐾",
                parse_mode="HTML",
            )
    except Exception:
        logger.exception("Не удалось уведомить клиента по заявке %s", req_id)


async def request_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Заявка отменена. Возвращайтесь в каталог 🐾",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ---------- Анкета владельца («сдать питомца в аренду») ----------

async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["owner_flow"] = {}
    await query.message.reply_text(
        "💼 <b>Сдать питомца в аренду</b>\n\n"
        "Короткая анкета (2-3 минуты) — после неё администратор проверит "
        "данные и подключит вас к платформе.\n\n"
        "Как вас зовут?\n\nОтменить в любой момент — /cancel",
        parse_mode="HTML",
    )
    return OWN_NAME


async def owner_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["name"] = update.message.text.strip()
    await update.message.reply_text("Ваш номер телефона (можно тот же, что в WhatsApp)?")
    return OWN_PHONE


async def owner_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["phone"] = update.message.text.strip()
    await update.message.reply_text("В каком городе вы находитесь?")
    return OWN_CITY


async def owner_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["city"] = update.message.text.strip()
    await update.message.reply_text("Как зовут вашего питомца?")
    return PET_NAME


async def pet_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["pet_name"] = update.message.text.strip()
    rows = [
        [InlineKeyboardButton(f"{emoji} {cat}", callback_data=f"pc:{cat}")]
        for cat, emoji in CATEGORY_EMOJI.items()
    ]
    rows.append([InlineKeyboardButton("➕ Другая категория", callback_data="pc:__custom__")])
    await update.message.reply_text(
        "Выберите категорию:", reply_markup=InlineKeyboardMarkup(rows)
    )
    return PET_CATEGORY


async def pet_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.split(":", 1)[1]
    if category == "__custom__":
        await query.message.reply_text("Напишите категорию текстом:")
        return PET_CATEGORY_CUSTOM
    context.user_data["owner_flow"]["category"] = category
    await query.message.reply_text("Вид и порода? Например: Собака, Корги")
    return PET_BREED


async def pet_category_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["category"] = update.message.text.strip()
    await update.message.reply_text("Вид и порода? Например: Собака, Корги")
    return PET_BREED


async def pet_breed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = [p.strip() for p in update.message.text.split(",", 1)]
    context.user_data["owner_flow"]["species"] = parts[0]
    context.user_data["owner_flow"]["breed"] = parts[1] if len(parts) > 1 else parts[0]
    await update.message.reply_text("Сколько лет питомцу?")
    return PET_AGE


async def pet_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["age"] = update.message.text.strip()
    await update.message.reply_text("Опишите характер (например: дружелюбный, спокойный)")
    return PET_TEMPERAMENT


async def pet_temperament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["temperament"] = update.message.text.strip()
    await update.message.reply_text(
        "Что умеет / для чего подходит? (например: фотосессии, детские праздники)"
    )
    return PET_SKILLS


async def pet_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["skills"] = update.message.text.strip()
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Да", callback_data="kids:да"),
        InlineKeyboardButton("Нет", callback_data="kids:нет"),
    ]])
    await update.message.reply_text("Можно ли доверить питомца детям?", reply_markup=keyboard)
    return PET_KIDS


async def pet_kids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["owner_flow"]["kids"] = query.data.split(":", 1)[1]
    await query.message.reply_text("Желаемая цена за час аренды, ₪? (только число)")
    return PET_PRICE_HOUR


async def pet_price_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["price_hour"] = parse_price(update.message.text)
    await update.message.reply_text("Желаемая цена за мероприятие (несколько часов), ₪?")
    return PET_PRICE_EVENT


async def pet_price_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner_flow"]["price_event"] = parse_price(update.message.text)
    await update.message.reply_text("Пришлите фото питомца, или напишите «пропустить»:")
    return PET_PHOTO


async def pet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flow = context.user_data["owner_flow"]
    flow["photo"] = update.message.photo[-1].file_id if update.message.photo else ""

    summary = (
        "Проверьте анкету:\n\n"
        f"👤 Владелец: {flow['name']}, {flow['phone']}, {flow['city']}\n\n"
        f"🐾 {flow['pet_name']} — {flow['species']} ({flow['breed']}), {flow['age']}\n"
        f"📂 Категория: {flow['category']}\n"
        f"😊 Характер: {flow['temperament']}\n"
        f"⭐ Умеет: {flow['skills']}\n"
        f"👶 Можно детям: {flow['kids']}\n"
        f"💰 {flow['price_hour']}₪/час, {flow['price_event']}₪/мероприятие\n\n"
        "Отправить на проверку администратору?"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Отправить на проверку", callback_data="pet_send")],
        [InlineKeyboardButton("❌ Отмена", callback_data="pet_cancel")],
    ])
    if flow["photo"]:
        await update.message.reply_photo(flow["photo"], caption=summary, reply_markup=keyboard)
    else:
        await update.message.reply_text(summary, reply_markup=keyboard)
    return PET_CONFIRM


async def pet_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pet_cancel":
        await query.message.reply_text("Анкета отменена.")
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

    await query.message.reply_text(
        "✅ Анкета отправлена на проверку! Мы свяжемся с вами после одобрения 🐾"
    )

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
    await update.message.reply_text("Анкета отменена.", reply_markup=ReplyKeyboardRemove())
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
    try:
        if action == "own_ok":
            sheets.update_owner_status(owner.get("id", ""), "проверен")
            await context.bot.send_message(
                int(owner_tg),
                f"🎉 Ваш питомец «{animal.get('имя', '')}» одобрен и уже в каталоге "
                "PetShare Israel!",
            )
        else:
            await context.bot.send_message(
                int(owner_tg),
                f"😔 Анкета на «{animal.get('имя', '')}» отклонена. "
                "Свяжитесь с нами, чтобы уточнить детали.",
            )
    except Exception:
        logger.exception("Не удалось уведомить владельца %s", owner_tg)


async def cmd_reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс кэша таблицы (только для администратора)."""
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        return
    sheets.clear_cache()
    await update.message.reply_text("♻️ Кэш сброшен, данные перечитаются из таблицы.")


async def on_error(update, context):
    logger.exception("Ошибка при обработке апдейта", exc_info=context.error)


def main():
    if not config.BOT_TOKEN:
        raise SystemExit("Не задан PETSHARE_BOT_TOKEN в .env")
    app = Application.builder().token(config.BOT_TOKEN).build()

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
        entry_points=[CallbackQueryHandler(owner_start, pattern=r"^owner_start$")],
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

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("reload", cmd_reload))
    app.add_handler(request_conv)
    app.add_handler(owner_conv)
    app.add_handler(CallbackQueryHandler(admin_decision, pattern=r"^adm_(ok|no):"))
    app.add_handler(CallbackQueryHandler(admin_owner_decision, pattern=r"^own_(ok|no):"))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_error_handler(on_error)
    logger.info("Бот PetShare Israel запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
