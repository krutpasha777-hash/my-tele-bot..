import telebot
import requests
import re
from flask import Flask
import threading
import time

# --- СЕРВЕР (чтобы Render не отключал бота) ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Accounting System Active'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

# --- НАСТРОЙКИ И ПРАЙС-ЛИСТ ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957"

# Твой актуальный прайс
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
    bot.reply_to(message, "🔢 Считаю по прайсу, секунду...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Запрос к нейросети (OCR)
        payload = {'url': file_url, 'apikey': API_KEY, 'language': 'rus', 'OCREngine': '2', 'scale': 'true'}
        r = requests.post('https://api.ocr.space/parse/image', data=payload)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText'].lower()
            
            report = "📝 **ОТЧЕТ ПО РАБОТЕ:**\n\n"
            total_sum = 0
            found_anything = False

            # Логика поиска: Деталь -> Модель -> Количество
            for item, price in PRICES.items():
                if item in text:
                    # Ищем число, которое идет ПОСЛЕ названия детали
                    # Например: "колесо 113 - 8"
                    match = re.search(rf"{item}.*?(\d+)", text)
                    if match:
                        count = int(match.group(1))
                        # Если число совпадает с моделью (113, 88, 600), ищем следующее число в строке
                        if count in [113, 88, 600]:
                            numbers = re.findall(r'\d+', text.split(item)[1])
                            if len(numbers) > 1:
                                count = int(numbers[1])
                            else: continue

                        cost = count * price
                        total_sum += cost
                        report += f"🔹 {item.upper()}: {count} шт. × {price} = {cost} грн\n"
                        found_anything = True

            if found_anything:
                report += f"\n💰 **ИТОГО ЗА СЕГОДНЯ: {total_sum} грн**"
                report += f"\n📅 {time.strftime('%d.%m.%Y')}"
                bot.send_message(message.chat.id, report)
            else:
                bot.send_message(message.chat.id, "🔍 Не узнал детали из прайса. Проверь названия в списке!")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось прочитать фото.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Система занята. Попробуй еще раз через 15 секунд.")

# ФИНАЛЬНЫЙ СБРОС (лечит ошибку 409)
if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    bot.polling(none_stop=True)
