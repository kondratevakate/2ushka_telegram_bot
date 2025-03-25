import os
import csv
import logging
import nest_asyncio
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
    CallbackQueryHandler,
)

# Import FAQ content from separate file
from faq_content import FAQ_TEXT

nest_asyncio.apply()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/home/ubuntu/bot_errors.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7809849560:AAHPQF54KnIzWMvj09KBJ9tTCkBjWuUktyA"
ADMIN_CHAT_ID = -1002453479330  # ID админ-чата
FOLDER_PATH = "/home/ubuntu"
LOG_FILE = f"{FOLDER_PATH}/client_interactions.csv"
GUIDE_PAYMENT_LINK = "https://web.tribute.tg/p/9yV"
GUIDE_STARS_LINK = "https://t.me/tribute/app?startapp=p9yV"

CONCIERGE_PAYMENT_LINK = "https://web.tribute.tg/p/9yZ"
CONCIERGE_STARS_LINK = "https://t.me/tribute/app?startapp=p9yZ"

os.makedirs(FOLDER_PATH, exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Timestamp", "User", "UserID", "Action"])
        writer.writeheader()

# Main menu with buttons
MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["🧭 Получить бесплатную подборку", "🛒 Купить гайд"],
        ["📖 О тарифах", "💼 Оплата тревел-консьерж"],
        ["ℹ️ Частые Вопросики", "❓ Задать вопрос"]
    ],
    resize_keyboard=True,
)

