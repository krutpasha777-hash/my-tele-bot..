import telebot
import os
import time
import threading
import re
import requests
import io
from flask import Flask
from PIL import Image

# --- НАСТРОЙКИ СЕРВЕРА (ОБМАНКА ДЛЯ RENDER) ---
app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Bot is running!'

def run_flask():
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Запускаем веб-сервер в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

# --- НАСТРОЙКИ БОТА ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN)

# --- ФУНКЦИИ КНОПОК (ТВОЙ ПРЕДЫДУЩИЙ КОД) ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "Привет! Я твой бот-помощник. Теперь я умею считать суммы с фото!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Итоги")
def show_summary(message):
    bot.send_message(message.chat.id, "Тут скоро будет твоя статистика!")

# --- НОВАЯ ФУНКЦИЯ: РАБОТА С ФОТО ---

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 Вижу фото! Анализирую текст, это займет пару секунд...")
    
    try:
        # 1. Получаем файл из Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # 2. Отправляем на бесплатный OCR API (ocr.space)
        payload = {
            'url': file_url,
            'apikey': 'helloworld', # Тестовый ключ
            'language': 'rus',
            'isOverlayRequired': False,
            'FileType': 'JPG',
        }
        
        response = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=15)
        result = response.json()
        
        if result.get('OCRExitCode') == 1:
            detected_text = result['ParsedResults'][0]['ParsedText']
            
            # 3. Ищем все числа в тексте (цены)
            # Находим всё, что похоже на числа (целые или с точкой)
            prices = re.findall(r'\d+', detected_text)
            
            # Превращаем строки в числа и суммируем
            total = sum(int(p) for p in prices)
            
            report = f"📝 **Распознанный текст:**\n\n{detected_text[:500]}...\n\n"
            report += f"🔢 **Нашел чисел на сумму:** {total}"
            
            bot.send_message(message.chat.id, report)
        else:
            bot.send_message(message.chat.id, "❌ Не удалось прочитать текст. Попробуй сделать фото ближе и четче.")
            
    except Exception as e:
        print(f"Ошибка OCR: {e}")
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка при обработке фото. Попробуй позже.")

# --- ОБРАБОТКА ЛЮБОГО ДРУГОГО ТЕКСТА ---
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Я получил твое сообщение. Нажми на кнопки или пришли фото списка покупок!")

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("--- БОТ УСПЕШНО ЗАПУЩЕН НА RENDER ---")
    bot.polling(none_stop=True)
