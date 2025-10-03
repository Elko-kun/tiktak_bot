import os
import time
import schedule
from telegram import Bot
from telegram.ext import Updater, CommandHandler
import datetime
import re
import threading

# Токен из переменных окружения
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    print("❌ ОШИБКА: Токен не найден!")
    print("💡 Добавьте TELEGRAM_BOT_TOKEN в настройки Render")
    exit(1)

# Настройки пользователей
user_settings = {}

def get_user_settings(chat_id):
    if chat_id not in user_settings:
        user_settings[chat_id] = {
            "name": "",
            "schedule": "1 minute", 
            "is_active": True
        }
    return user_settings[chat_id]

def start(update, context):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    settings = get_user_settings(chat_id)
    settings["name"] = user_name
    
    update.message.reply_text(
        f"Привет, {user_name}! 👋\n"
        f"✅ Вы подписаны на уведомления!\n"
        f"⏰ Уведомления приходят каждую минуту\n\n"
        f"⚙️ /settime - изменить расписание\n"
        f"📋 /help - список команд"
    )
    print(f"✅ Новый пользователь: {user_name} ({chat_id})")

def help_command(update, context):
    update.message.reply_text(
        "📋 Доступные команды:\n\n"
        "/start - подписаться на уведомления\n" 
        "/settime - установить время\n"
        "/help - эта справка\n\n"
        "⏰ Примеры:\n"
        "/settime 18:00 - каждый день в 18:00\n"
        "/settime 30 minutes - каждые 30 минут"
    )

def set_time(update, context):
    chat_id = update.effective_chat.id
    
    if not context.args:
        update.message.reply_text(
            "⏰ Укажите время:\n"
            "Пример: /settime 18:00\n" 
            "Или: /settime 30 minutes"
        )
        return
    
    time_input = " ".join(context.args)
    settings = get_user_settings(chat_id)
    
    if re.match(r'^\d{1,2}:\d{2}$', time_input):
        settings['schedule'] = f"каждый день в {time_input}"
        update.message.reply_text(f"✅ Установлено уведомление на {time_input}!")
    elif re.match(r'^(\d+)\s+(minutes?)$', time_input.lower()):
        match = re.match(r'^(\d+)\s+(minutes?)$', time_input.lower())
        minutes = match.group(1)
        settings['schedule'] = f"каждые {minutes} минут" 
        update.message.reply_text(f"✅ Установлены уведомления каждые {minutes} минут!")
    else:
        update.message.reply_text("❌ Неверный формат времени!")

def send_notifications():
    """Отправляет уведомления всем активным пользователям"""
    active_users = {cid: settings for cid, settings in user_settings.items() if settings["is_active"]}
    
    if not active_users:
        print("ℹ️ Нет активных пользователей для уведомления")
        return
    
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"🔔 [{current_time}] Отправляю уведомления {len(active_users)} пользователям...")
    
    bot = Bot(token=TOKEN)
    
    for chat_id, settings in active_users.items():
        try:
            send_message(bot, chat_id, settings['name'])
        except Exception as e:
            print(f"❌ Ошибка у пользователя {chat_id}: {e}")

def send_message(bot, chat_id, user_name):
    """Отправляет одно сообщение"""
    try:
        messages = [
            f"Привет, {user_name}! 🔔 Время сделать перерыв! 💧",
            f"{user_name}, ⏰ оторвитесь от экрана! 👀", 
            f"💡 {user_name}, время размяться! 🏃‍♂️",
            f"🌿 {user_name}, не забудьте про осанку! 🪑",
            f"💧 {user_name}, выпейте воды! 🥤"
        ]
        
        import random
        text = random.choice(messages)
        
        bot.send_message(chat_id=chat_id, text=text)
        print(f"✅ Уведомление отправлено {user_name}")
    except Exception as e:
        print(f"❌ Ошибка отправки {chat_id}: {e}")

def run_scheduler():
    """Запускает планировщик в отдельном потоке"""
    print("🕒 ПЛАНИРОВЩИК ЗАПУЩЕН!")
    
    # Проверяем каждую минуту
    schedule.every(1).minutes.do(send_notifications)
    
    print("🔄 Планировщик работает...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    print("=" * 50)
    print("🚀 БОТ ЗАПУСКАЕТСЯ НА RENDER")
    print("=" * 50)
    
    # Создаем updater
    updater = Updater(TOKEN, use_context=True)
    
    # Получаем диспетчер для регистрации обработчиков  
    dp = updater.dispatcher
    
    # Добавляем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("settime", set_time))
    
    # Запускаем планировщик в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    print("🤖 Бот запущен и готов к работе!")
    print("📝 Напишите /start в Telegram")
    print("-" * 50)
    
    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
