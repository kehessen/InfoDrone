import cv2
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# will detect faces and aim the "thruster" at them. in case of vertical aiming (pitch) implementation,
# the aim point shouldn't be in the face of the target.
# In our case, there will only be horizontal (yaw) turning so the vertical hit point will solely depend on the drone height
# and distance from the target

# this drone function will be used to avoid accidentally flying into any people as the drone will quickly escape in the opposite direction
# we have decided to use this type of thruster so it will even work in a vacuum and there is no chance of flying into a person


# this is the testing version, nopreview.py will be used for the raspberry pi implementation

face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})

picam2.configure(config)
picam2.start()

# change depending on camera pos
center_pos = (int(640 / 2), int(480 / 2))

current_offset = (None, None)

# GPIO pins
# PI_STEP = 11
# PI_DIR = 13
PI_SHOOT = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PI_SHOOT, GPIO.OUT, initial=GPIO.LOW)

# depends on camera resolution
# px_per_step = 8


# negative steps to go the other direction
def move_x(steps: int):
    pass


def move_y(steps: int):
    pass


def draw_rect(faces):
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)


def draw_circ(faces):
    for (x, y, w, h) in faces:
        cv2.circle(frame, (int(x + w / 2), int(y + h / 2)), int(w / 2), (0, 0, 255), 3)


def get_target(faces):
    biggest = 0
    index = -1
    for i in range(len(faces)):
        size = faces[i][2] * faces[i][3]
        if size > biggest:
            biggest = size
            index = i
    if index == -1: return []
    return [faces[index]]


def draw_and_get_offset(faces):
    draw_rect(faces)
    target = get_target(faces)
    draw_circ(target)
    for (x, y, w, h) in target:
        midpoint = (int(x + w / 2), int(y + h / 2))
        cv2.drawMarker(frame, midpoint, (0, 255, 0), 2)
        cv2.line(frame, midpoint, center_pos, (0, 255, 0), 2, cv2.LINE_AA)
        return -int(center_pos[0] - midpoint[0]), int(center_pos[1] - midpoint[1])
    return -1, -1


while True:
    frame = picam2.capture_array()
    frame = cv2.flip(frame, -1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
    current_offset = draw_and_get_offset(faces)
    print(f"current offset: {current_offset}, GPIO_SHOOT: {'HIGH' if GPIO.input(PI_SHOOT) else 'LOW'}")
    GPIO.output(PI_SHOOT, GPIO.LOW if not current_offset[0] is None else GPIO.HIGH)# for some reason it's inverted on the relais???
    cv2.imshow('Face Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
