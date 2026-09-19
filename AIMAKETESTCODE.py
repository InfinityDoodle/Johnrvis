import math
import time
from shapely.geometry import Point, Polygon
import shapely
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerResult
import pyautogui
import matplotlib.pyplot as plt


def update_eye_debug_plot(
    right_outer_line,
    right_inner_line,
    right_upper_line,
    right_lower_line,
    left_outer_line,
    left_inner_line,
    left_upper_line,
    left_lower_line,
    right_intersection_1,
    right_intersection_2,
    left_intersection_1,
    left_intersection_2,
    avg_intersection,
    screen_width,
    screen_height,
):
    """Update a live debugging plot for both eyes."""

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
        axes.plot(
            x_values,
            y_values,
            color=color,
            linewidth=2,
            label=label,
        )

    def draw_intersection(geometry, color, label, marker):
        if geometry is None or geometry.is_empty:
            return

        if isinstance(geometry, Point):
            axes.scatter(
                geometry.x,
                geometry.y,
                color=color,
                s=80,
                marker=marker,
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
                        marker=marker,
                        linewidths=3,
                        label=label if number == 0 else None,
                        zorder=10,
                    )

    # Right eye: bright colors.
    draw_line(right_outer_line, "red", "Right outer")
    draw_line(right_inner_line, "dodgerblue", "Right inner")
    draw_line(right_upper_line, "limegreen", "Right upper")
    draw_line(right_lower_line, "orange", "Right lower")

    # Left eye: dark colors.
    draw_line(left_outer_line, "darkred", "Left outer")
    draw_line(left_inner_line, "navy", "Left inner")
    draw_line(left_upper_line, "darkgreen", "Left upper")
    draw_line(left_lower_line, "saddlebrown", "Left lower")

    # Right-eye intersections use an X.
    draw_intersection(
        right_intersection_1,
        "magenta",
        "Right outer/lower intersection",
        "x",
    )
    draw_intersection(
        right_intersection_2,
        "cyan",
        "Right inner/upper intersection",
        "x",
    )

    # Left-eye intersections use a plus sign.
    draw_intersection(
        left_intersection_1,
        "darkmagenta",
        "Left outer/lower intersection",
        "+",
    )
    draw_intersection(
        left_intersection_2,
        "darkcyan",
        "Left inner/upper intersection",
        "+",
    )

    # Average of the intersections: a large gold star.
    if avg_intersection is not None:
        axes.scatter(
            avg_intersection[0],
            avg_intersection[1],
            color="gold",
            edgecolors="black",
            s=250,
            marker="*",
            linewidths=1.5,
            label="Average intersection",
            zorder=20,
        )

    axes.set_xlim(0, screen_width)
    axes.set_ylim(screen_height, 0)
    axes.set_aspect("equal", adjustable="box")
    axes.set_title("Both-eyes tracking geometry")
    axes.set_xlabel("Screen X")
    axes.set_ylabel("Screen Y")
    axes.grid(True, alpha=0.3)
    axes.legend(loc="upper right", fontsize="small", ncol=2)

    update_eye_debug_plot.figure.canvas.draw_idle()
    update_eye_debug_plot.figure.canvas.flush_events()