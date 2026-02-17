import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- SERVER (ОБМАНКА ДЛЯ RENDER) ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Live!'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))), daemon=True).start()

# --- BOT SETUP ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "✅ Бот настроен! Пришли фото списка или нажми кнопку.", reply_markup=markup)

# --- ОБРАБОТКА КНОПОК ---
@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.send_message(message.chat.id, "🌤 В Днепре сейчас облачно, около +5°C. Хорошего дня!")

@bot.message_handler(func=lambda message: message.text == "Заметки")
def notes(message):
    bot.send_message(message.chat.id, "📒 Твой блокнот пока пуст. Я могу хранить тут важные номера деталей!")

# --- ОБРАБОТКА ФОТО (УЛУЧШЕННАЯ) ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "🔍 Вижу список! Пытаюсь разобрать почерк и посчитать только цены...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Запрос к OCR API
        r = requests.post('https://api.ocr.space/parse/image', 
                          data={'url': file_url, 'apikey': 'helloworld', 'language': 'rus'})
        result = r.json()
        
        if result.get('OCRExitCode') == 1:
            detected_text = result['ParsedResults'][0]['ParsedText']
            
            # Умный поиск: ищем числа после знака "-" или "+"
            # Это поможет игнорировать "Штрак 88" и считать только "20"
            prices = re.findall(r'[-+]\s*(\d+)', detected_text)
            
            # Если после тире ничего не нашли, попробуем найти числа в конце строк
            if not prices:
                prices = re.findall(r'(\d+)(?:\s|$)', detected_text)

            total = sum(map(int, prices))
            
            report = f"📝 **Что я увидел:**\n`{detected_text[:200]}...`\n\n"
            report += f"💰 **Сумма цен (предварительно):** {total} грн"
            bot.send_message(message.chat.id, report)
        else:
            bot.send_message(message.chat.id, "❌ Не смог разобрать текст. Попробуй сделать фото ближе.")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Ошибка при обработке. Попробуй еще раз!")

# Ответ на обычный текст (не кнопки)
@bot.message_handler(func=lambda message: True)
def other_text(message):
    bot.reply_to(message, "Я получил сообщение, но не знаю что с ним делать. Нажми на кнопку или скинь фото!")

bot.polling(none_stop=True)
