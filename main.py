import os
import csv
import logging
import pandas as pd
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

# Разрешаем повторное использование event loop
nest_asyncio.apply()

# Настройка логирования (вывод в консоль и в файл bot_errors.log)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot_errors.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "7809849560:AAHPQF54KnIzWMvj09KBJ9tTCkBjWuUktyA"
ADMIN_CHAT_ID = -1002453479330  # ID админ-чата
FOLDER_PATH = "."
LOG_FILE = f"{FOLDER_PATH}/client_interactions.csv"
GUIDE_PAYMENT_LINK = "https://web.tribute.tg/p/9yV"
CONCIERGE_PAYMENT_LINK = "https://web.tribute.tg/p/9yZ"

# Убедимся, что папка для логов существует
os.makedirs(FOLDER_PATH, exist_ok=True)

# Создаем файл лога, если он не существует (с колонками: Timestamp, User, UserID, Action)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Timestamp", "User", "UserID", "Action"])
        writer.writeheader()

MAIN_MENU = ReplyKeyboardMarkup(
    [["📖 О тарифах", "❓ Задать вопрос"], ["🛒 Купить гайд", "💼 Тревел-консьерж"], ["ℹ️ Частые Вопросики"]],
    resize_keyboard=True,
)

def log_action(user: str, user_id: int, action: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode="a", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Timestamp", "User", "UserID", "Action"])
        writer.writerow({"Timestamp": timestamp, "User": user, "UserID": user_id, "Action": action})

async def notify_admin(context: CallbackContext, message: str):
    # Если не нужно отправлять сообщения об ошибках в чат, просто оставляем уведомления для других случаев
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.username or "Не указано"
    user_id = update.effective_user.id
    log_action(user, user_id, "Started bot")
    await notify_admin(context, f"Пользователь @{user} (ID: {user_id}) запустил бота.")
    await update.message.reply_text(
        "Добро пожаловать! Выберите, чем я могу помочь:",
        reply_markup=MAIN_MENU,
    )

async def about_tariffs(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.username or "Не указано"
    user_id = update.effective_user.id
    log_action(user, user_id, "Viewed tariffs")
    await notify_admin(context, f"Пользователь @{user} (ID: {user_id}) посмотрел тарифы.")
    keyboard = [
        [InlineKeyboardButton("Гайд", callback_data="tariff_guide")],
        [InlineKeyboardButton("Тревел-консьерж", callback_data="tariff_concierge")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Доступные тарифы:", reply_markup=reply_markup)

async def tariff_details(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    tariff_key = query.data.split("_")[1]  # Получаем ключ тарифа

    tariffs = {
        "guide": (
            "📖 *Какую пользу вы получите от гайда:*\n\n"
            "✅ *Подготовка за вечер*: вместо недельного поиска по отзывам на картах.\n"
            "✅ *Выбор лучших дат*: точные данные наблюдений за китами и сиянием за последние годы помогут вам избежать промахов.\n"
            "✅ *Экономия до 30%*: наши советы по бронированию трансфера, транспорту и выбору ресторанов помогут снизить расходы.\n\n"
            "💡 *Что внутри:*\n"
            "— Даты и места с максимальными шансами увидеть китов и сияние.\n"
            "— Рекомендации по кафе и активностям, которых нет в стандартных путеводителях.\n\n"
            "💰 Цена: 800 рублей.\n\n"
            "👀 *Почему это круто*: вы получите доступ к реальным данным, посмотрите на фото локаций в разные сезоны и узнаете историю региона."
        ),
        "concierge": (
            "💼 *Что даёт тревел-консьерж:*\n\n"
            "✅ *Персональный подход*: мы составим маршруты и расписания по вашим датам на настрою.\n"
            "✅ *Готовые решения*: вам не нужно искать билеты, бронировать рестораны или думать о страховках — мы всё сделаем за вас.\n"
            "✅ *Оптимизация маршрута*: наши рекомендации сэкономят до 2 дней времени в путешествии, оставив место для отдыха.\n\n"
            "💡 *Что включено:*\n"
            "— Индивидуальные маршруты под ваши даты.\n"
            "— Рекомендации по готовым турам и местам.\n"
            "— Полное расписание вашего путешествия.\n"
            "💰 *Цена:*\n"
            "— Полный пакет: 4000 рублей.\n"
            "— Если вы уже купили гайд, доплата за консультацию: 3500 рублей.\n\n"
            "👀 *Почему это круто*: за стоимость сеанса психотерапии вы снимаете с себя головную боль на несколько недель вперед."
        ),
    }

    if tariff_key in tariffs:
        await query.answer()
        await update.effective_message.reply_photo(
            photo=open(os.path.join(os.getcwd(), f"viz/{tariff_key}.jpg"), "rb"),
            caption=tariffs[tariff_key],
            parse_mode="Markdown",
        )

async def faq(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "💡 *Вопросики:*\n\n"
        "1️⃣ *Для кого этот гайд?*\n"
        "— Для соло-путешественников, которым нужен быстрый и практичный план действий.\n\n"
        "2️⃣ *Почему именно этот гайд?*\n"
        "— Опыт и проверенные данные помогут избежать типичных проблем в пути.\n\n"
        "3️⃣ *Почему такая цена?*\n"
        "— Мы предлагаем оптимальное соотношение цены и качества, чтобы сделать путешествие доступнее.\n\n"
        "4️⃣ *Почему консьерж-сервис?*\n"
        "— Потому что иногда хочется простого человеческого подхода и готовых решений.\n\n"
        "5️⃣ *Что делает гайд уникальным?*\n"
        "— Вы получаете проверенные маршруты и советы, которых нет в открытом доступе.\n\n"
        "6️⃣ *Как быстро я получу гайд?*\n"
        "— Сразу после оплаты вы получите ссылку для скачивания.\n\n"
        "Если остались вопросы, задайте их через '❓ Задать вопрос'.",
        parse_mode="Markdown",
    )

async def handle_purchase(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.username or "Не указано"
    user_id = update.effective_user.id
    purchase_type = update.message.text.strip()

    if "гайд" in purchase_type.lower():
        link = GUIDE_PAYMENT_LINK
    elif "тревел-консьерж" in purchase_type.lower():
        link = CONCIERGE_PAYMENT_LINK
    else:
        await update.message.reply_text("Неизвестный тип покупки. Попробуйте снова.")
        return

    try:
        await update.message.reply_text(
            f"Оплатите по ссылке: [Оплатить]({link})",
            parse_mode="Markdown",
            reply_markup=MAIN_MENU,
        )
        log_action(user, user_id, f"Initiated purchase: {purchase_type}")
        await notify_admin(context, f"Пользователь @{user} (ID: {user_id}) запросил ссылку на покупку: {purchase_type}")
    except Exception as e:
        logger.error("Ошибка при обработке покупки: %s", e)
        await update.message.reply_text(
            "Произошла ошибка при отправке ссылки. Пожалуйста, попробуйте снова.",
            reply_markup=MAIN_MENU,
        )

async def ask_question(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.username or "Не указано"
    user_id = update.effective_user.id
    log_action(user, user_id, "Asked a question")
    await update.message.reply_text(
        "Напишите ваш вопрос, и мы отправим его администратору.",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data["waiting_for_question"] = True

async def receive_question(update: Update, context: CallbackContext) -> None:
    if context.user_data.get("waiting_for_question"):
        user = update.effective_user.username or "Не указано"
        user_id = update.effective_user.id
        question = update.message.text
        log_action(user, user_id, f"Sent a question: {question}")
        await notify_admin(context, f"Пользователь @{user} (ID: {user_id}) задал вопрос:\n\n{question}")
        await update.message.reply_text(
            "Ваш вопрос отправлен администратору. Мы свяжемся с вами в течение рабочего дня.",
            reply_markup=MAIN_MENU,
        )
        context.user_data["waiting_for_question"] = False

# Глобальный обработчик ошибок, который логирует ошибки, не отправляя уведомлений в чат
async def error_handler(update: object, context: CallbackContext) -> None:
    logger.error("Ошибка при обработке обновления:", exc_info=context.error)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("📖 О тарифах"), about_tariffs))
    app.add_handler(MessageHandler(filters.Regex("🛒 Купить гайд"), handle_purchase))
    app.add_handler(MessageHandler(filters.Regex("💼 Тревел-консьерж"), handle_purchase))
    app.add_handler(MessageHandler(filters.Regex("❓ Задать вопрос"), ask_question))
    app.add_handler(MessageHandler(filters.Regex("ℹ️ Частые Вопросики"), faq))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question))
    app.add_handler(CallbackQueryHandler(tariff_details))
    
    # Регистрируем глобальный обработчик ошибок
    app.add_error_handler(error_handler)

    print("Бот запущен, ожидаю события...")
    await app.run_polling()
    print("Polling завершен.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
