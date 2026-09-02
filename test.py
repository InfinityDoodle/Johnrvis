import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import pyautogui
import math
import sys
import traceback
import threading
import calc
pyautogui.FAILSAFE = False
pyautogui.PAUSE = .01

global t
t = time.time()
global open_init
open_init = [False, t]
global init_code
init_code = [0, 0, 0]
global mouse_hand
mouse_hand = 0
global util_hand
util_hand = None

#thumb_tip = hand.hand_landmarks[0][4]
#index_tip = hand.hand_landmarks[0][8]
#middle_tip = hand.hand_landmarks[0][12]
#ring_tip = hand.hand_landmarks[0][16]
#pinky_tip = hand.hand_landmarks[0][20]


def calc(ges, thumb, index, middle, ring, pinky, world, landmarks, handedness, full_ges):
    calc.password(ges, thumb, index, middle, ring, pinky)
    calc.hand_choice(full_ges)
    if open_init[0]:
        palm = calc.detect_palm(handedness, world)
        calc.mouse_control(ges, thumb, index, middle, ring, pinky, world, landmarks, palm, full_ges)

def call(ges, mp_image: mp.Image, timestamp_ms: int):
    global t
    global open_init
    open_init = calc.open_init
    global init_code
    init_code = calc.init_code
    global mouse_hand
    mouse_hand = calc.mouse_hand
    global util_hand
    util_hand = calc.util_hand

    image_np = mp_image.numpy_view()
    frame = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    #height, width = frame.shape
    try:
        hand = ges
        try:
            hand_world = ges.hand_world_landmarks[mouse_hand]
            #print(ges.gestures[mouse_hand])

            thumb_tip = hand.hand_landmarks[mouse_hand][4]
            index_tip = hand.hand_landmarks[mouse_hand][8]
            middle_tip = hand.hand_landmarks[mouse_hand][12]
            ring_tip = hand.hand_landmarks[mouse_hand][16]
            pinky_tip = hand.hand_landmarks[mouse_hand][20]
        except:
            mouse_hand = 0
            util_hand = None

            hand_world = ges.hand_world_landmarks[mouse_hand]

            thumb_tip = hand.hand_landmarks[mouse_hand][4]
            index_tip = hand.hand_landmarks[mouse_hand][8]
            middle_tip = hand.hand_landmarks[mouse_hand][12]
            ring_tip = hand.hand_landmarks[mouse_hand][16]
            pinky_tip = hand.hand_landmarks[mouse_hand][20]

        if open_init[0]:
            for x in hand.hand_landmarks:
                mp.tasks.vision.drawing_utils.draw_landmarks(frame, x)
                # frame = cv2.circle(frame, center=(int(x), int(y)), radius=5, color=(0, 0, 255), thickness=-1)
        # print(ges.gestures[0][0].category_name)
        # print(hand.hand_landmarks[0])
        # print(init_code)
        # print(open_init)
        calc(ges.gestures[mouse_hand][0].category_name, thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip,
         hand_world, hand.hand_world_landmarks[mouse_hand], ges.handedness, ges)

    except Exception as e:
        if init_code[0] > 0:
            init_code[0] -= 1
        if init_code[1] > 0:
            init_code[1] -= 1
        if init_code[2] > 0:
            init_code[2] -= 12
        _, _, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno

        print(f"Error: '{e}' occurred on line {line_number}")

    if open_init[0]:
        frame = cv2.flip(frame, 1)
        cv2.namedWindow("John", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("John", cv2.WND_PROP_TOPMOST, 1)
        cv2.moveWindow("John", 0, 0)
        cv2.resizeWindow("John", int(1920 / 7), int(1920 / 10))
        cv2.imshow("John", frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            return
    else:
        cv2.destroyAllWindows()

def track():
    global open_init
    BaseOptions = mp.tasks.BaseOptions
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    mp_drawing = mp.tasks.vision.drawing_utils


    ges_path = r"C:\Users\jgdiv\PyCharmMiscProject\net\gesture_recognizer.task"
    hand_path = r"C:\Users\jgdiv\PyCharmMiscProject\net\hand_landmarker.task"

    ges_options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=ges_path),
        running_mode=VisionRunningMode.LIVE_STREAM, num_hands=2,
        min_hand_detection_confidence=.6,
        min_hand_presence_confidence=.6,
        min_tracking_confidence=.6, result_callback=call)
    cap = cv2.VideoCapture(0)
    time_stamp = 0
    with GestureRecognizer.create_from_options(ges_options) as recognizer:
        global util_hand
        global mouse_hand
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Video capture failed")
                break


            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            time_stamp = int(time.time()*100)
            recognizer.recognize_async(mp_image, time_stamp)
            if open_init[0]:
                time.sleep(1/25)
            else:
                time.sleep(1/5)

    cap.release()
    cv2.destroyAllWindows()

track()

if False:

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_eye.xml')
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_smile.xml')

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]

            smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20, minSize=(25, 25))

            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(frame, (x + sx, y + sy), (x + sx + sw, y + sy + sh), (0, 255, 0), 2)

        cv2.imshow('Smile Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break