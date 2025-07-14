import cv2
import RPi.GPIO as GPIO
from picamera2 import Picamera2
import time

# this is the version used for the final implementation

face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

center_pos = (int(640 / 2), int(480 / 2))
current_offset = (None, None)

PI_SHOOT = 7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PI_SHOOT, GPIO.OUT, initial=GPIO.HIGH)


def get_target(faces):
    biggest = 0
    index = -1
    for i in range(len(faces)):
        size = faces[i][2] * faces[i][3]
        if size > biggest:
            biggest = size
            index = i
    if index == -1: return ()
    return [faces[index]]


def get_offset(faces):
    target = get_target(faces)
    for (x, y, w, h) in target:
        midpoint = (int(x + w / 2), int(y + h / 2))
        cv2.drawMarker(frame, midpoint, (0, 255, 0), 2)
        cv2.line(frame, midpoint, center_pos, (0, 255, 0), 2, cv2.LINE_AA)
        return -int(center_pos[0] - midpoint[0]), int(center_pos[1] - midpoint[1])
    return None, None


while True:
    frame = picam2.capture_array()
    frame = cv2.flip(frame, -1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    current_offset = get_offset(faces)
    GPIO.output(PI_SHOOT, GPIO.LOW if not current_offset[0] is None else GPIO.HIGH)# for some reason it's inverted???
    print(f"current offset: {current_offset}, GPIO_SHOOT: {'HIGH' if GPIO.input(PI_SHOOT) else 'LOW'}")
