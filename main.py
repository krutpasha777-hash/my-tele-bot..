import telebot
import os
import time
import threading
import random
import re
from telebot import types
from flask import Flask # Добавили эту библиотеку

# --- МИНИ-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Bot is running!'

def run_flask():
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))

# Запускаем веб-сервер в отдельном потоке
threading.Thread(target=run_flask).start()
# -------------------------------------

TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN, threaded=False)

# ... (весь твой остальной код бота без изменений) ...
# Вставь сюда все функции: send_reminder, main_keyboard, start, 
# show_summary, weather, motivation, show_fin, show_not, clear_all, handle_all

# В самом конце оставь это:
print("--- БОТ ЗАПУЩЕН НА СЕРВЕРЕ ---")
while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=20)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)
