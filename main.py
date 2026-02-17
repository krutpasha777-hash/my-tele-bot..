import telebot
import requests
import re
from flask import Flask
import threading
import time

# --- СЕРВЕР ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Accounting System Active'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

# --- НАСТРОЙКИ ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957"

# Прайс-лист (ключевые слова для поиска)
PRICES = {
    'колесо 113': 40,
    'трак 88': 10,
    'башмак а2': 2,
    'колесо 600': 50,
    'палец 88': 7
}

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "🔢 Запускаю расширенный поиск по прайсу...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # OCR с улучшенным движком
        payload = {'url': file_url, 'apikey': API_KEY, 'language': 'rus', 'OCREngine': '2', 'scale': 'true'}
        r = requests.post('https://api.ocr.space/parse/image', data=payload)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            raw_text = result['ParsedResults'][0]['ParsedText'].lower()
            # Убираем лишние знаки, оставляем только буквы и цифры
            clean_text = re.sub(r'[^а-я0-9\s-]', '', raw_text)
            
            report = "📝 **ОТЧЕТ ПО РАБОТЕ:**\n\n"
            total_sum = 0
            found_anything = False

            # Разбиваем текст на строки
            lines = clean_text.split('\n')
            
            for line in lines:
                for item, price in PRICES.items():
                    # Проверяем, есть ли название детали в строке
                    if item in line:
                        # Ищем все числа в этой строке
                        nums = re.findall(r'\d+', line)
                        if nums:
                            # Берем последнее число (обычно это количество)
                            count = int(nums[-1])
                            
                            # Если число — это не модель (113, 88, 600)
                            if count not in [113, 88, 600] or (len(nums) > 1 and count == int(nums[-1])):
                                cost = count * price
                                total_sum += cost
                                report += f"🔹 {item.upper()}: {count} шт. × {price} = {cost} грн\n"
                                found_anything = True
                                break # Переходим к следующей строке

            if found_anything:
                report += f"\n💰 **ИТОГО: {total_sum} грн**"
                report += f"\n📅 {time.strftime('%d.%m.%Y')}"
                bot.send_message(message.chat.id, report)
            else:
                bot.send_message(message.chat.id, f"🔍 Не нашел детали в прайсе.\nТекст, который я увидел:\n`{raw_text}`")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось прочитать фото.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Попробуй еще раз через 10 секунд.")

if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    bot.polling(none_stop=True)
