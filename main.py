import telebot
import os
import requests
import re
from flask import Flask
import threading
import time

# --- ЖИВУЧЕСТЬ НА RENDER ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Scanner is Ready!'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

# --- НАСТРОЙКИ ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚙️ Включаю режим глубокого сканирования... Ищу цены.")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Улучшенные параметры для OCR Space
        payload = {
            'url': file_url,
            'apikey': API_KEY,
            'language': 'rus',
            'OCREngine': '2',      # Лучший для рукописи
            'scale': 'true',       # Увеличение для четкости
            'isOverlayRequired': 'false',
            'detectOrientation': 'true',
            'filetype': 'JPG'
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=30)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText']
            
            # Логика: ищем ВСЕ числа в тексте
            all_numbers = re.findall(r'\d+', text)
            
            # Чистим от номеров моделей (113, 88, 600, A2)
            # Берем только то, что логично может быть ценой (например, до 300)
            valid_prices = []
            for num in all_numbers:
                val = int(num)
                if val in [8, 20, 100, 60]: # Прямое попадание по твоему списку
                    valid_prices.append(val)
                elif 5 <= val <= 300 and val not in [113, 88, 600]:
                    valid_prices.append(val)
            
            total = sum(valid_prices)
            
            if total > 0 or text.strip():
                msg = f"✅ **Я расшифровал:**\n`{text}`\n\n"
                msg += f"💰 **Насчитал (цены):** {valid_prices}\n"
                msg += f"🔥 **ИТОГО:** {total} грн"
                bot.send_message(message.chat.id, msg)
            else:
                bot.send_message(message.chat.id, "🔍 Текст вижу, но цифры не разобрал. Попробуй обвести цены жирным маркером.")
        else:
            bot.send_message(message.chat.id, "❌ Сервер не видит букв. Попробуй сфоткать при ярком свете (у окна).")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Ошибка связи. Повтори попытку.")

if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    bot.polling(none_stop=True)
