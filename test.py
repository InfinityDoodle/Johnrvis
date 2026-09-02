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
pyautogui.FAILSAFE = False
pyautogui.PAUSE = .01

global open_init
global t
t = time.time()
open_init = [False, t]
global init_code
init_code = [0, 0, 0]
global last_pointer
last_pointer = [0, 0]
global mouse_Down
mouse_Down = 0
global mouse_hand
mouse_hand = 0
global util_hand
util_hand = None
global mouse_avg
mouse_avg = []
global lock
lock = threading.Lock()

#thumb_tip = hand.hand_landmarks[0][4]
#index_tip = hand.hand_landmarks[0][8]
#middle_tip = hand.hand_landmarks[0][12]
#ring_tip = hand.hand_landmarks[0][16]
#pinky_tip = hand.hand_landmarks[0][20]

def mouse_control(ges, thumb, index, middle, ring, pinky, world, landmarks, palm,full_ges):
    global mouse_Down
    global last_pointer
    width, height = pyautogui.size()
    index_to_middle = distance_3d(world[8].x, world[8].y, world[8].z, world[12].x, world[12].y, world[12].z)
    index_to_middle_1 = distance_3d(world[5].x,world[5].y,world[5].z,world[9].x,world[9].y,world[9].z)
    index_to_middle_2 = distance_3d(world[6].x, world[6].y, world[6].z, world[10].x, world[10].y, world[10].z)
    index_to_middle_3 = distance_3d(world[7].x, world[7].y, world[7].z, world[7].x, world[11].y,world[11].z)
    avg = (index_to_middle_1+(2*index_to_middle_2)+(3*index_to_middle_3)+(6*index_to_middle)) / 12
    #print(avg)
    if avg <= .025 and ges != "Victory" and ges != "Closed_Fist" and palm:
        x_diff = abs(last_pointer[0] - index.x)
        y_diff = abs(last_pointer[1] - index.y)
        x = ((last_pointer[0]- index.x) * width)
        y = ((index.y-last_pointer[1]) * height)
        if not (x_diff+y_diff)/2 <= .003:
            buffer = True
        else:
            buffer = False

        c = threading.Thread(target=thread_lock,
                             args=([x, y], (x_diff+y_diff)/2, full_ges))

        c.start()

    index_mid = world[6]
    thumb_world = world[4]
    thumb_to_index = distance_3d(thumb_world.x, thumb_world.y, thumb_world.z, index_mid.x, index_mid.y, index_mid.z)
    #print(thumb_to_index)
    if thumb_to_index <= .03  and mouse_Down >= 20 and palm:
        mouse_Down = 0
        pyautogui.click(button="left")

    last_pointer = [index.x, index.y]

    mouse_Down += 1

def distance_2d(x,y,a,b):
    xx = (x-a)*(x-a)
    yy = (y-b)*(y-b)
    distance = math.sqrt(xx+yy)
    return distance

def mouse_calc(new_pos, buffer, full_ges):
    global mouse_avg
    hand_choice(full_ges)
    x = new_pos[0]
    y = new_pos[1]
    d = .025
    mag_avg = .003*.003
    #print(f"{x}, {y}")

    if len(mouse_avg) >= 5:
        mouse_avg.pop(0)
        mouse_avg.append([x,y])
    else:
        mouse_avg.append([x, y])

    if len(mouse_avg) >= 5:

        mag_1 = distance_2d(mouse_avg[0][0], mouse_avg[0][1], mouse_avg[1][0], mouse_avg[1][1])
        mag_2 = distance_2d(mouse_avg[1][0], mouse_avg[1][1], mouse_avg[2][0], mouse_avg[2][1])
        mag_3 = distance_2d(mouse_avg[3][0], mouse_avg[3][1], mouse_avg[2][0], mouse_avg[2][1])
        mag_4 = distance_2d(mouse_avg[4][0], mouse_avg[4][1], mouse_avg[3][0], mouse_avg[3][1])
        mag_avg = (mag_1+mag_2+mag_4+mag_3)/4

        #print(1/(mag_avg/2))
        d= 1/(mag_avg*3)

    #print(mag_avg)
    speed = 3
    #print(d)
    if d > .075:
        d = .075
    if buffer >= .00065:
        v = math.sqrt(abs(mag_avg))/speed
        if v < .5:
            v = .5
        if v > 5:
            v = 5
        x = v * x
        y = v * y
        pyautogui.move(int(x), int(y), duration=d, tween=pyautogui.easeOutQuad, _pause=False)

