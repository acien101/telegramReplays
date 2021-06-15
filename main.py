import cv2 as cv
from buffer import Buffer
from datetime import datetime
import threading
import os
import sys
import time
import signal

#Define constants
FPS = 20.0
VIDEO_LENGTH = 5 # In seconds



buff = Buffer(FPS*VIDEO_LENGTH)
recording = 0
exit_event = threading.Event()

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
            if cv.waitKey(1) == ord('q'):
                break
            if cv.waitKey(1) == ord('r'):
                print("Saving last 5 seconds")
                filename = "record-{}.mp4".format(datetime.today().strftime('%d-%m-%Y-%H-%M-%S'))
                out = cv.VideoWriter(filename, self.fourcc, FPS, (640, 480))
                # Release everything if job is finished
                for i in buff.getbuff():
                    out.write(i)
                out.release()
            if exit_event.is_set():
                self.free()
                break

    def free(self):
        print("Esto se esta cerrando?")
        self.cap.release()
        cv.destroyAllWindows()

def signal_handler(signum, frame):
    exit_event.set()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    a = AddDaemon()
    t2 = threading.Thread(target=a.add)
    t2.setDaemon(True)
    t2.start()
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
