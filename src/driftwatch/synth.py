import cv2
import numpy as np


def make_video(path, kind="stable", seconds=4, fps=10, size=(160, 120)):
    """kind='stable': slowly moving circle; 'abrupt': scene/colour jumps every second."""
    w, h = size
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    rng = np.random.default_rng(0)
    for i in range(seconds * fps):
        if kind == "stable":
            f = np.full((h, w, 3), (90, 140, 60), np.uint8)
            cv2.circle(f, (40 + i, 60), 20, (30, 30, 220), -1)
        else:
            seg = i // fps
            col = tuple(int(c) for c in rng.integers(0, 255, 3)) if i % fps == 0 else col
            f = np.full((h, w, 3), col, np.uint8)
            if seg % 2:
                cv2.rectangle(f, (20, 20), (120, 100), (255, 255, 255), -1)
            else:
                cv2.circle(f, (80, 60), 35, (0, 0, 0), -1)
        vw.write(f)
    vw.release()
    return path