def distance_3d(x,y,z,a,b,c):

    xx = (x-a)*(x-a)
    yy = (y-b)*(y-b)
    zz = (z-c)*(z-c)
    distance = math.sqrt(xx+yy+zz)
    return distance

def calc(ges, thumb, index, middle, ring, pinky, world, landmarks, handedness, full_ges):
    password(ges, thumb, index, middle, ring, pinky)
    hand_choice(full_ges)
    if open_init[0]:
        palm = detect_palm(handedness, world)
        mouse_control(ges, thumb, index, middle, ring, pinky, world, landmarks, palm, full_ges)


def hand_choice(full_ges):
    global mouse_hand
    global util_hand
    #print(full_ges)
    if len(full_ges.handedness) == 1:
        mouse_hand = 0
        util_hand = None
    elif len(full_ges.handedness) == 2:
        if full_ges.handedness[0][0].category_name == "Right":
            mouse_hand = 0
            util_hand = 1
        else:
            mouse_hand = 1
            util_hand = 0

    #s.gestures[mouse_hand]) + " " + str(util_hand))

def detect_palm(handedness, world):
    global mouse_hand
    hand = 0
    if handedness[mouse_hand][0].category_name == "Right":
        hand = 0
    else:
        hand = 1
    #wrist is really base pinky
    wrist = world[17]
    thumb_base = world[1]
    thumb_x = thumb_base.x
    thumb_y = thumb_base.y
    thumb_z = thumb_base.z
    wrist_x = wrist.x
    wrist_y = wrist.y
    wrist_z = wrist.z

    checks = 0
    z = .028
    if hand == 0:
        if wrist_x < thumb_x:
            checks += 1
        if wrist_y < thumb_y:
            checks += 1
        if thumb_z - z < wrist_z < thumb_z + z:
            checks += 1
    else:
        if wrist_x > thumb_x:
            checks += 1
        if wrist_y < thumb_y:
            checks += 1
        if thumb_z - z < wrist_z < thumb_z + z:
            checks += 1

    if checks == 3:
        return True
    else:
        return False


def password(ges, thumb, index, middle, ring, pinky):
    global init_code

    unlock_num = 3
    max_num = 7

    if init_code[0] <= unlock_num * 2 and str(ges) == "Closed_Fist":
        init_code[0] += 2
    elif init_code[0] >= unlock_num and str(ges) == "Victory" and init_code[1] <= unlock_num * 2:
        init_code[1] += 2
        init_code[0] += 1
    elif init_code[1] >= unlock_num and str(ges) == "Closed_Fist":
        init_code[2] += 1
        init_code[1] += 1
        init_code[0] += 1
    else:
        if init_code[0] > 0:
            init_code[0] -= .5
        if init_code[1] > 0:
            init_code[1] -= .5
        if init_code[2] > 0:
            init_code[2] -= .5

    if init_code[2] >= max_num:
        init_code[2] = max_num
    if init_code[1] >= max_num:
        init_code[1] = max_num
    if init_code[0] >= max_num:
        init_code[0] = max_num

    if init_code[2] >= max_num and (time.time()-open_init[1] >= 5):
        open_init[1] = time.time()
        if open_init[0]:
            open_init[0] = False
        else:
            open_init[0] = True

def call(ges, mp_image: mp.Image, timestamp_ms: int):
    global mouse_hand
    global util_hand
    #print(f"{mouse_hand}:{util_hand}")
    global t

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

def thread_lock(*args):
    with lock:
        mouse_calc(*args)

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