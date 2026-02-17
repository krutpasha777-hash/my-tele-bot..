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
    # Используем стандартный порт 10000
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- НАСТРОЙКИ ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957" # Твой личный ключ

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Связь установлена! Ошибка 409 побеждена. Присылай фото списка.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚡️ Вижу фото! Читаю личным ключом...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Настройки Engine 2 для лучшего распознавания рукописи
        r = requests.post('https://api.ocr.space/parse/image', 
                          data={'url': file_url, 'apikey': API_KEY, 'language': 'rus', 'OCREngine': '2', 'scale': 'true'},
                          timeout=30)
        result = r.json()
        
        if 'ParsedResults' in result:
            text = result['ParsedResults'][0]['ParsedText']
            # Ищем числа (игнорируем модель 600)
            prices = [int(n) for n in re.findall(r'\d+', text) if 1 <= int(n) <= 500]
            total = sum(prices)
            
            bot.send_message(message.chat.id, f"📝 **Текст:** {text}\n🔢 **Цены:** {prices}\n💰 **СУММА:** {total} грн")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось прочитать. Попробуй еще раз.")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Ошибка связи. Подожди пару секунд и повтори.")

# ФИНАЛЬНЫЙ СБРОС (Чистим все старые сессии перед стартом)
if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    bot.polling(none_stop=True)
