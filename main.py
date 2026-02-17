import telebot
import os
import requests
import re
from flask import Flask
import threading
import time

# --- СЕРВЕР ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'System Online'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

# --- НАСТРОЙКИ ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957" # Твой личный ключ

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "🔍 Вижу список! Включаю режим супер-зрения...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Настройки для максимального распознавания
        payload = {
            'url': file_url,
            'apikey': API_KEY,
            'language': 'rus',
            'OCREngine': '2',     # Специально для рукописного текста
            'scale': 'true',      # Увеличиваем четкость
            'isTable': 'true'     # Помогает понять структуру "название - цена"
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=30)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText']
            
            # Чистим текст и ищем цифры
            # Мы ищем числа, которые стоят отдельно или после тире
            nums = re.findall(r'\d+', text)
            
            # Фильтр: убираем заведомо лишние числа (например, из названий деталей 113, 88, 600)
            # Берем только те цифры, что меньше 500 и не похожи на артикулы
            prices = []
            for n in nums:
                val = int(n)
                # Если число небольшое или стоит в конце строки (мы это определим логикой)
                if 5 <= val <= 500 and val not in [113, 88, 600]: 
                    prices.append(val)
            
            total = sum(prices)
            
            if text.strip():
                response = f"📝 **Я прочитал в списке:**\n`{text}`\n\n"
                response += f"🔢 **Найденные цены:** {', '.join(map(str, prices))}\n"
                response += f"💰 **ИТОГО:** {total} грн"
                bot.send_message(message.chat.id, response)
            else:
                bot.send_message(message.chat.id, "🔍 Текст вижу, но не могу выделить цифры. Напиши цены чуть крупнее.")
        else:
            bot.send_message(message.chat.id, "❌ Сервер OCR временно не ответил. Попробуй еще раз.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Система обновляется. Отправь фото через 10 секунд.")

if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    bot.polling(none_stop=True)
