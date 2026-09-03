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
import win32api
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

def mouse_control(ges, thumb, index, middle, ring, pinky, world, landmarks, palm,full_ges, last_pointer2, mouse_avg2, lock2):
    global mouse_Down
    global last_pointer
    last_pointer = last_pointer2
    global mouse_avg
    global lock
    lock = lock2
    mouse_avg = mouse_avg2


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


        mouse_avg = mouse_calc([x, y], (x_diff+y_diff)/2, full_ges, mouse_avg2)

    index_mid = world[6]
    thumb_world = world[4]
    thumb_to_index = distance_2d(thumb_world.x, thumb_world.y, index_mid.x, index_mid.y,)
    #print(thumb_to_index)
    scaled_d = size_scale(world)
    print(thumb_to_index)
    if thumb_to_index <= .008*scaled_d  and mouse_Down >= 5 and palm and win32api.GetKeyState(0x01)>=0:
        mouse_Down = 0
        pyautogui.mouseDown(button="left")

    elif thumb_to_index > .012*scaled_d and palm and win32api.GetKeyState(0x01)<0:
        mouse_Down = 0
        pyautogui.mouseUp(button="left")

    last_pointer = [index.x, index.y]

    mouse_Down += 1
    return last_pointer, mouse_avg, lock

def distance_2d(x,y,a,b):
    xx = (x-a)*(x-a)
    yy = (y-b)*(y-b)
    distance = math.sqrt(xx+yy)
    return distance

def size_scale(world):
    pinky_point = world[17]
    wrist_point = world[0]
    d = distance_3d(pinky_point.x, pinky_point.y, pinky_point.z, wrist_point.x, wrist_point.y, wrist_point.z)
    return .09/d

def mouse_calc(new_pos, buffer, full_ges, mouse_avg2):
    global mouse_avg
    mouse_avg = mouse_avg2
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

        c = threading.Thread(target=thread_lock,
                             args=(x, y, d))

        c.start()
    return mouse_avg

def move_mouse(x, y, d):
    pyautogui.move(int(x), int(y), duration=d, tween=pyautogui.easeOutQuad, _pause=False)

def distance_3d(x,y,z,a,b,c):

    xx = (x-a)*(x-a)
    yy = (y-b)*(y-b)
    zz = (z-c)*(z-c)
    distance = math.sqrt(xx+yy+zz)
    return distance

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
    return[mouse_hand, util_hand]

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


def password(ges, thumb, index, middle, ring, pinky, init_code2):
    global init_code
    init_code = init_code2

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
    return open_init, init_code

def thread_lock(*args):
    with lock:
        move_mouse(*args)