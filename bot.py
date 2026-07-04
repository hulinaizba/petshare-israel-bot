"""Telegram-бот PetShare Israel: каталог животных для аренды.

Запуск: ./venv/bin/python bot.py
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
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
            "сопровождение владельца.\n"
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

    if data.startswith("request:"):
        animal_id = data.split(":", 1)[1]
        animal = sheets.get_animal_by_id(animal_id)
        name = animal.get("имя", "") if animal else animal_id
        await query.message.reply_text(
            f"📩 Заявка на «{name}» — этот раздел подключим на следующем шаге.\n"
            "Пока можно полистать каталог 🐾"
        )
        return


async def cmd_reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс кэша таблицы (только для администратора)."""
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        return
    sheets.clear_cache()
    await update.message.reply_text("♻️ Кэш сброшен, данные перечитаются из таблицы.")


def main():
    if not config.BOT_TOKEN:
        raise SystemExit("Не задан PETSHARE_BOT_TOKEN в .env")
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("reload", cmd_reload))
    app.add_handler(CallbackQueryHandler(on_callback))
    logger.info("Бот PetShare Israel запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
