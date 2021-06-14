#import numpy as np
import cv2 as cv
from buffer import Buffer
from datetime import datetime

#Define constants
FPS = 20.0
VIDEO_LENGTH = 5 # In seconds

cap = cv.VideoCapture(0)
# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*'XVID')

buff = Buffer(FPS*VIDEO_LENGTH)

recording = 0

while cap.isOpened():
    ret, frame = cap.read()
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
        filename = "record-{}.avi".format(datetime.today().strftime('%d-%m-%Y-%H-%M-%S'))
        out = cv.VideoWriter(filename, fourcc, FPS, (640, 480))
        # Release everything if job is finished
        for i in buff.getbuff():
            out.write(i)
        out.release()

cap.release()
cv.destroyAllWindows()
