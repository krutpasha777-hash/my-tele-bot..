import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- СЕРВЕР ДЛЯ RENDER (Порт 10000) ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Live and Reading!'

def run_flask():
    # Render требует порт 10000 для Free тира
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- НАСТРОЙКИ БОТА ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957" # Твой личный ключ

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🎯 Конфликт исправлен! Личный ключ активен. Жду твой список.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚙️ Сканирую личным ключом (Engine 2)...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        payload = {
            'url': file_url,
            'apikey': API_KEY,
            'language': 'rus',
            'OCREngine': '2', # Лучший движок для рукописи
            'scale': 'true'
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=30)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText']
            # Ищем все числа от 1 до 1000
            prices = [int(n) for n in re.findall(r'\d+', text) if 1 <= int(n) <= 1000]
            total = sum(prices)
            
            report = f"✅ **Я увидел:**\n`{text}`\n\n💰 **СУММА:** {total} грн"
            bot.send_message(message.chat.id, report)
        else:
            bot.send_message(message.chat.id, "❌ ИИ не смог прочитать текст. Попробуй чуть дальше держать камеру.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Сервер занят, подожди 10 секунд и отправь снова.")

# СБРОС СТАРЫХ ПОДКЛЮЧЕНИЙ (Лечит ошибку 409)
bot.remove_webhook()
bot.polling(none_stop=True)
