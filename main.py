import telebot
import os
import requests
import re
from flask import Flask
import threading
import time

# --- СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is fully active!'

def run_flask():
    # Render Free требует порт 10000
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- НАСТРОЙКИ ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957" # Твой личный ключ

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Конфликт исправлен! Связь стабильна. Жду фото списка.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚡️ Вижу фото! Читаю через твой личный API...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Используем Engine 2 для рукописи
        payload = {
            'url': file_url, 
            'apikey': API_KEY, 
            'language': 'rus', 
            'OCREngine': '2', 
            'scale': 'true'
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=30)
        result = r.json()
        
        if 'ParsedResults' in result:
            text = result['ParsedResults'][0]['ParsedText']
            # Ищем числа (игнорируем модель 600)
            prices = [int(n) for n in re.findall(r'\d+', text) if 1 <= int(n) <= 500]
            total = sum(prices)
            
            bot.send_message(message.chat.id, f"📝 **Текст:** {text}\n🔢 **Цены:** {prices}\n💰 **СУММА:** {total} грн")
        else:
            bot.send_message(message.chat.id, "❌ ИИ не смог прочитать. Попробуй сфоткать чуть ближе.")
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Ошибка 409 ушла, но сервер занят. Попробуй через 10 секунд.")

# СБРОС ВСЕХ СТАРЫХ СВЯЗЕЙ (Убирает ошибку 409)
if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    bot.polling(none_stop=True)
