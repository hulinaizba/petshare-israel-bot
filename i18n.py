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
}


def t(key, lang, **kwargs):
    """Перевод по ключу; при отсутствии — русский вариант."""
    entry = T[key]
    text = entry.get(lang) or entry[DEFAULT_LANG]
    return text.format(**kwargs) if kwargs else text
