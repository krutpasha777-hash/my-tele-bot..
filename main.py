import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- СЕРВЕР ДЛЯ RENDER (Порт 10000 как просит лог) ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Live!'

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- НАСТРОЙКИ БОТА ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957" # Твой ключ из письма

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🎯 Личный ключ и порт 10000 настроены! Жду фото.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚙️ Считаю через твой личный канал...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Используем твой личный API_KEY
        payload = {
            'url': file_url,
            'apikey': API_KEY,
            'language': 'rus',
            'OCREngine': '2',
            'scale': 'true'
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText']
            # Ищем числа от 1 до 500
            prices = [int(n) for n in re.findall(r'\d+', text) if 1 <= int(n) <= 500]
            total = sum(prices)
            
            bot.send_message(message.chat.id, f"✅ **Распознано:**\n`{text}`\n\n💰 **ИТОГО:** {total} грн")
        else:
            bot.send_message(message.chat.id, "❌ Не смог разобрать. Проверь, нет ли бликов на бумаге.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Система перезагружается. Попробуй через 30 секунд.")

# Удаляем вебхуки перед запуском, чтобы не было ошибки 409
bot.remove_webhook()
bot.polling(none_stop=True)
