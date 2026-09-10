import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components.containers.landmark import Landmark
import calc
import pyautogui
import audio_synth
import asyncio
import threading

#thumb_tip = hand.hand_landmarks[0][4]
#index_tip = hand.hand_landmarks[0][8]
#middle_tip = hand.hand_landmarks[0][12]
#ring_tip = hand.hand_landmarks[0][16]
#pinky_tip = hand.hand_landmarks[0][20]



def toolkit_active(world: list[Landmark]):
    pinky_tip = world[20]
    ring_tip = world[16]
    ring_bottom = world[13]
    pinky_bottom = world[17]
    tip_avg = (pinky_tip.y + ring_tip.y)/2
    bottom_avg = (pinky_bottom.y + ring_bottom.y)/2

    if tip_avg > bottom_avg:
        return True
    else:
        return False

def pick_tool(world: list[Landmark]):
    thumb = world[4]
    index = world[8]
    middle = world[12]
    ring = world[16]
    thumb_to_index = calc.distance_3d(thumb.x, thumb.y, thumb.z, index.x, index.y, index.z)
    thumb_to_middle = calc.distance_3d(thumb.x, thumb.y, thumb.z, middle.x, middle.y, middle.z)
    thumb_to_ring = calc.distance_3d(thumb.x, thumb.y, thumb.z, ring.x, ring.y, ring.z)

    d = [thumb_to_index, "index"]
    if d[0] > thumb_to_middle:
        d = [thumb_to_middle, "middle"]
    if d[0] > thumb_to_ring:
        d = [thumb_to_ring, "ring"]

    if d[0] < .035:
        return d[1]
    else:
        return None

def right_click(mode):
    if mode == "down":
        pyautogui.mouseDown(button="right")
    else:
        pyautogui.mouseUp(button="right")