def log_action(user: str, user_id: int, action: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Timestamp", "User", "UserID", "Action"])
        writer.writerow({"Timestamp": timestamp, "User": user, "UserID": user_id, "Action": action})

async def notify_admin(context: CallbackContext, message: str):
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.username or "Не указано"
    user_id = update.effective_user.id
    log_action(user, user_id, "Started bot")
    await notify_admin(context, f"Пользователь @{user} (ID: {user_id}) запустил бота.")
    await update.message.reply_text("Что будем делать?", reply_markup=MAIN_MENU)

async def about_tariffs(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.username or "Не указано"
    user_id = update.effective_user.id
    log_action(user, user_id, "Viewed tariffs")
    await notify_admin(context, f"Пользователь @{user} (ID: {user_id}) посмотрел тарифы.")
    # Added "Назад в меню" button for navigation
    keyboard = [
        [InlineKeyboardButton("Гайд", callback_data="tariff_guide")],
        [InlineKeyboardButton("Тревел-консьерж", callback_data="tariff_concierge")],
        [InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Доступные тарифы:", reply_markup=reply_markup)

async def tariff_details(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    tariff_key = query.data.split("_")[1]
    tariffs = {
        "guide": (
            "📖 *Что особенного в гайде?*\n\n"
            "👀 *Отзыв про гайд:* Комплексно, без воды, с анализом вероятностей китов/сияния, при этом реально полезная информация, не компиляция инфы из интернета.\n"
            "✅ *Выбор лучших дат*: точные данные наблюдений за китами и сиянием за последние годы.\n"
            "💡 *Что внутри:*\n"
            "— Даты и места с максимальными шансами увидеть китов и сияние.\n"
            "— Рекомендации по кафе и активностям, и ни одной рекламы.\n\n"
            "💰 Цена: 1500 рублей.\n\n"
            "🛒 *Как купить гайд?*\n"
            "— Оплата в рублях с карты или Telegram звездами\n"
            f"— Ссылка на покупку за Телеграмм звезды [здесь]({GUIDE_STARS_LINK}) или по карте через главное меню 🛒 \"Купить Гайд\"\n\n"
        ),
        "concierge": (
            "💼 *Что даёт тревел-консьерж:*\n\n"
            "✅ *Персональный подход*: мы составим маршруты и расписания по вашим датам на настрою.\n"
            "✅ *Боремся с прокрастинацией*: напоминаем про покупку билетов, бронирование и страховку.\n"
            "💡 *Что включено:*\n"
            "— Индивидуальные маршруты под ваши даты.\n"
            "— Рекомендации по готовым турам и местам.\n"
            "— Полное расписание вашего путешествия.\n"
            "💰 *Цена:*\n"
            "— Полный пакет: 5000 рублей.\n"
            "— Если вы уже купили гайд, доплата за консультацию меньше.\n\n"
            "👀 *Почему это круто*: за стоимость сеанса психотерапии вы снимаете с себя головную боль на несколько недель вперед.\n\n"
            "🛒 *Как получить услугу \"Тревел-консьерж\":*\n"
            f"— Внесите предоплату в размере 1000 рублей по [ссылке]({CONCIERGE_STARS_LINK}) на оплату Телеграм звездами или по карте в главном меню 💼 \"Тревел Консьерж\".\n"
            "— После получения предоплаты мы создаем отдельный чат и начинаем работу.\n"
            "— Остальную часть суммы вы переводите, когда мы согласуем маршрут."
        )
    }
    if tariff_key in tariffs:
        await query.answer()
        await update.effective_message.reply_photo(
            photo=open(os.path.join(os.getcwd(), f"2ushka_telegram_bot/viz/{tariff_key}.jpg"), "rb"),
            caption=tariffs[tariff_key],
            parse_mode="Markdown"
        )

async def faq(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(FAQ_TEXT, parse_mode="Markdown")

# --- Helper function to request an email with "Назад в меню" option ---
async def request_email(update: Update, context: CallbackContext, request_type: str) -> None:
    context.user_data["awaiting_email"] = request_type
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")]])
    # For purchase update, use the new custom text.
    if request_type == "purchase_update":
        text = ("Оставьте ваш email, мы обновляем маршруты раз в полгода и оповестим вас, "
                "если откроются новые места или закроются другие.")
    else:
        text = ("Чтобы получить доступ к подборке навсегда, введите ваш адрес электронной почты.\n"
                "Мы не будем спамить, у нас пока нечем 🥲\n\nВведи свою почту здесь текстом:")
    await update.effective_message.reply_text(text, reply_markup=keyboard)

# --- Function to send free selection content with three inline buttons ---
async def free_selection_send(update: Update, context: CallbackContext) -> None:
    free_text = "Забирай бесплатные подборки:"
    keyboard = [
        [InlineKeyboardButton("📍 40+ мест на Кольском", callback_data="free_link_yandex")],
        [InlineKeyboardButton("🚗 Гайд по Териберке", callback_data="free_link_teriberka")],
        [InlineKeyboardButton("📋 Топ 20 туров мечты по России", callback_data="free_link_notion")],
        [InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(free_text, reply_markup=reply_markup)

# --- Callback handler for free link buttons ---
async def free_link_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    callback_data = query.data
    user = update.effective_user.username or "Не указано"
    user_id = update.effective_user.id
    if callback_data == "free_link_yandex":
        url = "https://yandex.com/maps/?bookmarks%5BpublicId%5D=mSuY2SbK"
        log_action(user, user_id, "Requested free link: 40+ мест на Кольском")
    elif callback_data == "free_link_teriberka":
        url = "https://www.aviasales.ru/psgr/article/teriberka"
        log_action(user, user_id, "Requested free link: Гайд по Териберке")
    elif callback_data == "free_link_notion":
        url = "https://fantastic-makemake-bce.notion.site/2025-19aeb694471180779cddcc1aeb88a3fe?pvs=4"
        log_action(user, user_id, "Requested free link: Топ 20 туров мечты по России")
    else:
        return
    # Send the link as a message with the main menu for navigation
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Вот ссылка: {url}",
        reply_markup=MAIN_MENU
    )

# --- Handler for free selection requests ---
async def handle_free_selection(update: Update, context: CallbackContext) -> None:
    await free_selection_send(update, context)

# --- Handler for purchase requests ---
# The purchase link is sent immediately, then the bot asks for an email for updates.
async def handle_purchase(update: Update, context: CallbackContext) -> None:
    purchase_type = update.message.text.strip()
    if "гайд" in purchase_type.lower():
        link = GUIDE_PAYMENT_LINK
        message_text = (
            f"Держи ссылку на оплату: [оплатить картой]({link}) или [телеграм звездами]({GUIDE_STARS_LINK})\n"
            "*❗Важно❗*: гайд приходит ссылкой сразу же в чате Tribute в телеграмме.\n\n"
            "Мы спросим email, чтобы гайд до тебя точно дошёл.\n\n"
        )
    elif "тревел-консьерж" in purchase_type.lower():
        link = CONCIERGE_PAYMENT_LINK
        message_text = (
            f"Держи ссылку на оплату: [оплатить картой]({link}) или [телеграм звездами]({CONCIERGE_STARS_LINK})\n"
            "Мы скинем ссылку на чат, втч пары часов, как получим предоплату.\n\n"
        )
    else:
        await update.message.reply_text("Неизвестный тип покупки. Попробуйте снова.", reply_markup=MAIN_MENU)
        return
    await update.message.reply_text(
        message_text,
        parse_mode="Markdown",
        reply_markup=MAIN_MENU,
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Оставить email", callback_data="purchase_email")],
        [InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")]
    ])
    await update.message.reply_text("На всякий случай, чтобы вас точно найти, введите ваш email:", reply_markup=keyboard)
    context.user_data["awaiting_email"] = "purchase_update"

async def ask_question(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.username or "Не указано"
    user_id = update.effective_user.id
    log_action(user, user_id, "Asked a question")
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")]])
    await update.message.reply_text("Напишите ваш вопрос, и мы отправим его администратору.", reply_markup=keyboard)
    context.user_data["waiting_for_question"] = True

async def receive_text(update: Update, context: CallbackContext) -> None:
    if context.user_data.get("awaiting_email"):
        email = update.message.text.strip()
        request_type = context.user_data.pop("awaiting_email")
        user = update.effective_user.username or "Не указано"
        user_id = update.effective_user.id
        log_action(user, user_id, f"Provided email for request ({request_type}): {email}")
        if request_type == "purchase_update":
            await update.message.reply_text("Спасибо, ваш email записан.", reply_markup=MAIN_MENU)
        else:
            await update.message.reply_text("Неизвестный тип запроса. Попробуйте снова.", reply_markup=MAIN_MENU)
        return

    if context.user_data.get("waiting_for_question"):
        user = update.effective_user.username or "Не указано"
        user_id = update.effective_user.id
        question = update.message.text
        log_action(user, user_id, f"Sent a question: {question}")
        await notify_admin(context, f"Пользователь @{user} (ID: {user_id}) задал вопрос:\n\n{question}")
        await update.message.reply_text("Ваш вопрос отправлен администратору. Мы свяжемся с вами в течение рабочего дня.", reply_markup=MAIN_MENU)
        context.user_data["waiting_for_question"] = False

# --- Callback handler for inline buttons: Back to menu ---
async def back_to_menu_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Возвращаемся в главное меню...")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Главное меню", reply_markup=MAIN_MENU)

# --- Callback handler for "Оставить email" button in purchase flow ---
async def purchase_email_callback(update: Update, context: CallbackContext) -> None:
    await request_email(update, context, "purchase_update")

async def error_handler(update: object, context: CallbackContext) -> None:
    logger.error("Ошибка при обработке обновления:", exc_info=context.error)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("📖 О тарифах"), about_tariffs))
    app.add_handler(MessageHandler(filters.Regex("🛒 Купить гайд"), handle_purchase))
    app.add_handler(MessageHandler(filters.Regex("💼 Оплата тревел-консьерж"), handle_purchase))
    app.add_handler(MessageHandler(filters.Regex("❓ Задать вопрос"), ask_question))
    app.add_handler(MessageHandler(filters.Regex("ℹ️ Частые Вопросики"), faq))
    app.add_handler(MessageHandler(filters.Regex("🧭 Получить бесплатную подборку"), handle_free_selection))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text))
    app.add_handler(CallbackQueryHandler(tariff_details, pattern="^tariff_"))
    app.add_handler(CallbackQueryHandler(free_link_callback, pattern="^free_link_"))
    app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
    app.add_handler(CallbackQueryHandler(purchase_email_callback, pattern="^purchase_email$"))
    app.add_error_handler(error_handler)
    print("Бот запущен, ожидаю события...")
    await app.run_polling()
    print("Polling завершен.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
#nohup python /home/ubuntu/2ushka_telegram_bot/bot.py > bot.log 2>&1 &
