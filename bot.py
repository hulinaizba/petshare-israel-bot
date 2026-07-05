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


def parse_price(value):
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return 0


def whatsapp_link(phone):
    """Превращает номер в ссылку wa.me (оставляет только цифры)."""
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    return f"https://wa.me/{digits}" if digits else ""


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🐾 Каталог животных", callback_data="catalog")],
        [InlineKeyboardButton("ℹ️ Как это работает", callback_data="about")],
    ])


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


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🐾 <b>PetShare Israel</b>\n\n"
        "Аренда животных для фотосессий, праздников и хорошего настроения:\n"
        "собаки, кошки, попугаи, кролики, альпаки и не только.\n\n"
        "Все животные проверены, с документами и страховкой.\n"
        "Выберите, с чего начнём:"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


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
    client_fee = round(price * CLIENT_FEE)
    total = price + client_fee

    summary = (
        "Проверьте заявку:\n\n"
        f"🐾 Животное: <b>{animal.get('имя', '')}</b> ({animal.get('порода', '')})\n"
        f"📅 Дата: {context.user_data['req_date']}\n"
        f"📱 Телефон: {phone}\n\n"
        f"💰 Аренда: {price}₪\n"
        f"➕ Сервисный сбор ({int(CLIENT_FEE * 100)}%): {client_fee}₪\n"
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
    client_fee = round(price * CLIENT_FEE)
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

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("reload", cmd_reload))
    app.add_handler(request_conv)
    app.add_handler(CallbackQueryHandler(admin_decision, pattern=r"^adm_(ok|no):"))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_error_handler(on_error)
    logger.info("Бот PetShare Israel запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
