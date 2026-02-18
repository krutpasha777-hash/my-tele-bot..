import telebot
import time

TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Гриша на связи! Если видишь это — сервер работает. Жду фото.")

@bot.message_handler(content_types=['photo'])
def handle(message):
    bot.reply_to(message, "Фото получил, начинаю обработку...")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling(none_stop=True)
