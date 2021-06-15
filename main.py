import cv2 as cv
from buffer import Buffer
from datetime import datetime
import threading
import os
import sys
import time
import signal
import telebot

#Define constants
FPS = 20.0
VIDEO_LENGTH = 5 # In seconds
TOKEN = os.environ['TELEGRAM_TOKEN']

buff = Buffer(FPS*VIDEO_LENGTH)
recording = 0
exit_event = threading.Event()
#app = telebot.TeleBot(__name__)
#bot = telebot.TeleBot(TOKEN, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

class AddDaemon(object):
    def __init__(self):
        self.cap = cv.VideoCapture(0)
        # Define the codec and create VideoWriter object
        self.fourcc = cv.VideoWriter_fourcc(*'mp4v')

    def add(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            frame = cv.flip(frame, 90)
            buff.put(frame)
            cv.imshow('frame', frame)
            if exit_event.is_set():
                self.free()
                break

    def free(self):
        print("Esto se esta cerrando?")
        self.cap.release()
        cv.destroyAllWindows()

def signal_handler(signum, frame):
    exit_event.set()
"""
@bot.message_handler(commands=['getVideo'])
def send_video(message):
	#bot.reply_to(message, "Howdy, how are you doing?")
    #video = open('record-14-06-2021-19-32-07.mp4', 'rb')

    print("Saving last 5 seconds")
    #filename = "record-{}.mp4".format(datetime.today().strftime('%d-%m-%Y-%H-%M-%S'))
    #out = cv.VideoWriter(filename, a.fourcc, FPS, (640, 480))
    ## Release everything if job is finished
    #for i in buff.getbuff():
    #    out.write(i)
    #out.release()
    #video = open(filename, 'rb')
    #
    #bot.send_video(message.chat.id, video)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)
"""

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    a = AddDaemon()
    t2 = threading.Thread(target=a.add)
    t2.setDaemon(True)
    t2.start()
    #bot.polling()
    while not exit_event.is_set():
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
