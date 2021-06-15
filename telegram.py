import telebot
import os

from telebot import TeleBot

app = TeleBot(__name__)
TOKEN = os.environ['TELEGRAM_TOKEN']

bot = telebot.TeleBot(TOKEN, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

@bot.message_handler(commands=['getVideo'])
def send_video(message):
	#bot.reply_to(message, "Howdy, how are you doing?")
    video = open('record-14-06-2021-19-32-07.mp4', 'rb')
    bot.send_video(message.chat.id, video)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.polling()