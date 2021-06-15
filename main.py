import cv2 as cv
from buffer import Buffer
from datetime import datetime
import threading
import os
import sys
import time
import signal
import telebot
import serial

#Define constants
FPS = 20.0
VIDEO_LENGTH = 5 # In seconds
BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
BOT_INTERVAL = 3
BOT_TIMEOUT = 30
CHAT_ID = os.environ['CHAT_ID']     # Use the script telegramGetChatID to get
                                    # the chat identifier where you want to send videos
COM_PORT = os.environ['COM_PORT']

buff = Buffer(FPS*VIDEO_LENGTH)
recording = 0
exit_event = threading.Event()
fourcc = cv.VideoWriter_fourcc(*'mp4v')

bot = telebot.TeleBot(BOT_TOKEN) #Generate new bot instance

arduino = None

class UartDaemon:
    def listen_uart(self):
        print("Listening to port {}".format(COM_PORT))
        global arduino
        while not exit_event.is_set():
            try:
                if arduino.readline().strip() == 'EA4RCT':
                    print("Detected!\n")
                    self.sendVideo()
            except:
                print("Failed to read from COM port")

    def sendVideo(self):
        filename = "record-{}.mp4".format(datetime.today().strftime('%d-%m-%Y-%H-%M-%S'))
        out = cv.VideoWriter(filename, fourcc, FPS, (640, 480))
        # Release everything if job is finished
        for i in buff.getbuff():
            out.write(i)
        out.release()
        video = open(filename, 'rb')
        bot.send_video(CHAT_ID, video)


class TelBotDaemon:
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
        @bot.message_handler(commands=['getVideo'])
        def send_video(message):
            print("Saving last 5 seconds")
            filename = "record-{}.mp4".format(datetime.today().strftime('%d-%m-%Y-%H-%M-%S'))
            out = cv.VideoWriter(filename, fourcc, FPS, (640, 480))
            # Release everything if job is finished
            for i in buff.getbuff():
                out.write(i)
            out.release()
            video = open(filename, 'rb')

            bot.send_video(message.chat.id, video)

        @bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            bot.reply_to(message, "Howdy, how are you doing?")

        @bot.message_handler(func=lambda m: True)
        def echo_all(message):
            bot.reply_to(message, message.text)


class CameraDaemon(object):
    def __init__(self):
        self.cap = cv.VideoCapture(0)
        # Define the codec and create VideoWriter object

    def add(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            frame = cv.flip(frame, 90)
            buff.put(frame)
            if exit_event.is_set():
                self.free()
                break

    def free(self):
        print("Esto se esta cerrando?")
        self.cap.release()

    def getfourcc(self):
        return fourcc

def signal_handler(signum, frame):
    exit_event.set()

def main():
    print("Running TelegramReplays Script")

    if COM_PORT:
        print("Opening serial port {}".format(COM_PORT))
        try:
            global arduino
            arduino = serial.Serial(COM_PORT, 9600)
        except:
            print("Failed to connect on {}".format(COM_PORT))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    camDaemon = CameraDaemon()
    telDaemon = TelBotDaemon()
    uartDaemon = UartDaemon()
    t2 = threading.Thread(target=camDaemon.add)
    polling_thread = threading.Thread(target=telDaemon.bot_polling)
    uart_thread = threading.Thread(target=uartDaemon.listen_uart)
    t2.setDaemon(True)
    polling_thread.setDaemon(True)
    uart_thread.setDaemon(True)
    t2.start()
    polling_thread.start()
    if COM_PORT:
        uart_thread.start()

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
