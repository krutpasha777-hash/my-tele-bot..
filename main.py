import telebot
import requests
import re
import time
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def hello(): return 'Accounting System Active'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957"

# Твой прайс
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
    bot.reply_to(message, "🔢 Чистая загрузка... Считаю по прайсу.")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # OCR
        payload = {'url': file_url, 'apikey': API_KEY, 'language': 'rus', 'OCREngine': '2'}
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=25)
        result = r.json()
        
        if 'ParsedResults' in result:
            raw_text = result['ParsedResults'][0]['ParsedText'].lower()
            
            report = "📝 **ВЕДОМОСТЬ:**\n\n"
            total = 0
            found = False

            # Ищем каждую деталь из прайса
            for item, price in PRICES.items():
                if item in raw_text:
                    # Ищем число в радиусе 10 символов от названия детали
                    # Это поможет, если тире или пробелы прочитались криво
                    match = re.search(rf"{item}.*?(\d+)", raw_text)
                    if match:
                        count = int(match.group(1))
                        # Проверка на модель
                        if count in [113, 88, 600]:
                            nums = re.findall(r'\d+', raw_text.split(item)[1])
                            if len(nums) > 1: count = int(nums[1])
                            else: continue

                        cost = count * price
                        total += cost
                        report += f"✅ {item.upper()}: {count} шт. × {price} = {cost} грн\n"
                        found = True

            if found:
                report += f"\n💰 **ИТОГО К ОПЛАТЕ: {total} грн**"
                bot.send_message(message.chat.id, report)
            else:
                bot.send_message(message.chat.id, f"🔍 Детали не узнал. Текст:\n`{raw_text}`")
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Ошибка. Сделай Manual Deploy на Render.")

if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(2)
    bot.polling(none_stop=True)
