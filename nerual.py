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

from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerResult

import calc
import win32api
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
global lock
lock = threading.Lock()
global draw_face_landmarks
draw_face_landmarks = []

global mouse_avg
mouse_avg = []
global last_pointer
last_pointer = [0, 0]

#thumb_tip = hand.hand_landmarks[0][4]
#index_tip = hand.hand_landmarks[0][8]
#middle_tip = hand.hand_landmarks[0][12]
#ring_tip = hand.hand_landmarks[0][16]
#pinky_tip = hand.hand_landmarks[0][20]


def calcy(ges, thumb, index, middle, ring, pinky, world, landmarks, handedness, full_ges):
    global t
    global open_init
    global init_code
    global mouse_hand
    global util_hand
    global last_pointer
    global mouse_avg
    global lock
    open_init, init_code = calc.password(ges, thumb, index, middle, ring, pinky, init_code)
    mouse_hand, util_hand = calc.hand_choice(full_ges)
    if open_init[0]:
        palm = calc.detect_palm(handedness, world)
        last_pointer, mouse_avg, lock = calc.mouse_control(ges, thumb, index, middle, ring, pinky, world, landmarks, palm, full_ges, last_pointer, mouse_avg, lock)

def call(ges, mp_image: mp.Image, timestamp_ms: int):
    global t
    global open_init
    global init_code
    global mouse_hand
    global util_hand
    global lock

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
        calcy(ges.gestures[mouse_hand][0].category_name, thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip,
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

        try:
            eye_landmarks = []
            for x in draw_face_landmarks[0][468:477]:
                eye_landmarks.append(x)
            mp.tasks.vision.drawing_utils.draw_landmarks(frame, eye_landmarks)
        except Exception as e:
            pass

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

def call_face(face: FaceLandmarkerResult, mp_image: mp.Image, timestamp_ms: int):
    #print(face)
    global draw_face_landmarks

    # LEFT IRIS (Indices 468 - 472)
    # 468: Left Eye Pupil / Iris Center
    # 469: Left Iris Inner / Right Boundary (towards the nose)
    # 470: Left Iris Upper / Top Boundary
    # 471: Left Iris Outer / Left Boundary (towards the temple)
    # 472: Left Iris Lower / Bottom Boundary

    # RIGHT IRIS (Indices 473 - 477)
    # 473: Right Eye Pupil / Iris Center
    # 474: Right Iris Inner / Left Boundary (towards the nose)
    # 475: Right Iris Upper / Top Boundary
    # 476: Right Iris Outer / Right Boundary (towards the temple)
    # 477: Right Iris Lower / Bottom Boundary

    draw_face_landmarks = face.face_landmarks


def track():
    global open_init
    BaseOptions = mp.tasks.BaseOptions
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    FaceDetectorLandMark = mp.tasks.vision.FaceLandmarker
    FaceLandMarkOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode


    ges_path = r"C:\Users\jgdiv\PyCharmMiscProject\net\weights\gesture_recognizer.task"
    face_path = r"C:\Users\jgdiv\PyCharmMiscProject\net\weights\face_landmarker.task"

    ges_options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=ges_path),
        running_mode=VisionRunningMode.LIVE_STREAM, num_hands=2,
        min_hand_detection_confidence=.6,
        min_hand_presence_confidence=.6,
        min_tracking_confidence=.6, result_callback=call)

    face_options = FaceLandMarkOptions(
        base_options=BaseOptions(model_asset_path=face_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        min_tracking_confidence=.6,
        min_face_detection_confidence=.6,
        min_face_presence_confidence=.6,
        result_callback=call_face,
        num_faces=1)

    cap = cv2.VideoCapture(0)
    time_stamp = 0
    with GestureRecognizer.create_from_options(ges_options) as recognizer:
        with FaceDetectorLandMark.create_from_options(face_options) as detector:
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
                detector.detect_async(mp_image, time_stamp)
                if open_init[0]:
                    time.sleep(1/25)
                else:
                    time.sleep(1/5)

        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
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