#!/bin/bash

# Активируем виртуальное окружение
source /home/ubuntu/telega_env/bin/activate

# Запускаем основной бот в фоновом режиме
nohup python /home/ubuntu/2ushka_telegram_bot/bot.py > /home/ubuntu/2ushka_telegram_bot/bot1.log 2>&1 &
echo "Основной бот запущен с PID $!"

# Запускаем мониторинг покупок в фоновом режиме
nohup python /home/ubuntu/2ushka_telegram_bot/payment_notifier.py > /home/ubuntu/2ushka_telegram_bot/payment_notifier.log 2>&1 &
echo "Мониторинг покупок запущен с PID $!"

# Выводим информацию о логах
echo "Логи основного бота: /home/ubuntu/2ushka_telegram_bot/bot.log"
echo "Логи мониторинга покупок: /home/ubuntu/2ushka_telegram_bot/payment_notifier.log"

# Проверяем статус процессов
echo -e "\nСтатус процессов:"
ps aux | grep -E "bot.py|payment_notifier.py" | grep -v grep 