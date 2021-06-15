import threading
import os
import sys
import time
import signal
import telebot

#Define constants
BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
BOT_INTERVAL = 3
BOT_TIMEOUT = 30

exit_event = threading.Event()

bot = telebot.TeleBot(BOT_TOKEN) #Generate new bot instance

class telBotDaemon:
    def bot_polling(self):
        #global bot #Keep the bot object as global variable if needed
        print("Starting bot polling now")
        while True:
            try:
                print("New bot instance started")
                self.botactions(bot) #If bot is used as a global variable, remove bot as an input param
                bot.polling(none_stop=True, interval=BOT_INTERVAL, timeout=BOT_TIMEOUT)
                if exit_event.is_set():
                    raise Exception('Script interrupted by external SIGINT')
            except Exception as ex: #Error in polling
                print("Bot polling failed, restarting in {}sec. Error:\n{}".format(BOT_TIMEOUT, ex))
                bot.stop_polling()
                time.sleep(BOT_TIMEOUT)
            else: #Clean exit
                bot.stop_polling()
                print("Bot polling loop finished")
                break #End loop


    def botactions(self, bot):
        @bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            bot.reply_to(message, "Your Chat id is {}".format(message.chat.id))
            print("YOUR CHAT IDENTIFIER IS {}".format(message.chat.id))


def signal_handler(signum, frame):
    exit_event.set()

def main():
    print("Running Script get getting Chat id, please send /start in the bot where you want the chat id")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    telDaemon = telBotDaemon()
    polling_thread = threading.Thread(target=telDaemon.bot_polling)
    polling_thread.setDaemon(True)
    polling_thread.start()

    while True:
        try:
            time.sleep(120)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
