import cv2
import numpy as np


def sample_frames(path, fps=2.0, max_frames=300, max_side=512):
    """Return (frames_bgr list, timestamps list, source_fps)."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise IOError(f"cannot open video: {path}")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, int(round(src_fps / fps))) if fps > 0 else 1
    frames, ts, i = [], [], 0
    while len(frames) < max_frames:
        ok, f = cap.read()
        if not ok:
            break
        if i % step == 0:
            h, w = f.shape[:2]
            s = max_side / max(h, w)
            if s < 1:
                f = cv2.resize(f, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
            frames.append(f)
            ts.append(i / src_fps)
        i += 1
    cap.release()
    if not frames:
        raise ValueError("no frames decoded")
    return frames, ts, src_fps
