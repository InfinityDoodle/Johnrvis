import math
import time
from shapely.geometry import Point, Polygon
import shapely
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerResult
import pyautogui
import AIMAKETESTCODE
import matplotlib.pyplot as plt

def calc_iris_pupil_angle(iris_x, iris_y, pupil_x, pupil_y, x_multiplier, y_multiplier):
    #X will be oppisite and y will be adjecent
    x = iris_x - pupil_x
    x*=x_multiplier
    y = iris_y - pupil_y
    y*=y_multiplier
    return math.degrees(math.atan2(y,x))


def line_from_angle(startx, starty, angle, nx=1, ny=1):
    start = Point(startx, starty)
    length = 10000
    angle = math.radians(angle)

    end = Point(start.x + nx * (length * math.cos(angle)),
                start.y + ny * (length * math.sin(angle)))
    l = shapely.LineString([start, end])

    return l

def calc_eye_tracking(face_all: FaceLandmarkerResult, image):
    # LEFT EYE INDICES
    # 33: Outer corner
    # 133: Inner corner
    # 159: Upper eyelid top
    # 145: Lower eyelid bottom
    # 468: Iris center
    #
    # RIGHT EYE INDICES
    # 263: Outer corner
    # 362: Inner corner
    # 386: Upper eyelid top
    # 374: Lower eyelid bottom
    # 473: Iris center

    face = face_all.face_landmarks[0]

    outer_right = calc_iris_pupil_angle(face[263].x, face[263].y, face[473].x, face[473].y, image.width, image.height)
    inner_right = calc_iris_pupil_angle(face[362].x, face[362].y, face[473].x, face[473].y, image.width, image.height)
    upper_right = calc_iris_pupil_angle(face[386].x, face[386].y, face[473].x, face[473].y, image.width, image.height)
    lower_right = calc_iris_pupil_angle(face[374].x, face[374].y, face[473].x, face[473].y, image.width, image.height)

    outer_left = calc_iris_pupil_angle(face[33].x, face[33].y, face[468].x, face[468].y, image.width, image.height)
    inner_left = calc_iris_pupil_angle(face[133].x, face[133].y, face[468].x, face[468].y, image.width, image.height)
    upper_left = calc_iris_pupil_angle(face[159].x, face[159].y, face[468].x, face[468].y, image.width, image.height)
    lower_left = calc_iris_pupil_angle(face[145].x, face[145].y, face[468].x, face[468].y, image.width, image.height)

    x = pyautogui.size().width
    y = pyautogui.size().height

    right_outer_cords = [[x, y/2]]
    right_inner_cords = [[0, y/2]]
    right_upper_cords = [[x/2, y]]
    right_lower_cords = [[x/2, 0]]

    left_outer_cords = [[0, y/2]]
    left_inner_cords = [[x, y/2]]
    left_upper_cords = [[x/2, y]]
    left_lower_cords = [[x/2, 0]]

    print(f"{outer_right}, {inner_right}, {upper_right}, {lower_right}")

    l1 = line_from_angle(right_outer_cords[0][0], right_outer_cords[0][1], -outer_right, -1, 1)

    l2 = line_from_angle(right_inner_cords[0][0], right_inner_cords[0][1], -inner_right, -1, 1)

    l3 = line_from_angle(right_upper_cords[0][0], right_upper_cords[0][1], -upper_right, 1, -1)

    l4 = line_from_angle(right_lower_cords[0][0], right_lower_cords[0][1], lower_right)


    l5 = line_from_angle(left_outer_cords[0][0], left_outer_cords[0][1], -outer_left, -1, 1)

    l6 = line_from_angle(left_inner_cords[0][0], left_inner_cords[0][1], -inner_left, -1, 1)

    l7 = line_from_angle(left_upper_cords[0][0], left_upper_cords[0][1], -upper_left, 1, -1)

    l8 = line_from_angle(left_lower_cords[0][0], left_lower_cords[0][1], lower_left, 1, 1)

    intersection_1 = shapely.intersection(l1, l4)
    intersection_2 = shapely.intersection(l2, l3)

    intersection_3 = shapely.intersection(l5, l6)
    intersection_4 = shapely.intersection(l6, l8)

    inter_x, inter_y = intersection_1.xy[0], intersection_1.xy[1]
    inter_x_2, inter_y_2 = intersection_2.xy[0], intersection_2.xy[1]

    intersections = []

    for line in [l1, l2, l3, l4, l5, l6, l7, l8]:
        for line2 in [l1, l2, l3, l4, l5, l6, l7, l8]:
            if line != line2:
                intersection = shapely.intersection(line2, line)
                if intersection not in intersections:
                    intersections.append(intersection)

    avg_x = 0
    avg_y = 0
    count = 0
    print((intersections[0].xy[0][0]))
    for intersection in intersections:
        savex = avg_x
        savey = avg_y
        savecount = count
        try:
            avg_x += float(intersection.xy[0][0])
            avg_y += float(intersection.xy[1][0])
            count += 1
        except:
            avg_x = avg_x
            avg_y = avg_y
            count = savecount

    avg_intersection = [avg_x/count, avg_y/count]


    AIMAKETESTCODE.update_eye_debug_plot(
        right_outer_line=l1,
        right_inner_line=l2,
        right_upper_line=l3,
        right_lower_line=l4,
        right_intersection_1=intersection_1,
        right_intersection_2=intersection_2,
        left_outer_line=l5,
        left_inner_line=l6,
        left_upper_line=l7,
        left_lower_line=l8,
        left_intersection_1=intersection_3,
        left_intersection_2=intersection_4,
        screen_width=x,
        screen_height=y,
        avg_intersection=avg_intersection,
    )

    return (f"The lines intersect at: ({inter_x}, {inter_y}) and the others at ({inter_x_2}, {inter_y_2})")