"""Per-frame drift metrics. All are heuristics; none are validated against human ratings yet."""
import cv2
import numpy as np


def color_flicker(frames):
    """Mean LAB delta (L and chroma) + histogram distance vs previous frame."""
    out, prev_lab, prev_hist = [], None, None
    for f in frames:
        lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(np.float32)
        mean = lab.reshape(-1, 3).mean(0)
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
        cv2.normalize(hist, hist)
        if prev_lab is None:
            out.append({"brightness_delta": 0.0, "color_delta": 0.0, "hist_dist": 0.0})
        else:
            d = mean - prev_lab
            out.append({
                "brightness_delta": float(abs(d[0]) / 255 * 100),  # ~L* units
                "color_delta": float(np.hypot(d[1], d[2])),
                "hist_dist": float(cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)),
            })
        prev_lab, prev_hist = mean, hist
    return out


def flow_smoothness(frames):
    """Farneback optical flow magnitude and its change (jerk) between steps."""
    out, prev_g, prev_mag = [], None, None
    for f in frames:
        g = cv2.cvtColor(cv2.resize(f, (256, int(256 * f.shape[0] / f.shape[1]))), cv2.COLOR_BGR2GRAY)
        if prev_g is None:
            out.append({"flow_mag": 0.0, "flow_jerk": 0.0})
        else:
            flow = cv2.calcOpticalFlowFarneback(prev_g, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag = float(np.linalg.norm(flow, axis=2).mean())
            jerk = 0.0 if prev_mag is None else abs(mag - prev_mag)
            out.append({"flow_mag": mag, "flow_jerk": float(jerk)})
            prev_mag = mag
        prev_g = g
    return out


def histogram_embedder():
    """Fallback 'embedding' when torch/open_clip is unavailable (much weaker)."""
    def embed(imgs):
        vs = []
        for f in imgs:
            small = cv2.resize(f, (32, 32)).astype(np.float32).ravel()
            vs.append(small - small.mean())
        v = np.stack(vs)
        return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-8)
    return embed, "pixel-32x32-fallback"


def clip_embedder(model_name="ViT-B-32", pretrained="laion2b_s34b_b79k"):
    import torch, open_clip
    from PIL import Image
    model, _, preprocess = open_clip.create_model_and_transforms(model_name, pretrained=pretrained)
    model.eval()

    def embed(imgs):
        with torch.no_grad():
            batch = torch.stack([preprocess(Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))) for f in imgs])
            e = model.encode_image(batch)
            e = e / e.norm(dim=-1, keepdim=True)
        return e.cpu().numpy()
    return embed, f"open_clip:{model_name}/{pretrained}"


def get_embedder(backend="auto"):
    if backend in ("auto", "clip"):
        try:
            return clip_embedder()
        except Exception as ex:
            if backend == "clip":
                raise
            print(f"[driftwatch] CLIP unavailable ({ex.__class__.__name__}); using pixel fallback")
    return histogram_embedder()


def semantic_drift(embs):
    first = embs @ embs[0]
    prev = np.concatenate([[1.0], np.sum(embs[1:] * embs[:-1], axis=1)])
    return [{"sim_first": float(a), "sim_prev": float(b)} for a, b in zip(first, prev)]


_detector = None
YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"


def _load_detector():
    """YuNet (OpenCV FaceDetectorYN, ~230 KB ONNX, downloaded once to ~/.cache/driftwatch).
    Falls back to Haar cascade on older OpenCV; returns False if nothing is available."""
    import os, urllib.request
    if hasattr(cv2, "FaceDetectorYN"):
        path = os.path.expanduser("~/.cache/driftwatch/yunet.onnx")
        try:
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                urllib.request.urlretrieve(YUNET_URL, path)
            return ("yunet", cv2.FaceDetectorYN.create(path, "", (320, 320), 0.8))
        except Exception as ex:
            print(f"[driftwatch] face detector unavailable ({ex}); skipping faces")
    if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data"):
        c = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if not c.empty():
            return ("haar", c)
    return False


def detect_face(f):
    global _detector
    if _detector is None:
        _detector = _load_detector()
    if not _detector:
        return None
    kind, det = _detector
    if kind == "yunet":
        det.setInputSize((f.shape[1], f.shape[0]))
        _, faces = det.detect(f)
        if faces is None or len(faces) == 0:
            return None
        x, y, w, h = [int(v) for v in max(faces, key=lambda r: r[2] * r[3])[:4]]
    else:
        faces = det.detectMultiScale(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(40, 40))
        if len(faces) == 0:
            return None
        x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
    if w < 24 or h < 24:
        return None
    p = int(0.15 * w)
    return f[max(0, y - p):y + h + p, max(0, x - p):x + w + p]


def face_drift(frames, embed):
    """Largest-face crop embedded with the same image model; cosine sim to first detected face.
    This is an identity *proxy*, not a face-recognition model."""
    crops = [detect_face(f) for f in frames]
    idx = [i for i, c in enumerate(crops) if c is not None and c.size]
    out = [{"face_found": False, "face_sim_first": None} for _ in frames]
    if len(idx) < 2:
        return out, len(idx)
    e = embed([crops[i] for i in idx])
    for k, i in enumerate(idx):
        out[i] = {"face_found": True, "face_sim_first": float(e[k] @ e[0])}
    return out, len(idx)
