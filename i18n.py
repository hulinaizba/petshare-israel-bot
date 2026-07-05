"""Переводы интерфейса бота: русский / английский / иврит.

Использование: t("ключ", lang) или t("ключ", lang, name="Луна").
Если перевода нет — возвращается русский текст.
"""

LANGS = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "he": "🇮🇱 עברית",
}

DEFAULT_LANG = "ru"

T = {
    # ---------- Общее ----------
    "choose_lang": {
        "ru": "🌐 Выберите язык:",
        "en": "🌐 Choose your language:",
        "he": "🌐 בחרו שפה:",
    },
    # Первое знакомство: человек ещё не выбрал язык, поэтому текст на всех трёх
    "choose_lang_first": {
        "ru": (
            "╔═══════════════════╗\n"
            "   🐶  🐱  🦜  🐰  🦙  🐴\n"
            "   ✨ <b>P E T S H A R E</b> ✨\n"
            "   🇮🇱 <b>I S R A E L</b> 🇮🇱\n"
            "   🐾 ─────────────── 🐾\n"
            "   <i>walk • play • love</i>\n"
            "╚═══════════════════╝\n\n"
            "🇮🇱 1️⃣ ?באיזו שפה נמשיך\n"
            "🇷🇺 2️⃣ На каком языке продолжим?\n"
            "🇬🇧 3️⃣ Which language shall we continue in?\n\n"
            "👇 👇 👇"
        ),
        "en": (
            "🇮🇱 1️⃣ ?באיזו שפה נמשיך\n"
            "🇷🇺 2️⃣ На каком языке продолжим?\n"
            "🇬🇧 3️⃣ Which language shall we continue in?"
        ),
        "he": (
            "🇮🇱 1️⃣ ?באיזו שפה נמשיך\n"
            "🇷🇺 2️⃣ На каком языке продолжим?\n"
            "🇬🇧 3️⃣ Which language shall we continue in?"
        ),
    },
    "use_buttons": {
        "ru": "☝️ Пожалуйста, нажмите одну из кнопок выше 🙂",
        "en": "☝️ Please tap one of the buttons above 🙂",
        "he": "☝️ אנא לחצו על אחד הכפתורים למעלה 🙂",
    },
    "fallback_msg": {
        "ru": "🤔 Я не понял сообщение. Вот главное меню:",
        "en": "🤔 I didn't understand that. Here is the main menu:",
        "he": "🤔 לא הבנתי את ההודעה. הנה התפריט הראשי:",
    },
    "nothing_to_cancel": {
        "ru": "Сейчас нечего отменять 🙂 Вот меню:",
        "en": "Nothing to cancel right now 🙂 Here is the menu:",
        "he": "אין מה לבטל כרגע 🙂 הנה התפריט:",
    },
    "cant_self": {
        "ru": "Нельзя предложить знакомство собственному питомцу 😄 Выберите другую анкету!",
        "en": "You can't propose a meeting to your own pet 😄 Choose another profile!",
        "he": "אי אפשר להציע היכרות לחיית המחמד של עצמכם 😄 בחרו פרופיל אחר!",
    },

    # ---------- Сообщения через бота ----------
    "btn_ask": {"ru": "✉️ Задать вопрос", "en": "✉️ Ask a question", "he": "✉️ לשאול שאלה"},
    "ask_intro": {
        "ru": "✉️ Ваш вопрос о «{name}» — напишите одним сообщением:\n\nОтменить — /cancel",
        "en": "✉️ Your question about “{name}” — write it in one message:\n\nCancel — /cancel",
        "he": "✉️ השאלה שלכם על «{name}» — כתבו בהודעה אחת:\n\nלביטול — /cancel",
    },
    "msg_sent": {
        "ru": "✅ Сообщение отправлено! Ответ придёт прямо сюда, в бот 💬",
        "en": "✅ Message sent! The reply will arrive right here in the bot 💬",
        "he": "✅ ההודעה נשלחה! התשובה תגיע ישירות לכאן, לבוט 💬",
    },
    "btn_reply": {"ru": "💬 Ответить", "en": "💬 Reply", "he": "💬 להשיב"},
    "incoming_msg": {
        "ru": "💬 <b>Сообщение по теме «{label}»</b>\n\n{text}",
        "en": "💬 <b>Message about “{label}”</b>\n\n{text}",
        "he": "💬 <b>הודעה בנושא «{label}»</b>\n\n{text}",
    },
    "reply_intro": {
        "ru": "💬 Напишите ответ одним сообщением:\n\nОтменить — /cancel",
        "en": "💬 Write your reply in one message:\n\nCancel — /cancel",
        "he": "💬 כתבו את התשובה בהודעה אחת:\n\nלביטול — /cancel",
    },
    "reply_label": {"ru": "ответ", "en": "reply", "he": "תשובה"},
    "btn_wish": {"ru": "💡 Не нашли? Напишите нам", "en": "💡 Can't find it? Tell us", "he": "💡 לא מצאתם? כתבו לנו"},
    "wish_intro": {
        "ru": "💡 Напишите, кого или что вы ищете (животное, услугу, дату, город) — мы постараемся найти:\n\nОтменить — /cancel",
        "en": "💡 Tell us who or what you are looking for (animal, service, date, city) — we will try to find it:\n\nCancel — /cancel",
        "he": "💡 כתבו מי או מה אתם מחפשים (בעל חיים, שירות, תאריך, עיר) — ננסה למצוא:\n\nלביטול — /cancel",
    },
    "wish_sent": {
        "ru": "✅ Спасибо! Мы получили ваше пожелание и свяжемся с вами 🐾",
        "en": "✅ Thank you! We received your request and will contact you 🐾",
        "he": "✅ תודה! קיבלנו את הבקשה וניצור קשר 🐾",
    },

    # ---------- Конные прогулки ----------
    "btn_horses": {"ru": "🐴 Конные прогулки", "en": "🐴 Horse rides", "he": "🐴 רכיבה על סוסים"},
    "horses_menu": {
        "ru": (
            "🐴 <b>Конные прогулки</b>\n\n"
            "🌅 Прогулка на рассвете, ☀️ днём или 🌇 на закате —\n"
            "время подберём под вас, всегда в сопровождении владельца.\n"
            "Подходит и новичкам, и опытным наездникам.\n\n"
            "🐎 А если у вас есть лошадь — зарегистрируйте её\n"
            "и зарабатывайте на прогулках!"
        ),
        "en": (
            "🐴 <b>Horse rides</b>\n\n"
            "🌅 A ride at dawn, ☀️ midday or 🌇 at sunset —\n"
            "we adjust the time for you, always with the owner along.\n"
            "Great for beginners and experienced riders alike.\n\n"
            "🐎 And if you have a horse — register it\n"
            "and earn on rides!"
        ),
        "he": (
            "🐴 <b>רכיבה על סוסים</b>\n\n"
            "🌅 רכיבה בזריחה, ☀️ בצהריים או 🌇 בשקיעה —\n"
            "נתאים את הזמן בשבילכם, תמיד בליווי הבעלים.\n"
            "מתאים למתחילים ולרוכבים מנוסים.\n\n"
            "🐎 ואם יש לכם סוס — רשמו אותו\n"
            "והרוויחו על רכיבות!"
        ),
    },
    "btn_ride_book": {"ru": "🌅 Записаться на прогулку", "en": "🌅 Book a ride", "he": "🌅 להירשם לרכיבה"},
    "btn_reg_horse": {"ru": "🐎 Зарегистрировать свою лошадь", "en": "🐎 Register your horse", "he": "🐎 לרשום את הסוס שלכם"},
    "btn_horses_list": {"ru": "🐴 Смотреть лошадей", "en": "🐴 Browse horses", "he": "🐴 לצפות בסוסים"},
    "horses_empty": {
        "ru": "Лошадей в каталоге пока нет — загляните позже 🐴",
        "en": "No horses in the catalog yet — come back later 🐴",
        "he": "אין עדיין סוסים בקטלוג — חזרו מאוחר יותר 🐴",
    },
    "hrs_intro": {
        "ru": (
            "🐎 <b>Регистрация лошади для прогулок</b>\n\n"
            "Все прогулки проходят в вашем сопровождении, цену назначаете вы.\n"
            f"Комиссия сервиса — 20% с состоявшихся прогулок,\n"
            "клиент дополнительно платит сервисный сбор 10%.\n\n"
            "Как вас зовут?\n\nОтменить — /cancel"
        ),
        "en": (
            "🐎 <b>Register your horse for rides</b>\n\n"
            "All rides happen with you accompanying, you set the price.\n"
            "Service commission — 20% of completed rides,\n"
            "the client additionally pays a 10% service fee.\n\n"
            "What is your name?\n\nCancel — /cancel"
        ),
        "he": (
            "🐎 <b>רישום סוס לרכיבות</b>\n\n"
            "כל הרכיבות בליווי שלכם, אתם קובעים את המחיר.\n"
            "עמלת השירות — 20% מרכיבות שהתקיימו,\n"
            "הלקוח משלם בנוסף עמלת שירות של 10%.\n\n"
            "איך קוראים לכם?\n\nלביטול — /cancel"
        ),
    },
    "hrs_ask_horsename": {"ru": "Кличка лошади?", "en": "Your horse's name?", "he": "שם הסוס?"},
    "hrs_ask_breed": {"ru": "Порода лошади?", "en": "Horse breed?", "he": "גזע הסוס?"},
    "hrs_ask_city": {
        "ru": "Где проходят прогулки? (город/ферма/конюшня)",
        "en": "Where do the rides take place? (city/farm/stable)",
        "he": "איפה מתקיימות הרכיבות? (עיר/חווה/אורווה)",
    },
    "hrs_ask_character": {
        "ru": "Характер лошади? (например: спокойная, привыкла к новичкам)",
        "en": "The horse's character? (e.g.: calm, used to beginners)",
        "he": "האופי של הסוס? (לדוגמה: רגוע, רגיל למתחילים)",
    },
    "hrs_ask_beginners": {
        "ru": "Подходит ли лошадь новичкам без опыта?",
        "en": "Is the horse suitable for beginners?",
        "he": "האם הסוס מתאים למתחילים?",
    },
    "hrs_ask_price_hour": {
        "ru": "Цена за час прогулки с человека, ₪? (только число)",
        "en": "Price per hour per person, ₪? (number only)",
        "he": "מחיר לשעה לאדם, ₪? (מספר בלבד)",
    },
    "hrs_ask_price_sunset": {
        "ru": "Цена за закатную/рассветную прогулку с человека, ₪? (обычно дороже — это самый популярный формат 🌇)",
        "en": "Price for a sunset/dawn ride per person, ₪? (usually higher — the most popular format 🌇)",
        "he": "מחיר לרכיבת שקיעה/זריחה לאדם, ₪? (בדרך כלל יקר יותר — הפורמט המבוקש ביותר 🌇)",
    },
    "hrs_summary": {
        "ru": (
            "Проверьте анкету лошади:\n\n"
            "👤 Владелец: {name}, {phone}\n"
            "🐴 {horse_name} — {breed}, возраст: {age}\n"
            "📍 {city}\n"
            "😊 {character}\n"
            "🔰 Подходит новичкам: {beginners}\n"
            "💰 {price_hour}₪/час с человека | 🌇 закат: {price_sunset}₪\n\n"
            "💳 Напоминание: комиссия сервиса 20% с состоявшихся прогулок.\n\n"
            "Отправить на проверку?"
        ),
        "en": (
            "Please check the horse profile:\n\n"
            "👤 Owner: {name}, {phone}\n"
            "🐴 {horse_name} — {breed}, age: {age}\n"
            "📍 {city}\n"
            "😊 {character}\n"
            "🔰 Beginner-friendly: {beginners}\n"
            "💰 {price_hour}₪/hour per person | 🌇 sunset: {price_sunset}₪\n\n"
            "💳 Reminder: 20% service commission on completed rides.\n\n"
            "Send for review?"
        ),
        "he": (
            "בדקו את פרופיל הסוס:\n\n"
            "👤 בעלים: {name}, {phone}\n"
            "🐴 {horse_name} — {breed}, גיל: {age}\n"
            "📍 {city}\n"
            "😊 {character}\n"
            "🔰 מתאים למתחילים: {beginners}\n"
            "💰 {price_hour}₪ לשעה לאדם | 🌇 שקיעה: {price_sunset}₪\n\n"
            "💳 תזכורת: עמלת שירות 20% מרכיבות שהתקיימו.\n\n"
            "לשלוח לבדיקה?"
        ),
    },
    "hrs_approved": {
        "ru": "🎉 Лошадь «{name}» одобрена и уже в каталоге прогулок!",
        "en": "🎉 Horse “{name}” is approved and already in the rides catalog!",
        "he": "🎉 הסוס «{name}» אושר וכבר בקטלוג הרכיבות!",
    },
    "hrs_declined": {
        "ru": "😔 Анкета лошади «{name}» отклонена. Свяжитесь с нами для деталей.",
        "en": "😔 The profile of horse “{name}” was declined. Contact us for details.",
        "he": "😔 הפרופיל של הסוס «{name}» נדחה. צרו קשר לפרטים.",
    },
    "hrs_card_beginners": {"ru": "Подходит новичкам", "en": "Beginner-friendly", "he": "מתאים למתחילים"},
    "hrs_card_hour": {"ru": "час с человека", "en": "hour per person", "he": "שעה לאדם"},
    "hrs_card_sunset": {"ru": "закат/рассвет", "en": "sunset/dawn", "he": "שקיעה/זריחה"},
    "btn_book_this": {"ru": "🌅 Записаться", "en": "🌅 Book", "he": "🌅 להירשם"},

    # Заявка на прогулку
    "rid_ask_time": {
        "ru": "🐴 Запись на прогулку с «{name}»\n\nКакое время суток вам подходит?",
        "en": "🐴 Booking a ride with “{name}”\n\nWhat time of day suits you?",
        "he": "🐴 הרשמה לרכיבה עם «{name}»\n\nאיזה זמן ביום מתאים לכם?",
    },
    "btn_dawn": {"ru": "🌅 Рассвет", "en": "🌅 Dawn", "he": "🌅 זריחה"},
    "btn_day": {"ru": "☀️ День", "en": "☀️ Daytime", "he": "☀️ יום"},
    "btn_sunset": {"ru": "🌇 Закат", "en": "🌇 Sunset", "he": "🌇 שקיעה"},
    "btn_evening": {"ru": "🌙 Вечер", "en": "🌙 Evening", "he": "🌙 ערב"},
    "tod_рассвет": {"ru": "рассвет", "en": "dawn", "he": "זריחה"},
    "tod_день": {"ru": "день", "en": "daytime", "he": "יום"},
    "tod_закат": {"ru": "закат", "en": "sunset", "he": "שקיעה"},
    "tod_вечер": {"ru": "вечер", "en": "evening", "he": "ערב"},
    "rid_ask_date": {
        "ru": "На какую дату? Точное время обговорим и подтвердим 🕐\nНапример: <i>20.07 или «ближайшие выходные»</i>",
        "en": "What date? We will agree on the exact time later 🕐\nFor example: <i>20.07 or “next weekend”</i>",
        "he": "לאיזה תאריך? את השעה המדויקת נתאם ונאשר 🕐\nלדוגמה: <i>20.07 או «סוף השבוע הקרוב»</i>",
    },
    "rid_ask_people": {
        "ru": "Сколько человек поедет? (только число)",
        "en": "How many people will ride? (number only)",
        "he": "כמה אנשים ירכבו? (מספר בלבד)",
    },
    "rid_ask_exp": {
        "ru": "Какой у вас опыт верховой езды?",
        "en": "What is your riding experience?",
        "he": "מה ניסיון הרכיבה שלכם?",
    },
    "btn_beginner": {"ru": "🔰 Новичок", "en": "🔰 Beginner", "he": "🔰 מתחיל"},
    "btn_experienced": {"ru": "🏇 Опытный", "en": "🏇 Experienced", "he": "🏇 מנוסה"},
    "exp_новичок": {"ru": "новичок", "en": "beginner", "he": "מתחיל"},
    "exp_опытный": {"ru": "опытный", "en": "experienced", "he": "מנוסה"},
    "rid_ask_wishes": {
        "ru": "Особые пожелания? 📸 Фотосессия, пикник, сюрприз для второй половинки...\nЕсли нет — напишите «нет»",
        "en": "Special wishes? 📸 A photo shoot, picnic, surprise for a loved one...\nIf none — type “no”",
        "he": "בקשות מיוחדות? 📸 צילומים, פיקניק, הפתעה לבן/בת הזוג...\nאם אין — כתבו «אין»",
    },
    "rid_summary": {
        "ru": (
            "Проверьте заявку на прогулку:\n\n"
            "🐴 Лошадь: <b>{horse}</b>\n"
            "🕐 Время суток: {tod}\n"
            "📅 Дата: {date} (точное время подтвердим)\n"
            "👥 Человек: {people}\n"
            "🏇 Опыт: {exp}\n"
            "📝 Пожелания: {wishes}\n"
            "📱 Телефон: {phone}\n\n"
            "💰 {people} × {price}₪ = {cost}₪\n"
            "➕ Сервисный сбор (10%): {fee}₪\n"
            "<b>Итого: {total}₪</b>\n\n"
            "Оплата — после подтверждения."
        ),
        "en": (
            "Please check your ride request:\n\n"
            "🐴 Horse: <b>{horse}</b>\n"
            "🕐 Time of day: {tod}\n"
            "📅 Date: {date} (exact time to be confirmed)\n"
            "👥 People: {people}\n"
            "🏇 Experience: {exp}\n"
            "📝 Wishes: {wishes}\n"
            "📱 Phone: {phone}\n\n"
            "💰 {people} × {price}₪ = {cost}₪\n"
            "➕ Service fee (10%): {fee}₪\n"
            "<b>Total: {total}₪</b>\n\n"
            "Payment — after confirmation."
        ),
        "he": (
            "בדקו את בקשת הרכיבה:\n\n"
            "🐴 סוס: <b>{horse}</b>\n"
            "🕐 זמן ביום: {tod}\n"
            "📅 תאריך: {date} (השעה המדויקת תאושר)\n"
            "👥 אנשים: {people}\n"
            "🏇 ניסיון: {exp}\n"
            "📝 בקשות: {wishes}\n"
            "📱 טלפון: {phone}\n\n"
            "💰 {people} × {price}₪ = {cost}₪\n"
            "➕ עמלת שירות (10%): {fee}₪\n"
            "<b>סה\"כ: {total}₪</b>\n\n"
            "התשלום — לאחר האישור."
        ),
    },
    "rid_sent": {
        "ru": "✅ Заявка <b>{id}</b> отправлена!\n\nВладелец подтвердит дату, и мы согласуем точное время 🐴",
        "en": "✅ Request <b>{id}</b> sent!\n\nThe owner will confirm the date and we will agree on the exact time 🐴",
        "he": "✅ הבקשה <b>{id}</b> נשלחה!\n\nהבעלים יאשר את התאריך ונתאם את השעה המדויקת 🐴",
    },
    "cli_rid_confirmed": {
        "ru": "🎉 Прогулка <b>{id}</b> подтверждена!\n\n🐴 {horse}, {date} ({tod})\n\nСвяжитесь с владельцем, чтобы согласовать точное время и место встречи:",
        "en": "🎉 Ride <b>{id}</b> confirmed!\n\n🐴 {horse}, {date} ({tod})\n\nContact the owner to agree on the exact time and meeting point:",
        "he": "🎉 הרכיבה <b>{id}</b> אושרה!\n\n🐴 {horse}, {date} ({tod})\n\nצרו קשר עם הבעלים לתיאום השעה ומקום המפגש:",
    },
    "cli_rid_declined": {
        "ru": "😔 К сожалению, прогулка <b>{id}</b> не подтверждена — дата занята.\n\nПопробуйте другую дату или другую лошадь 🐴",
        "en": "😔 Unfortunately, ride <b>{id}</b> was not confirmed — the date is taken.\n\nTry another date or another horse 🐴",
        "he": "😔 לצערנו הרכיבה <b>{id}</b> לא אושרה — התאריך תפוס.\n\nנסו תאריך אחר או סוס אחר 🐴",
    },

    # ---------- Мои заявки ----------
    "btn_my": {"ru": "📋 Мои заявки", "en": "📋 My requests", "he": "📋 הבקשות שלי"},
    "my_title": {"ru": "📋 <b>Мои заявки</b>", "en": "📋 <b>My requests</b>", "he": "📋 <b>הבקשות שלי</b>"},
    "my_empty": {
        "ru": "У вас пока нет заявок. Загляните в каталог 🐾",
        "en": "You have no requests yet. Check the catalog 🐾",
        "he": "אין לכם עדיין בקשות. הציצו בקטלוג 🐾",
    },
    "my_rentals": {"ru": "🐾 Аренда", "en": "🐾 Rentals", "he": "🐾 השכרות"},
    "my_boardings": {"ru": "🏡 Передержка", "en": "🏡 Boarding", "he": "🏡 פנסיון"},
    "my_rides": {"ru": "🐴 Прогулки", "en": "🐴 Rides", "he": "🐴 רכיבות"},
    "my_matches": {"ru": "💞 Знакомства", "en": "💞 Meetings", "he": "💞 היכרויות"},

    # ---------- Отзывы ----------
    "review_pick": {
        "ru": "⭐ <b>Оставить отзыв</b>\n\nВыберите, о чём хотите рассказать:",
        "en": "⭐ <b>Leave a review</b>\n\nChoose what you want to review:",
        "he": "⭐ <b>להשאיר ביקורת</b>\n\nבחרו על מה תרצו לספר:",
    },
    "review_none": {
        "ru": "Отзыв можно оставить после подтверждённой сделки. Пока таких нет 🐾",
        "en": "You can leave a review after a confirmed booking. None yet 🐾",
        "he": "אפשר להשאיר ביקורת אחרי הזמנה מאושרת. עדיין אין כאלה 🐾",
    },
    "review_rate": {
        "ru": "Оцените от 1 до 5 звёзд:",
        "en": "Rate from 1 to 5 stars:",
        "he": "דרגו מ-1 עד 5 כוכבים:",
    },
    "review_text": {
        "ru": "Напишите пару слов — что понравилось, что можно улучшить?",
        "en": "Write a few words — what did you like, what could be better?",
        "he": "כתבו כמה מילים — מה אהבתם, מה אפשר לשפר?",
    },
    "review_saved": {
        "ru": "🙏 Спасибо за отзыв! Он поможет другим выбрать 🐾",
        "en": "🙏 Thank you for the review! It will help others choose 🐾",
        "he": "🙏 תודה על הביקורת! היא תעזור לאחרים לבחור 🐾",
    },
    "lang_set": {
        "ru": "✅ Язык переключён на русский.",
        "en": "✅ Language switched to English.",
        "he": "✅ השפה הוחלפה לעברית.",
    },
    "menu_short": {
        "ru": "🐾 <b>PetShare Israel</b>\n\nВыберите, с чего начнём:",
        "en": "🐾 <b>PetShare Israel</b>\n\nWhere shall we start?",
        "he": "🐾 <b>PetShare Israel</b>\n\nמאיפה נתחיל?",
    },

    # ---------- Кнопки меню ----------
    "btn_catalog": {"ru": "🐾 Каталог животных", "en": "🐾 Animal catalog", "he": "🐾 קטלוג בעלי חיים"},
    "btn_filters": {"ru": "🔍 Подбор по фильтрам", "en": "🔍 Search with filters", "he": "🔍 חיפוש לפי מסננים"},
    "btn_owner": {"ru": "💼 Сдать питомца в аренду", "en": "💼 List your pet for rent", "he": "💼 להשכיר את חיית המחמד"},
    "btn_about": {"ru": "ℹ️ Как это работает", "en": "ℹ️ How it works", "he": "ℹ️ איך זה עובד"},
    "btn_lang": {"ru": "🌐 Язык / Language / שפה", "en": "🌐 Язык / Language / שפה", "he": "🌐 Язык / Language / שפה"},
    "btn_menu": {"ru": "🏠 Меню", "en": "🏠 Menu", "he": "🏠 תפריט"},
    "btn_categories": {"ru": "🔙 Категории", "en": "🔙 Categories", "he": "🔙 קטגוריות"},
    "btn_request": {"ru": "📩 Оставить заявку", "en": "📩 Send a request", "he": "📩 לשלוח בקשה"},
    "btn_open_catalog": {"ru": "🐾 Открыть каталог", "en": "🐾 Open catalog", "he": "🐾 לפתוח קטלוג"},
    "btn_fill_form": {"ru": "💼 Заполнить анкету питомца", "en": "💼 Fill in the pet form", "he": "💼 למלא שאלון לחיית המחמד"},

    # ---------- Приветствие ----------
    "welcome": {
        "ru": (
            "🐾 <b>PetShare Israel</b>\n"
            "<i>Время с животными — без забот владения</i>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🚶 Погулять с собакой, о которой давно мечтаете?\n"
            "🐴 Покататься на лошади на закате?\n"
            "🤔 Понять, ваша ли это порода, до покупки щенка?\n"
            "📸 Фотосессия с альпакой или праздник с корги?\n\n"
            "Всё это — здесь, за пару кликов!\n\n"
            "✨ <b>Для вас:</b>\n"
            "🔹 Проверенные животные с документами\n"
            "🔹 Владелец рядом, инструкции и поддержка\n"
            "🔹 Заявка за 2 минуты прямо в боте\n\n"
            "💼 <b>Для владельцев питомцев:</b>\n"
            "Ваш любимец может «работать» и приносить доход в дом.\n"
            "Цену назначаете вы. Анкета — 3 минуты!\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        "en": (
            "🐾 <b>PetShare Israel</b>\n"
            "<i>Time with animals — without the worries of ownership</i>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🚶 Walk a dog you have always dreamed of?\n"
            "🐴 Ride a horse at sunset?\n"
            "🤔 Try a breed before buying a puppy?\n"
            "📸 A photo shoot with an alpaca or a party with a corgi?\n\n"
            "All of it — here, in a couple of taps!\n\n"
            "✨ <b>For you:</b>\n"
            "🔹 Verified animals with documents\n"
            "🔹 Owner nearby, instructions and support\n"
            "🔹 A request takes 2 minutes right in the bot\n\n"
            "💼 <b>For pet owners:</b>\n"
            "Your pet can “work” and bring income home.\n"
            "You set the price. The form takes 3 minutes!\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        "he": (
            "🐾 <b>PetShare Israel</b>\n"
            "<i>זמן עם בעלי חיים — בלי דאגות של בעלות</i>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🚶 לטייל עם כלב שתמיד חלמתם עליו?\n"
            "🐴 לרכוב על סוס בשקיעה?\n"
            "🤔 להכיר גזע לפני שקונים גור?\n"
            "📸 צילומים עם אלפקה או מסיבה עם קורגי?\n\n"
            "הכל כאן — בכמה לחיצות!\n\n"
            "✨ <b>בשבילכם:</b>\n"
            "🔹 בעלי חיים מאומתים עם מסמכים\n"
            "🔹 הבעלים לידכם, הנחיות ותמיכה\n"
            "🔹 בקשה תוך 2 דקות ישירות בבוט\n\n"
            "💼 <b>לבעלי חיות מחמד:</b>\n"
            "חיית המחמד שלכם יכולה «לעבוד» ולהכניס הכנסה הביתה.\n"
            "אתם קובעים את המחיר. השאלון — 3 דקות!\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
    },

    # ---------- Как это работает ----------
    "about": {
        "ru": (
            "ℹ️ <b>Как это работает</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💼 <b>Ваш питомец может работать!</b>\n\n"
            "Да-да, домашние животные тоже могут приносить доход в дом 😄\n"
            "Людям нужны не только съёмки — им нужны эмоции и общение\n"
            "с животными, которых у них нет:\n\n"
            "🚶 <b>Прогулки</b> — с вашей собакой погуляет тот,\n"
            "кто мечтает о такой же, но не может завести\n"
            "🤔 <b>«Тест-драйв породы»</b> — человек сомневается,\n"
            "заводить ли щенка. Знакомится с вашим питомцем —\n"
            "и принимает взвешенное решение\n"
            "🐴 <b>Конные прогулки</b> — катание и фото с лошадьми\n"
            "📸 <b>События</b> — фотосессии, детские праздники,\n"
            "свадьбы, реклама\n\n"
            "Цену назначаете вы сами — за час или за событие.\n\n"
            "Как начать:\n"
            "1️⃣ Заполняете анкету в боте — 3 минуты\n"
            "2️⃣ Мы проверяем данные и документы (прививки, ветпаспорт)\n"
            "3️⃣ Питомец появляется в каталоге\n"
            "4️⃣ Получаете заявки и зарабатываете 💰\n\n"
            "Вы всегда рядом со своим питомцем, все условия — по договору,\n"
            "комиссия платформы 20% только с состоявшихся аренд.\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🐾 <b>Хотите провести время с животным?</b>\n\n"
            "Не только «для дела» — можно просто для души:\n"
            "🔹 погулять с собакой, о которой мечтаете\n"
            "🔹 покататься на лошади\n"
            "🔹 «примерить» породу перед покупкой щенка\n"
            "🔹 устроить праздник, фотосессию или сюрприз близким\n\n"
            "1️⃣ Выбираете в каталоге или через фильтры\n"
            "2️⃣ Оставляете заявку прямо в боте\n"
            "3️⃣ Владелец подтверждает дату и время\n"
            "4️⃣ Встречаетесь и наслаждаетесь 🐾\n\n"
            "📋 У всех животных есть ветеринарные документы.\n"
            "🛡 Для крупных и экзотических — сопровождение владельца.\n"
            "💳 К цене аренды добавляется сервисный сбор 10%."
        ),
        "en": (
            "ℹ️ <b>How it works</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💼 <b>Your pet can work!</b>\n\n"
            "Yes — pets can bring income home too 😄\n"
            "People need more than photo shoots: they want emotions\n"
            "and time with animals they don't have:\n\n"
            "🚶 <b>Walks</b> — someone who dreams of a dog like yours\n"
            "but can't have one will gladly walk with it\n"
            "🤔 <b>“Breed test-drive”</b> — someone is unsure about\n"
            "getting a puppy. They meet your pet —\n"
            "and make an informed decision\n"
            "🐴 <b>Horse rides</b> — riding and photos with horses\n"
            "📸 <b>Events</b> — photo shoots, kids' parties,\n"
            "weddings, advertising\n\n"
            "You set the price yourself — per hour or per event.\n\n"
            "How to start:\n"
            "1️⃣ Fill in the form in the bot — 3 minutes\n"
            "2️⃣ We verify the data and documents (vaccinations, vet passport)\n"
            "3️⃣ Your pet appears in the catalog\n"
            "4️⃣ You receive requests and earn 💰\n\n"
            "You are always next to your pet, everything is under contract,\n"
            "the platform fee is 20% only on completed rentals.\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🐾 <b>Want to spend time with an animal?</b>\n\n"
            "Not only “for business” — just for the soul:\n"
            "🔹 walk a dog you dream about\n"
            "🔹 ride a horse\n"
            "🔹 “try on” a breed before buying a puppy\n"
            "🔹 arrange a party, a photo shoot or a surprise\n\n"
            "1️⃣ Choose in the catalog or with filters\n"
            "2️⃣ Send a request right in the bot\n"
            "3️⃣ The owner confirms date and time\n"
            "4️⃣ Meet and enjoy 🐾\n\n"
            "📋 All animals have veterinary documents.\n"
            "🛡 Large and exotic animals come with the owner.\n"
            "💳 A 10% service fee is added to the rental price."
        ),
        "he": (
            "ℹ️ <b>איך זה עובד</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💼 <b>חיית המחמד שלכם יכולה לעבוד!</b>\n\n"
            "כן — חיות מחמד יכולות להכניס הכנסה הביתה 😄\n"
            "אנשים מחפשים לא רק צילומים — הם רוצים רגש וזמן\n"
            "עם בעלי חיים שאין להם:\n\n"
            "🚶 <b>טיולים</b> — מי שחולם על כלב כמו שלכם\n"
            "אבל לא יכול לגדל אחד, ישמח לטייל איתו\n"
            "🤔 <b>«טסט-דרייב לגזע»</b> — מישהו מתלבט אם לקנות גור.\n"
            "הוא נפגש עם חיית המחמד שלכם — ומחליט בצורה מושכלת\n"
            "🐴 <b>רכיבה על סוסים</b> — רכיבה וצילומים עם סוסים\n"
            "📸 <b>אירועים</b> — צילומים, ימי הולדת לילדים,\n"
            "חתונות, פרסום\n\n"
            "את המחיר אתם קובעים — לשעה או לאירוע.\n\n"
            "איך מתחילים:\n"
            "1️⃣ ממלאים שאלון בבוט — 3 דקות\n"
            "2️⃣ אנחנו בודקים את הנתונים והמסמכים (חיסונים, פנקס וטרינרי)\n"
            "3️⃣ חיית המחמד מופיעה בקטלוג\n"
            "4️⃣ מקבלים בקשות ומרוויחים 💰\n\n"
            "אתם תמיד ליד חיית המחמד שלכם, הכל לפי הסכם,\n"
            "עמלת הפלטפורמה 20% רק על השכרות שהתקיימו.\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🐾 <b>רוצים לבלות זמן עם בעל חיים?</b>\n\n"
            "לא רק «לעניינים» — אפשר פשוט בשביל הנשמה:\n"
            "🔹 לטייל עם כלב שאתם חולמים עליו\n"
            "🔹 לרכוב על סוס\n"
            "🔹 «למדוד» גזע לפני קניית גור\n"
            "🔹 לארגן מסיבה, צילומים או הפתעה\n\n"
            "1️⃣ בוחרים בקטלוג או עם מסננים\n"
            "2️⃣ שולחים בקשה ישירות בבוט\n"
            "3️⃣ הבעלים מאשר תאריך ושעה\n"
            "4️⃣ נפגשים ונהנים 🐾\n\n"
            "📋 לכל בעלי החיים יש מסמכים וטרינריים.\n"
            "🛡 חיות גדולות ואקזוטיות — רק בליווי הבעלים.\n"
            "💳 למחיר ההשכרה מתווספת עמלת שירות של 10%."
        ),
    },

    # ---------- Каталог и карточки ----------
    "choose_category": {"ru": "Выберите категорию:", "en": "Choose a category:", "he": "בחרו קטגוריה:"},
    "catalog_empty": {
        "ru": "Каталог пока пуст, загляните позже 🐾",
        "en": "The catalog is empty for now, come back later 🐾",
        "he": "הקטלוג ריק כרגע, חזרו מאוחר יותר 🐾",
    },
    "category_empty": {
        "ru": "В этой категории пока нет животных 🐾",
        "en": "No animals in this category yet 🐾",
        "he": "אין עדיין בעלי חיים בקטגוריה הזו 🐾",
    },
    "card_age": {"ru": "возраст", "en": "age", "he": "גיל"},
    "card_hour": {"ru": "час", "en": "hour", "he": "שעה"},
    "card_event": {"ru": "мероприятие", "en": "event", "he": "אירוע"},
    "card_character": {"ru": "Характер", "en": "Character", "he": "אופי"},
    "card_skills": {"ru": "Умеет", "en": "Skills", "he": "כישורים"},
    "card_risk": {"ru": "Уровень риска", "en": "Risk level", "he": "רמת סיכון"},
    "card_kids": {"ru": "Можно детям", "en": "Kid-friendly", "he": "מתאים לילדים"},
    "card_accompany": {
        "ru": "👤 Только с сопровождением владельца",
        "en": "👤 Only with the owner present",
        "he": "👤 רק בליווי הבעלים",
    },
    "card_pos": {"ru": "Карточка {pos} из {total}", "en": "Card {pos} of {total}", "he": "כרטיס {pos} מתוך {total}"},

    # ---------- Фильтры ----------
    "flt_title": {"ru": "🔍 <b>Подбор по фильтрам</b>", "en": "🔍 <b>Search with filters</b>", "he": "🔍 <b>חיפוש לפי מסננים</b>"},
    "flt_city": {"ru": "📍 Город", "en": "📍 City", "he": "📍 עיר"},
    "flt_price": {"ru": "💰 Цена", "en": "💰 Price", "he": "💰 מחיר"},
    "flt_kids": {"ru": "👶 Можно детям", "en": "👶 Kid-friendly", "he": "👶 מתאים לילדים"},
    "flt_found": {"ru": "Найдено животных: <b>{count}</b>", "en": "Animals found: <b>{count}</b>", "he": "נמצאו בעלי חיים: <b>{count}</b>"},
    "btn_flt_city": {"ru": "📍 Выбрать город", "en": "📍 Choose city", "he": "📍 לבחור עיר"},
    "btn_flt_price": {"ru": "💰 Выбрать цену", "en": "💰 Choose price", "he": "💰 לבחור מחיר"},
    "btn_flt_kids": {"ru": "👶 Можно детям: да/не важно", "en": "👶 Kid-friendly: yes/any", "he": "👶 מתאים לילדים: כן/לא משנה"},
    "btn_flt_show": {"ru": "✅ Показать ({count})", "en": "✅ Show ({count})", "he": "✅ להציג ({count})"},
    "btn_flt_reset": {"ru": "♻️ Сбросить", "en": "♻️ Reset", "he": "♻️ לאפס"},
    "btn_flt_back": {"ru": "🔍 Фильтры", "en": "🔍 Filters", "he": "🔍 מסננים"},
    "any_city": {"ru": "любой", "en": "any", "he": "כל עיר"},
    "any_city_btn": {"ru": "Любой город", "en": "Any city", "he": "כל עיר"},
    "choose_city_txt": {"ru": "Выберите город:", "en": "Choose a city:", "he": "בחרו עיר:"},
    "choose_price_txt": {"ru": "Выберите диапазон цены:", "en": "Choose a price range:", "he": "בחרו טווח מחירים:"},
    "price_any": {"ru": "любая", "en": "any", "he": "כל מחיר"},
    "price_low": {"ru": "до 100₪/час", "en": "up to 100₪/hour", "he": "עד 100₪ לשעה"},
    "price_high": {"ru": "от 100₪/час", "en": "from 100₪/hour", "he": "מ-100₪ לשעה"},
    "kids_any": {"ru": "не важно", "en": "any", "he": "לא משנה"},
    "kids_only_yes": {"ru": "только да", "en": "yes only", "he": "רק כן"},
    "flt_none": {
        "ru": "По этим фильтрам ничего не нашлось 🐾",
        "en": "Nothing found with these filters 🐾",
        "he": "לא נמצא כלום עם המסננים האלה 🐾",
    },

    # ---------- Заявка на аренду ----------
    "req_unavailable": {
        "ru": "Это животное сейчас недоступно 🐾",
        "en": "This animal is not available right now 🐾",
        "he": "בעל החיים הזה לא זמין כרגע 🐾",
    },
    "req_intro": {
        "ru": (
            "📩 Заявка на «{name}»\n\n"
            "На какую дату и время хотите арендовать?\n"
            "Например: <i>12.07 в 16:00</i>\n\n"
            "Отменить заявку — /cancel"
        ),
        "en": (
            "📩 Request for “{name}”\n\n"
            "What date and time would you like?\n"
            "For example: <i>12.07 at 16:00</i>\n\n"
            "Cancel — /cancel"
        ),
        "he": (
            "📩 בקשה עבור «{name}»\n\n"
            "לאיזה תאריך ושעה תרצו?\n"
            "לדוגמה: <i>12.07 בשעה 16:00</i>\n\n"
            "לביטול — /cancel"
        ),
    },
    "req_ask_phone": {
        "ru": "Отлично! Теперь оставьте номер телефона для связи —\nнажмите кнопку ниже или напишите номер вручную:",
        "en": "Great! Now share your phone number —\ntap the button below or type it manually:",
        "he": "מעולה! עכשיו השאירו מספר טלפון —\nלחצו על הכפתור למטה או הקלידו ידנית:",
    },
    "btn_send_phone": {"ru": "📱 Отправить мой номер", "en": "📱 Share my number", "he": "📱 לשלוח את המספר שלי"},
    "req_summary": {
        "ru": (
            "Проверьте заявку:\n\n"
            "🐾 Животное: <b>{name}</b> ({breed})\n"
            "📅 Дата: {date}\n"
            "📱 Телефон: {phone}\n\n"
            "💰 Аренда: {price}₪\n"
            "➕ Сервисный сбор (10%): {fee}₪\n"
            "<b>Итого: {total}₪</b>\n\n"
            "Оплата — после подтверждения владельцем."
        ),
        "en": (
            "Please check your request:\n\n"
            "🐾 Animal: <b>{name}</b> ({breed})\n"
            "📅 Date: {date}\n"
            "📱 Phone: {phone}\n\n"
            "💰 Rental: {price}₪\n"
            "➕ Service fee (10%): {fee}₪\n"
            "<b>Total: {total}₪</b>\n\n"
            "Payment — after the owner confirms."
        ),
        "he": (
            "בדקו את הבקשה:\n\n"
            "🐾 בעל חיים: <b>{name}</b> ({breed})\n"
            "📅 תאריך: {date}\n"
            "📱 טלפון: {phone}\n\n"
            "💰 השכרה: {price}₪\n"
            "➕ עמלת שירות (10%): {fee}₪\n"
            "<b>סה\"כ: {total}₪</b>\n\n"
            "התשלום — לאחר אישור הבעלים."
        ),
    },
    "btn_req_send": {"ru": "✅ Отправить заявку", "en": "✅ Send request", "he": "✅ לשלוח בקשה"},
    "btn_req_cancel": {"ru": "❌ Отменить", "en": "❌ Cancel", "he": "❌ לבטל"},
    "req_cancelled": {
        "ru": "Заявка отменена. Возвращайтесь в каталог 🐾",
        "en": "Request cancelled. Come back to the catalog 🐾",
        "he": "הבקשה בוטלה. חזרו לקטלוג 🐾",
    },
    "req_sent": {
        "ru": "✅ Заявка <b>{id}</b> отправлена!\n\nМы свяжемся с вами для подтверждения даты.\nСпасибо, что выбрали PetShare Israel 🐾",
        "en": "✅ Request <b>{id}</b> sent!\n\nWe will contact you to confirm the date.\nThank you for choosing PetShare Israel 🐾",
        "he": "✅ הבקשה <b>{id}</b> נשלחה!\n\nניצור קשר לאישור התאריך.\nתודה שבחרתם ב-PetShare Israel 🐾",
    },

    # ---------- Решение по заявке (клиенту) ----------
    "cli_confirmed": {
        "ru": "🎉 Ваша заявка <b>{id}</b> подтверждена!\n\n🐾 {animal}\n📅 {date}\n\nСвяжитесь с владельцем, чтобы договориться о деталях:",
        "en": "🎉 Your request <b>{id}</b> is confirmed!\n\n🐾 {animal}\n📅 {date}\n\nContact the owner to arrange the details:",
        "he": "🎉 הבקשה שלכם <b>{id}</b> אושרה!\n\n🐾 {animal}\n📅 {date}\n\nצרו קשר עם הבעלים לתיאום הפרטים:",
    },
    "btn_wa_owner": {
        "ru": "💬 Написать владельцу в WhatsApp",
        "en": "💬 Message the owner on WhatsApp",
        "he": "💬 לכתוב לבעלים בוואטסאפ",
    },
    "cli_declined": {
        "ru": "😔 К сожалению, заявка <b>{id}</b> отклонена — выбранная дата недоступна.\n\nЗагляните в каталог: возможно, подойдёт другое животное 🐾",
        "en": "😔 Unfortunately, request <b>{id}</b> was declined — the chosen date is unavailable.\n\nCheck the catalog: maybe another animal will suit you 🐾",
        "he": "😔 לצערנו הבקשה <b>{id}</b> נדחתה — התאריך שנבחר אינו זמין.\n\nהציצו בקטלוג: אולי בעל חיים אחר יתאים 🐾",
    },

    # ---------- Анкета владельца ----------
    "own_intro": {
        "ru": (
            "💼 <b>Сдать питомца в аренду</b>\n\n"
            "Короткая анкета (2-3 минуты) — после неё администратор проверит "
            "данные и подключит вас к платформе.\n\n"
            "Как вас зовут?\n\nОтменить в любой момент — /cancel"
        ),
        "en": (
            "💼 <b>List your pet for rent</b>\n\n"
            "A short form (2-3 minutes) — then the administrator will verify "
            "the data and connect you to the platform.\n\n"
            "What is your name?\n\nCancel anytime — /cancel"
        ),
        "he": (
            "💼 <b>להשכיר את חיית המחמד</b>\n\n"
            "שאלון קצר (2-3 דקות) — לאחר מכן המנהל יבדוק את הנתונים "
            "ויחבר אתכם לפלטפורמה.\n\n"
            "איך קוראים לכם?\n\nלביטול בכל שלב — /cancel"
        ),
    },
    "own_ask_phone": {
        "ru": "Ваш номер телефона (можно тот же, что в WhatsApp)?",
        "en": "Your phone number (WhatsApp number works too)?",
        "he": "מספר הטלפון שלכם (אפשר גם מספר וואטסאפ)?",
    },
    "own_ask_city": {"ru": "В каком городе вы находитесь?", "en": "Which city are you in?", "he": "באיזו עיר אתם נמצאים?"},
    "own_ask_petname": {"ru": "Как зовут вашего питомца?", "en": "What is your pet's name?", "he": "איך קוראים לחיית המחמד שלכם?"},
    "own_choose_cat": {"ru": "Выберите категорию:", "en": "Choose a category:", "he": "בחרו קטגוריה:"},
    "own_other_cat": {"ru": "➕ Другая категория", "en": "➕ Other category", "he": "➕ קטגוריה אחרת"},
    "own_ask_cat_text": {"ru": "Напишите категорию текстом:", "en": "Type the category:", "he": "כתבו את הקטגוריה:"},
    "own_ask_breed": {
        "ru": "Вид и порода? Например: Собака, Корги",
        "en": "Species and breed? For example: Dog, Corgi",
        "he": "סוג וגזע? לדוגמה: כלב, קורגי",
    },
    "own_ask_age": {"ru": "Сколько лет питомцу?", "en": "How old is your pet?", "he": "בן כמה חיית המחמד?"},
    "own_ask_temper": {
        "ru": "Опишите характер (например: дружелюбный, спокойный)",
        "en": "Describe the character (e.g.: friendly, calm)",
        "he": "תארו את האופי (לדוגמה: ידידותי, רגוע)",
    },
    "own_ask_skills": {
        "ru": "Что умеет / для чего подходит? (например: фотосессии, детские праздники)",
        "en": "Skills / good for? (e.g.: photo shoots, kids' parties)",
        "he": "מה הוא יודע / למה מתאים? (לדוגמה: צילומים, ימי הולדת)",
    },
    "own_ask_kids": {
        "ru": "Можно ли доверить питомца детям?",
        "en": "Is your pet safe with children?",
        "he": "אפשר לסמוך על חיית המחמד עם ילדים?",
    },
    "btn_yes": {"ru": "Да", "en": "Yes", "he": "כן"},
    "btn_no": {"ru": "Нет", "en": "No", "he": "לא"},
    "own_ask_price_hour": {
        "ru": "Желаемая цена за час аренды, ₪? (только число)",
        "en": "Desired price per hour, ₪? (number only)",
        "he": "מחיר רצוי לשעה, ₪? (מספר בלבד)",
    },
    "own_ask_price_event": {
        "ru": "Желаемая цена за мероприятие (несколько часов), ₪?",
        "en": "Desired price per event (a few hours), ₪?",
        "he": "מחיר רצוי לאירוע (כמה שעות), ₪?",
    },
    "own_ask_photo": {
        "ru": "Пришлите фото питомца, или напишите «пропустить»:",
        "en": "Send a photo of your pet, or type “skip”:",
        "he": "שלחו תמונה של חיית המחמד, או כתבו «דלג»:",
    },
    "own_summary": {
        "ru": (
            "Проверьте анкету:\n\n"
            "👤 Владелец: {name}, {phone}, {city}\n\n"
            "🐾 {pet_name} — {species} ({breed}), {age}\n"
            "📂 Категория: {category}\n"
            "😊 Характер: {temperament}\n"
            "⭐ Умеет: {skills}\n"
            "👶 Можно детям: {kids}\n"
            "💰 {price_hour}₪/час, {price_event}₪/мероприятие\n\n"
            "Отправить на проверку администратору?"
        ),
        "en": (
            "Please check the form:\n\n"
            "👤 Owner: {name}, {phone}, {city}\n\n"
            "🐾 {pet_name} — {species} ({breed}), {age}\n"
            "📂 Category: {category}\n"
            "😊 Character: {temperament}\n"
            "⭐ Skills: {skills}\n"
            "👶 Kid-friendly: {kids}\n"
            "💰 {price_hour}₪/hour, {price_event}₪/event\n\n"
            "Send for review to the administrator?"
        ),
        "he": (
            "בדקו את השאלון:\n\n"
            "👤 בעלים: {name}, {phone}, {city}\n\n"
            "🐾 {pet_name} — {species} ({breed}), {age}\n"
            "📂 קטגוריה: {category}\n"
            "😊 אופי: {temperament}\n"
            "⭐ כישורים: {skills}\n"
            "👶 מתאים לילדים: {kids}\n"
            "💰 {price_hour}₪ לשעה, {price_event}₪ לאירוע\n\n"
            "לשלוח לבדיקת המנהל?"
        ),
    },
    "btn_own_send": {"ru": "✅ Отправить на проверку", "en": "✅ Send for review", "he": "✅ לשלוח לבדיקה"},
    "btn_own_cancel": {"ru": "❌ Отмена", "en": "❌ Cancel", "he": "❌ ביטול"},
    "own_sent": {
        "ru": "✅ Анкета отправлена на проверку! Мы свяжемся с вами после одобрения 🐾",
        "en": "✅ Form sent for review! We will contact you after approval 🐾",
        "he": "✅ השאלון נשלח לבדיקה! ניצור קשר לאחר האישור 🐾",
    },
    "own_cancelled": {"ru": "Анкета отменена.", "en": "Form cancelled.", "he": "השאלון בוטל."},
    "own_approved": {
        "ru": "🎉 Ваш питомец «{name}» одобрен и уже в каталоге PetShare Israel!",
        "en": "🎉 Your pet “{name}” is approved and already in the PetShare Israel catalog!",
        "he": "🎉 חיית המחמד שלכם «{name}» אושרה וכבר בקטלוג PetShare Israel!",
    },
    "own_declined": {
        "ru": "😔 Анкета на «{name}» отклонена. Свяжитесь с нами, чтобы уточнить детали.",
        "en": "😔 The form for “{name}” was declined. Contact us for details.",
        "he": "😔 השאלון עבור «{name}» נדחה. צרו איתנו קשר לפרטים.",
    },

    # ---------- Передержка ----------
    "btn_boarding": {"ru": "🏡 Передержка питомцев", "en": "🏡 Pet boarding", "he": "🏡 פנסיון לחיות מחמד"},
    "board_menu": {
        "ru": (
            "🏡 <b>Передержка питомцев</b>\n\n"
            "Улетаете в отпуск, а оставить любимца не с кем?\n"
            "Или наоборот — любите животных и готовы присмотреть\n"
            "за чужим питомцем за оплату?\n\n"
            "Выберите, что вам нужно:"
        ),
        "en": (
            "🏡 <b>Pet boarding</b>\n\n"
            "Going on vacation with no one to leave your pet with?\n"
            "Or the opposite — you love animals and are ready to look\n"
            "after someone's pet for pay?\n\n"
            "Choose what you need:"
        ),
        "he": (
            "🏡 <b>פנסיון לחיות מחמד</b>\n\n"
            "טסים לחופשה ואין עם מי להשאיר את חיית המחמד?\n"
            "או להפך — אוהבים בעלי חיים ומוכנים לשמור\n"
            "על חיית מחמד של מישהו אחר בתשלום?\n\n"
            "בחרו מה אתם צריכים:"
        ),
    },
    "btn_give_pet": {"ru": "🧳 Отдать питомца на время", "en": "🧳 Leave my pet for a while", "he": "🧳 למסור חיית מחמד לזמן מה"},
    "btn_be_sitter": {"ru": "🤝 Стать пет-ситтером", "en": "🤝 Become a pet sitter", "he": "🤝 להיות פט-סיטר"},
    "btn_sitters_list": {"ru": "👥 Посмотреть ситтеров", "en": "👥 Browse sitters", "he": "👥 לצפות בפט-סיטרים"},

    # Анкета ситтера
    "sit_intro": {
        "ru": (
            "🤝 <b>Стать пет-ситтером</b>\n\n"
            "Короткая анкета — после проверки вы появитесь в каталоге,\n"
            "и владельцы смогут оставлять вам питомцев за оплату.\n\n"
            "Как вас зовут?\n\nОтменить в любой момент — /cancel"
        ),
        "en": (
            "🤝 <b>Become a pet sitter</b>\n\n"
            "A short form — after verification you will appear in the catalog,\n"
            "and owners will be able to leave their pets with you for pay.\n\n"
            "What is your name?\n\nCancel anytime — /cancel"
        ),
        "he": (
            "🤝 <b>להיות פט-סיטר</b>\n\n"
            "שאלון קצר — לאחר האימות תופיעו בקטלוג,\n"
            "ובעלים יוכלו להשאיר אצלכם חיות מחמד בתשלום.\n\n"
            "איך קוראים לכם?\n\nלביטול בכל שלב — /cancel"
        ),
    },
    "sit_ask_animals": {
        "ru": "Каких животных готовы брать? (например: собаки мелкие, кошки, грызуны)",
        "en": "Which animals can you take? (e.g.: small dogs, cats, rodents)",
        "he": "אילו בעלי חיים תוכלו לקחת? (לדוגמה: כלבים קטנים, חתולים, מכרסמים)",
    },
    "sit_ask_exp": {
        "ru": "Ваш опыт с животными? (например: свой пёс 5 лет, работал(а) в приюте)",
        "en": "Your experience with animals? (e.g.: own dog for 5 years, shelter volunteer)",
        "he": "הניסיון שלכם עם בעלי חיים? (לדוגמה: כלב משלי 5 שנים, התנדבות במקלט)",
    },
    "sit_ask_cond": {
        "ru": "Условия у вас: квартира или дом? есть ли двор, другие животные, дети?",
        "en": "Your conditions: apartment or house? yard, other pets, kids?",
        "he": "התנאים אצלכם: דירה או בית? חצר, חיות אחרות, ילדים?",
    },
    "sit_ask_price": {
        "ru": "Цена за сутки передержки, ₪? (только число)",
        "en": "Price per day of boarding, ₪? (number only)",
        "he": "מחיר ליום פנסיון, ₪? (מספר בלבד)",
    },
    "sit_summary": {
        "ru": (
            "Проверьте анкету ситтера:\n\n"
            "👤 {name}, {phone}, {city}\n"
            "🐾 Берёт: {animals}\n"
            "⭐ Опыт: {exp}\n"
            "🏠 Условия: {cond}\n"
            "💰 {price}₪/сутки\n\n"
            "Отправить на проверку администратору?"
        ),
        "en": (
            "Please check the sitter form:\n\n"
            "👤 {name}, {phone}, {city}\n"
            "🐾 Takes: {animals}\n"
            "⭐ Experience: {exp}\n"
            "🏠 Conditions: {cond}\n"
            "💰 {price}₪/day\n\n"
            "Send for review to the administrator?"
        ),
        "he": (
            "בדקו את שאלון הפט-סיטר:\n\n"
            "👤 {name}, {phone}, {city}\n"
            "🐾 לוקח: {animals}\n"
            "⭐ ניסיון: {exp}\n"
            "🏠 תנאים: {cond}\n"
            "💰 {price}₪ ליום\n\n"
            "לשלוח לבדיקת המנהל?"
        ),
    },
    "sit_approved": {
        "ru": "🎉 Ваша анкета пет-ситтера одобрена! Вы в каталоге PetShare Israel.",
        "en": "🎉 Your pet sitter form is approved! You are in the PetShare Israel catalog.",
        "he": "🎉 שאלון הפט-סיטר שלכם אושר! אתם בקטלוג PetShare Israel.",
    },
    "sit_declined": {
        "ru": "😔 Анкета пет-ситтера отклонена. Свяжитесь с нами, чтобы уточнить детали.",
        "en": "😔 Your pet sitter form was declined. Contact us for details.",
        "he": "😔 שאלון הפט-סיטר נדחה. צרו איתנו קשר לפרטים.",
    },
    "sitters_empty": {
        "ru": "Проверенных ситтеров пока нет — загляните позже 🐾",
        "en": "No verified sitters yet — come back later 🐾",
        "he": "אין עדיין פט-סיטרים מאומתים — חזרו מאוחר יותר 🐾",
    },
    "sit_card_takes": {"ru": "Берёт", "en": "Takes", "he": "לוקח"},
    "sit_card_exp": {"ru": "Опыт", "en": "Experience", "he": "ניסיון"},
    "sit_card_cond": {"ru": "Условия", "en": "Conditions", "he": "תנאים"},
    "sit_card_day": {"ru": "сутки", "en": "day", "he": "יום"},
    "btn_request_sitter": {"ru": "📩 Оставить заявку", "en": "📩 Send a request", "he": "📩 לשלוח בקשה"},

    # Заявка на передержку
    "brd_intro": {
        "ru": (
            "🧳 <b>Заявка на передержку</b>\n\n"
            "Расскажите о питомце: вид, порода, кличка, возраст.\n"
            "Например: <i>собака, корги, Айза, 3 года</i>\n\n"
            "Отменить — /cancel"
        ),
        "en": (
            "🧳 <b>Boarding request</b>\n\n"
            "Tell us about your pet: species, breed, name, age.\n"
            "For example: <i>dog, corgi, Aiza, 3 years</i>\n\n"
            "Cancel — /cancel"
        ),
        "he": (
            "🧳 <b>בקשת פנסיון</b>\n\n"
            "ספרו על חיית המחמד: סוג, גזע, שם, גיל.\n"
            "לדוגמה: <i>כלב, קורגי, אייזה, 3 שנים</i>\n\n"
            "לביטול — /cancel"
        ),
    },
    "brd_intro_sitter": {
        "ru": (
            "🧳 <b>Заявка на передержку к ситтеру {name}</b>\n\n"
            "Расскажите о питомце: вид, порода, кличка, возраст.\n"
            "Например: <i>собака, корги, Айза, 3 года</i>\n\n"
            "Отменить — /cancel"
        ),
        "en": (
            "🧳 <b>Boarding request to sitter {name}</b>\n\n"
            "Tell us about your pet: species, breed, name, age.\n"
            "For example: <i>dog, corgi, Aiza, 3 years</i>\n\n"
            "Cancel — /cancel"
        ),
        "he": (
            "🧳 <b>בקשת פנסיון אצל {name}</b>\n\n"
            "ספרו על חיית המחמד: סוג, גזע, שם, גיל.\n"
            "לדוגמה: <i>כלב, קורגי, אייזה, 3 שנים</i>\n\n"
            "לביטול — /cancel"
        ),
    },
    "brd_ask_dates": {
        "ru": "На какие даты нужна передержка? Например: <i>с 15.07 по 25.07</i>",
        "en": "What dates do you need? For example: <i>from 15.07 to 25.07</i>",
        "he": "לאילו תאריכים צריך פנסיון? לדוגמה: <i>מ-15.07 עד 25.07</i>",
    },
    "brd_ask_city": {
        "ru": "В каком вы городе?",
        "en": "Which city are you in?",
        "he": "באיזו עיר אתם?",
    },
    "brd_ask_notes": {
        "ru": "Особенности ухода: корм, лекарства, привычки? Если нет — напишите «нет»",
        "en": "Care details: food, medication, habits? If none — type “no”",
        "he": "פרטי טיפול: אוכל, תרופות, הרגלים? אם אין — כתבו «אין»",
    },
    "brd_summary": {
        "ru": (
            "Проверьте заявку на передержку:\n\n"
            "🐾 Питомец: {pet}\n"
            "📅 Даты: {dates}\n"
            "📍 Город: {city}\n"
            "📝 Особенности: {notes}\n"
            "📱 Телефон: {phone}\n"
            "{sitter_line}\n"
            "Отправить заявку?"
        ),
        "en": (
            "Please check your boarding request:\n\n"
            "🐾 Pet: {pet}\n"
            "📅 Dates: {dates}\n"
            "📍 City: {city}\n"
            "📝 Care details: {notes}\n"
            "📱 Phone: {phone}\n"
            "{sitter_line}\n"
            "Send the request?"
        ),
        "he": (
            "בדקו את בקשת הפנסיון:\n\n"
            "🐾 חיית מחמד: {pet}\n"
            "📅 תאריכים: {dates}\n"
            "📍 עיר: {city}\n"
            "📝 פרטי טיפול: {notes}\n"
            "📱 טלפון: {phone}\n"
            "{sitter_line}\n"
            "לשלוח את הבקשה?"
        ),
    },
    "brd_sitter_line": {
        "ru": "🤝 Ситтер: {name}\n",
        "en": "🤝 Sitter: {name}\n",
        "he": "🤝 פט-סיטר: {name}\n",
    },
    "brd_sent": {
        "ru": "✅ Заявка <b>{id}</b> отправлена!\n\nМы подберём проверенного ситтера и свяжемся с вами 🐾",
        "en": "✅ Request <b>{id}</b> sent!\n\nWe will find a verified sitter and contact you 🐾",
        "he": "✅ הבקשה <b>{id}</b> נשלחה!\n\nנמצא פט-סיטר מאומת וניצור קשר 🐾",
    },
    "cli_brd_confirmed": {
        "ru": "🎉 Заявка на передержку <b>{id}</b> подтверждена!\n\nСвяжитесь с ситтером, чтобы договориться о деталях:",
        "en": "🎉 Boarding request <b>{id}</b> confirmed!\n\nContact the sitter to arrange the details:",
        "he": "🎉 בקשת הפנסיון <b>{id}</b> אושרה!\n\nצרו קשר עם הפט-סיטר לתיאום:",
    },
    "btn_wa_sitter": {
        "ru": "💬 Написать ситтеру в WhatsApp",
        "en": "💬 Message the sitter on WhatsApp",
        "he": "💬 לכתוב לפט-סיטר בוואטסאפ",
    },
    "cli_brd_declined": {
        "ru": "😔 К сожалению, заявка на передержку <b>{id}</b> отклонена — на эти даты нет свободных ситтеров.\n\nПопробуйте другие даты 🐾",
        "en": "😔 Unfortunately, boarding request <b>{id}</b> was declined — no sitters available for these dates.\n\nTry other dates 🐾",
        "he": "😔 לצערנו בקשת הפנסיון <b>{id}</b> נדחתה — אין פט-סיטרים פנויים בתאריכים אלה.\n\nנסו תאריכים אחרים 🐾",
    },
    "brd_ask_days": {
        "ru": "Сколько суток нужна передержка? (только число)",
        "en": "How many days of boarding do you need? (number only)",
        "he": "כמה ימי פנסיון צריך? (מספר בלבד)",
    },
    "brd_cost_block": {
        "ru": "💰 {days} сут. × {rate}₪ = {cost}₪\n➕ Сервисный сбор (10%): {fee}₪\n<b>Итого: {total}₪</b>",
        "en": "💰 {days} days × {rate}₪ = {cost}₪\n➕ Service fee (10%): {fee}₪\n<b>Total: {total}₪</b>",
        "he": "💰 {days} ימים × {rate}₪ = {cost}₪\n➕ עמלת שירות (10%): {fee}₪\n<b>סה\"כ: {total}₪</b>",
    },
    "brd_cost_later": {
        "ru": "💰 Стоимость рассчитаем после подбора ситтера (+10% сервисный сбор)",
        "en": "💰 The cost will be calculated after we match a sitter (+10% service fee)",
        "he": "💰 העלות תחושב לאחר התאמת פט-סיטר (+10% עמלת שירות)",
    },

    # ---------- Знакомства питомцев ----------
    "btn_friends": {"ru": "💞 Знакомства питомцев", "en": "💞 Pet matchmaking", "he": "💞 היכרויות לחיות מחמד"},
    "frd_menu": {
        "ru": (
            "💞 <b>Знакомства питомцев</b>\n\n"
            "🤝 Найдите питомцу друга для совместных прогулок\n"
            "💞 Или пару для вязки — с проверенными документами\n\n"
            "Правило простое: сначала создайте анкету своего питомца,\n"
            "после проверки вы сможете предлагать знакомства.\n\n"
            "💳 Организация вязки — сервисный сбор {mating_fee}₪.\n"
            "Дружеские знакомства — бесплатно!"
        ),
        "en": (
            "💞 <b>Pet matchmaking</b>\n\n"
            "🤝 Find your pet a friend for walks together\n"
            "💞 Or a mate for breeding — with verified documents\n\n"
            "Simple rule: first create your pet's profile,\n"
            "after verification you can propose meetings.\n\n"
            "💳 Breeding arrangement — {mating_fee}₪ service fee.\n"
            "Friendship meetings are free!"
        ),
        "he": (
            "💞 <b>היכרויות לחיות מחמד</b>\n\n"
            "🤝 מצאו לחיית המחמד חבר לטיולים משותפים\n"
            "💞 או בן/בת זוג להרבעה — עם מסמכים מאומתים\n\n"
            "הכלל פשוט: קודם צרו פרופיל לחיית המחמד שלכם,\n"
            "לאחר האימות תוכלו להציע היכרויות.\n\n"
            "💳 ארגון הרבעה — עמלת שירות {mating_fee}₪.\n"
            "היכרויות חברות — בחינם!"
        ),
    },
    "btn_create_profile": {"ru": "📝 Создать анкету питомца", "en": "📝 Create pet profile", "he": "📝 ליצור פרופיל לחיית המחמד"},
    "btn_browse_friends": {"ru": "🤝 Ищут друзей", "en": "🤝 Looking for friends", "he": "🤝 מחפשים חברים"},
    "btn_browse_mating": {"ru": "💞 Ищут пару (вязка)", "en": "💞 Looking for a mate", "he": "💞 מחפשים בני זוג"},
    "frd_intro": {
        "ru": (
            "📝 <b>Анкета питомца для знакомств</b>\n\n"
            "После проверки анкета попадёт в каталог, и вы сможете\n"
            "предлагать знакомства другим питомцам.\n\n"
            "Как вас зовут (владельца)?\n\nОтменить — /cancel"
        ),
        "en": (
            "📝 <b>Pet profile for matchmaking</b>\n\n"
            "After verification your profile will appear in the catalog,\n"
            "and you will be able to propose meetings.\n\n"
            "What is your (owner's) name?\n\nCancel — /cancel"
        ),
        "he": (
            "📝 <b>פרופיל חיית מחמד להיכרויות</b>\n\n"
            "לאחר האימות הפרופיל יופיע בקטלוג ותוכלו\n"
            "להציע היכרויות לחיות מחמד אחרות.\n\n"
            "איך קוראים לכם (הבעלים)?\n\nלביטול — /cancel"
        ),
    },
    "frd_ask_sex": {"ru": "Пол питомца?", "en": "Your pet's sex?", "he": "מין חיית המחמד?"},
    "btn_male": {"ru": "♂ Мальчик", "en": "♂ Male", "he": "♂ זכר"},
    "btn_female": {"ru": "♀ Девочка", "en": "♀ Female", "he": "♀ נקבה"},
    "frd_ask_goal": {"ru": "Что ищете?", "en": "What are you looking for?", "he": "מה אתם מחפשים?"},
    "btn_goal_friend": {"ru": "🤝 Друга для прогулок", "en": "🤝 A friend for walks", "he": "🤝 חבר לטיולים"},
    "btn_goal_mate": {"ru": "💞 Пару для вязки", "en": "💞 A mate for breeding", "he": "💞 בן/בת זוג להרבעה"},
    "btn_goal_both": {"ru": "✨ И то, и другое", "en": "✨ Both", "he": "✨ גם וגם"},
    "frd_ask_docs": {
        "ru": "Документы питомца: прививки, ветпаспорт, родословная?\nНапример: <i>прививки есть, родословная есть</i>",
        "en": "Your pet's documents: vaccinations, vet passport, pedigree?\nFor example: <i>vaccinated, has pedigree</i>",
        "he": "מסמכי חיית המחמד: חיסונים, פנקס וטרינרי, ייחוס?\nלדוגמה: <i>מחוסן, יש ייחוס</i>",
    },
    "frd_ask_desc": {
        "ru": "Пара слов о питомце: характер, привычки, что любит?",
        "en": "A few words about your pet: character, habits, likes?",
        "he": "כמה מילים על חיית המחמד: אופי, הרגלים, מה אוהב?",
    },
    "frd_summary": {
        "ru": (
            "Проверьте анкету:\n\n"
            "👤 Владелец: {name}, {phone}, {city}\n\n"
            "🐾 {pet_name} — {breed}\n"
            "{sex_icon} Пол: {sex}   |   Возраст: {age}\n"
            "🎯 Цель: {goal}\n"
            "📋 Документы: {docs}\n"
            "📝 {desc}\n\n"
            "Отправить на проверку?"
        ),
        "en": (
            "Please check the profile:\n\n"
            "👤 Owner: {name}, {phone}, {city}\n\n"
            "🐾 {pet_name} — {breed}\n"
            "{sex_icon} Sex: {sex}   |   Age: {age}\n"
            "🎯 Goal: {goal}\n"
            "📋 Documents: {docs}\n"
            "📝 {desc}\n\n"
            "Send for review?"
        ),
        "he": (
            "בדקו את הפרופיל:\n\n"
            "👤 בעלים: {name}, {phone}, {city}\n\n"
            "🐾 {pet_name} — {breed}\n"
            "{sex_icon} מין: {sex}   |   גיל: {age}\n"
            "🎯 מטרה: {goal}\n"
            "📋 מסמכים: {docs}\n"
            "📝 {desc}\n\n"
            "לשלוח לבדיקה?"
        ),
    },
    "frd_approved": {
        "ru": "🎉 Анкета «{name}» одобрена! Теперь вы можете предлагать знакомства 💞",
        "en": "🎉 Profile “{name}” approved! Now you can propose meetings 💞",
        "he": "🎉 הפרופיל «{name}» אושר! עכשיו אפשר להציע היכרויות 💞",
    },
    "frd_declined": {
        "ru": "😔 Анкета «{name}» отклонена. Свяжитесь с нами, чтобы уточнить детали.",
        "en": "😔 Profile “{name}” was declined. Contact us for details.",
        "he": "😔 הפרופיל «{name}» נדחה. צרו איתנו קשר לפרטים.",
    },
    "frd_empty": {
        "ru": "Пока нет анкет в этом разделе — создайте первую! 🐾",
        "en": "No profiles in this section yet — create the first one! 🐾",
        "he": "אין עדיין פרופילים בקטגוריה — צרו את הראשון! 🐾",
    },
    "frd_card_sex": {"ru": "Пол", "en": "Sex", "he": "מין"},
    "frd_card_age": {"ru": "возраст", "en": "age", "he": "גיל"},
    "frd_card_goal": {"ru": "Ищет", "en": "Looking for", "he": "מחפש"},
    "frd_card_docs": {"ru": "Документы", "en": "Documents", "he": "מסמכים"},
    "goal_friend": {"ru": "друга для прогулок", "en": "a friend for walks", "he": "חבר לטיולים"},
    "goal_mate": {"ru": "пару для вязки", "en": "a mate for breeding", "he": "בן/בת זוג להרבעה"},
    "goal_both": {"ru": "друга и пару", "en": "a friend and a mate", "he": "חבר ובן/בת זוג"},
    "sex_male": {"ru": "мальчик", "en": "male", "he": "זכר"},
    "sex_female": {"ru": "девочка", "en": "female", "he": "נקבה"},
    "btn_propose": {"ru": "💌 Предложить знакомство", "en": "💌 Propose a meeting", "he": "💌 להציע היכרות"},
    "frd_need_profile": {
        "ru": "Чтобы предлагать знакомства, сначала создайте анкету своего питомца и дождитесь её проверки 📝",
        "en": "To propose meetings, first create your pet's profile and wait for verification 📝",
        "he": "כדי להציע היכרויות, קודם צרו פרופיל לחיית המחמד שלכם והמתינו לאימות 📝",
    },
    "propose_sent": {
        "ru": "💌 Предложение <b>{id}</b> отправлено!\n\nМы проверим совместимость и свяжем вас с владельцем 🐾",
        "en": "💌 Proposal <b>{id}</b> sent!\n\nWe will check compatibility and connect you with the owner 🐾",
        "he": "💌 ההצעה <b>{id}</b> נשלחה!\n\nנבדוק התאמה ונחבר אתכם עם הבעלים 🐾",
    },
    "mating_fee_note": {
        "ru": "💳 За организацию вязки — сервисный сбор {fee}₪ (оплата после подтверждения).",
        "en": "💳 Breeding arrangement service fee — {fee}₪ (paid after confirmation).",
        "he": "💳 עמלת שירות לארגון הרבעה — {fee}₪ (תשלום לאחר האישור).",
    },
    "mtc_confirmed": {
        "ru": (
            "🎉 Знакомство <b>{id}</b> одобрено!\n\n"
            "🐾 {pet1} и {pet2} — отличная пара!\n"
            "Свяжитесь с владельцем и договоритесь о встрече:"
        ),
        "en": (
            "🎉 Meeting <b>{id}</b> approved!\n\n"
            "🐾 {pet1} and {pet2} — a great match!\n"
            "Contact the owner and arrange the meeting:"
        ),
        "he": (
            "🎉 ההיכרות <b>{id}</b> אושרה!\n\n"
            "🐾 {pet1} ו-{pet2} — התאמה מצוינת!\n"
            "צרו קשר עם הבעלים ותאמו פגישה:"
        ),
    },
    "mtc_declined": {
        "ru": "😔 Знакомство <b>{id}</b> не согласовано. Посмотрите другие анкеты в каталоге 🐾",
        "en": "😔 Meeting <b>{id}</b> was not approved. Check other profiles in the catalog 🐾",
        "he": "😔 ההיכרות <b>{id}</b> לא אושרה. בדקו פרופילים אחרים בקטלוג 🐾",
    },
}


def t(key, lang, **kwargs):
    """Перевод по ключу; при отсутствии — русский вариант."""
    entry = T[key]
    text = entry.get(lang) or entry[DEFAULT_LANG]
    return text.format(**kwargs) if kwargs else text


# Перевод значений из таблицы (города, категории, да/нет, риск).
# Ключ — как записано в таблице по-русски.
VALUES = {
    # города и районы
    "Тель-Авив": {"en": "Tel Aviv", "he": "תל אביב"},
    "Иерусалим": {"en": "Jerusalem", "he": "ירושלים"},
    "Хайфа": {"en": "Haifa", "he": "חיפה"},
    "Ришон-ле-Цион": {"en": "Rishon LeZion", "he": "ראשון לציון"},
    "Беэр-Шева": {"en": "Be'er Sheva", "he": "באר שבע"},
    "Нетания": {"en": "Netanya", "he": "נתניה"},
    "Ашдод": {"en": "Ashdod", "he": "אשדוד"},
    "Центральный округ": {"en": "Central District", "he": "מחוז המרכז"},
    "Северный округ": {"en": "Northern District", "he": "מחוז הצפון"},
    "Южный округ": {"en": "Southern District", "he": "מחוז הדרום"},
    "Центр": {"en": "Center", "he": "מרכז"},
    "Север": {"en": "North", "he": "צפון"},
    "Юг": {"en": "South", "he": "דרום"},
    # категории каталога
    "Собаки": {"en": "Dogs", "he": "כלבים"},
    "Кошки": {"en": "Cats", "he": "חתולים"},
    "Птицы": {"en": "Birds", "he": "ציפורים"},
    "Грызуны и кролики": {"en": "Rodents & rabbits", "he": "מכרסמים וארנבים"},
    "Экзотика и ферма": {"en": "Exotic & farm", "he": "אקזוטי וחווה"},
    # значения полей
    "да": {"en": "yes", "he": "כן"},
    "нет": {"en": "no", "he": "לא"},
    "не указан": {"en": "not specified", "he": "לא צוין"},
    "низкий": {"en": "low", "he": "נמוכה"},
    "средний": {"en": "medium", "he": "בינונית"},
    "высокий": {"en": "high", "he": "גבוהה"},
    # статусы заявок и анкет
    "новая": {"en": "new", "he": "חדשה"},
    "подтверждена": {"en": "confirmed", "he": "אושרה"},
    "отклонена": {"en": "declined", "he": "נדחתה"},
    "одобрена": {"en": "approved", "he": "אושרה"},
    "на проверке": {"en": "under review", "he": "בבדיקה"},
    "проверен": {"en": "verified", "he": "מאומת"},
    "проверено": {"en": "verified", "he": "מאומת"},
    "отклонено": {"en": "declined", "he": "נדחה"},
    "отклонён": {"en": "declined", "he": "נדחה"},
}


def tr_value(value, lang):
    """Переводит значение из таблицы по словарю; неизвестное — как есть."""
    value = str(value).strip()
    if lang == DEFAULT_LANG:
        return value
    entry = VALUES.get(value)
    if entry:
        return entry.get(lang, value)
    return value
