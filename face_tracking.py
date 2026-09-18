import math
import time
from shapely.geometry import Point, Polygon
import shapely
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerResult
import pyautogui
import matplotlib.pyplot as plt
def calc_iris_pupil_angle(iris_x, iris_y, pupil_x, pupil_y, x_multiplier, y_multiplier):
    #X will be oppisite and y will be adjecent
    x = iris_x - pupil_x
    x*=x_multiplier
    y = iris_y - pupil_y
    y*=y_multiplier
    return math.degrees(math.atan2(x,y))


def update_eye_debug_plot(
    outer_line,
    inner_line,
    upper_line,
    lower_line,
    intersection_1,
    intersection_2,
    screen_width,
    screen_height,
):
    """Update a live debugging plot of the eye-tracking geometry."""

    # Create the plot only on the first call.
    if not hasattr(update_eye_debug_plot, "figure"):
        plt.ion()

        update_eye_debug_plot.figure, update_eye_debug_plot.axes = plt.subplots(
            figsize=(10, 6)
        )

    axes = update_eye_debug_plot.axes
    axes.clear()

    def draw_line(line, color, label):
        if line is None or line.is_empty:
            return

        x_values, y_values = line.xy
        axes.plot(x_values, y_values, color=color, linewidth=2, label=label)

    def draw_intersection(geometry, color, label):
        if geometry is None or geometry.is_empty:
            return

        if isinstance(geometry, Point):
            axes.scatter(
                geometry.x,
                geometry.y,
                color=color,
                s=80,
                marker="x",
                linewidths=3,
                label=label,
                zorder=10,
            )
        elif hasattr(geometry, "geoms"):
            for number, point in enumerate(geometry.geoms):
                if isinstance(point, Point):
                    axes.scatter(
                        point.x,
                        point.y,
                        color=color,
                        s=80,
                        marker="x",
                        linewidths=3,
                        label=label if number == 0 else None,
                        zorder=10,
                    )

    draw_line(outer_line, "red", "Outer corner line")
    draw_line(inner_line, "blue", "Inner corner line")
    draw_line(upper_line, "green", "Upper eyelid line")
    draw_line(lower_line, "orange", "Lower eyelid line")

    draw_intersection(intersection_1, "purple", "Outer/lower intersection")
    draw_intersection(intersection_2, "black", "Inner/upper intersection")

    axes.set_xlim(0, screen_width)
    axes.set_ylim(screen_height, 0)  # Match screen coordinates: (0, 0) at top-left.
    axes.set_aspect("equal", adjustable="box")
    axes.set_title("Eye-tracking geometry debug view")
    axes.set_xlabel("Screen X")
    axes.set_ylabel("Screen Y")
    axes.grid(True, alpha=0.3)
    axes.legend(loc="upper right")

    update_eye_debug_plot.figure.canvas.draw_idle()
    update_eye_debug_plot.figure.canvas.flush_events()
    plt.pause(0.001)

def line_from_angle(startx, starty, angle):
    start = Point(startx, starty)
    length = 10000
    angle = math.radians(angle)

    end = Point(start.x + length * math.cos(angle),
                start.y + length * math.sin(angle))
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

    outer_left = calc_iris_pupil_angle(face[33].x, face[33].y, face[473].x, face[473].y, image.width, image.height)
    inner_left = calc_iris_pupil_angle(face[133].x, face[133].y, face[473].x, face[473].y, image.width, image.height)
    upper_left = calc_iris_pupil_angle(face[159].x, face[159].y, face[473].x, face[473].y, image.width, image.height)
    lower_left = calc_iris_pupil_angle(face[145].x, face[145].y, face[473].x, face[473].y, image.width, image.height)

    x = pyautogui.size().width
    y = pyautogui.size().height

    right_outer_cords = [[x, y/2]]
    right_inner_cords = [[0, y/2]]
    right_upper_cords = [[x/2, y]]
    right_lower_cords = [[x/2, 0]]

    print(f"{outer_right}, {inner_right}, {upper_right}, {lower_right}")

    l1 = line_from_angle(right_outer_cords[0][0], right_outer_cords[0][1], -outer_right)

    l2 = line_from_angle(right_inner_cords[0][0], right_inner_cords[0][1], -inner_right)

    l3 = line_from_angle(right_upper_cords[0][0], right_upper_cords[0][1], -upper_right)

    l4 = line_from_angle(right_lower_cords[0][0], right_lower_cords[0][1], -lower_right)

    intersection = shapely.intersection(l1, l4)
    intersection_2 = shapely.intersection(l2, l3)

    inter_x, inter_y = intersection.xy[0], intersection.xy[1]
    inter_x_2, inter_y_2 = intersection_2.xy[0], intersection_2.xy[1]

    update_eye_debug_plot(
        outer_line=l1,
        inner_line=l2,
        upper_line=l3,
        lower_line=l4,
        intersection_1=intersection,
        intersection_2=intersection_2,
        screen_width=x,
        screen_height=y,
    )

    return (f"The lines intersect at: ({inter_x}, {inter_y}) and the others at ({inter_x_2}, {inter_y_2})")