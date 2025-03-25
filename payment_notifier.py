import os
import logging
from datetime import datetime
from telegram import Bot
import asyncio
import re

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("payment_notifier.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "7809849560:AAHPQF54KnIzWMvj09KBJ9tTCkBjWuUktyA"
TRIBUTE_CHAT_ID = -6675346585  # ID чата Tribute
NOTIFICATIONS_CHAT_ID = -1002453479330  # ID чата для уведомлений

PAYMENT_PATTERNS = {
    "guide": r"Покупка гайда",
    "concierge": r"Предоплата за тревел-консьерж"
}

async def send_notification(bot: Bot, message: str):
    """Отправка уведомления в чат уведомлений"""
    try:
        await bot.send_message(
            chat_id=NOTIFICATIONS_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

async def process_tribute_message(bot: Bot, message_text: str):
    """Обработка сообщения из чата Tribute"""
    # Ищем username в сообщении (формат @username)
    username_match = re.search(r'@(\w+)', message_text)
    if not username_match:
        return

    username = username_match.group(1)
    
    # Определяем тип покупки
    purchase_type = None
    for p_type, pattern in PAYMENT_PATTERNS.items():
        if re.search(pattern, message_text):
            purchase_type = p_type
            break

    if purchase_type:
        notification_text = (
            f"🎉 <b>Новая покупка!</b>\n\n"
            f"👤 Пользователь: @{username}\n"
            f"📦 Тип покупки: {purchase_type}\n"
            f"💬 Сообщение: {message_text}\n"
            f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_notification(bot, notification_text)

async def main():
    """Основная функция"""
    print("Запускаю мониторинг чата Tribute...")
    print(f"ID чата Tribute: {TRIBUTE_CHAT_ID}")
    print(f"ID чата уведомлений: {NOTIFICATIONS_CHAT_ID}")
    
    bot = Bot(token=BOT_TOKEN)
    last_update_id = 0
    
    while True:
        try:
            # Получаем обновления
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=30)
            
            for update in updates:
                if update.message and update.message.chat.id == TRIBUTE_CHAT_ID:
                    await process_tribute_message(bot, update.message.text)
                    last_update_id = update.update_id
            
            # Ждем 5 секунд перед следующей проверкой
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main()) 