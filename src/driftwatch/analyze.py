"""Combine metrics into per-frame drift and an aggregate DriftScore (heuristic)."""
import numpy as np
from . import metrics as M
from .frames import sample_frames

# Reference scales: a component equal to its scale contributes "1.0" (fully drifting) before weighting.
SCALES = {"sem": 0.15, "hist": 0.5, "bright": 10.0, "jerk": 2.0, "face": 0.25}
WEIGHTS = {"sem": 0.4, "hist": 0.2, "bright": 0.2, "jerk": 0.1, "face": 0.1}


def _c(x, s):
    return float(min(1.0, max(0.0, x / s)))


def analyze(path, fps=2.0, max_frames=300, backend="auto", faces=True, flow=True):
    frames, ts, src_fps = sample_frames(path, fps=fps, max_frames=max_frames)
    embed, model = M.get_embedder(backend)
    embs = np.concatenate([embed(frames[i:i + 16]) for i in range(0, len(frames), 16)])
    sem = M.semantic_drift(embs)
    col = M.color_flicker(frames)
    fl = M.flow_smoothness(frames) if flow else [{} for _ in frames]
    if faces:
        fc, nfaces = M.face_drift(frames, embed)
    else:
        fc, nfaces = [{} for _ in frames], 0

    per = []
    for i, t in enumerate(ts):
        r = {"index": i, "time_s": round(t, 3), **sem[i], **col[i], **fl[i], **fc[i]}
        comp = {
            "sem": _c(1 - r["sim_prev"], SCALES["sem"]),
            "hist": _c(r["hist_dist"], SCALES["hist"]),
            "bright": _c(r["brightness_delta"], SCALES["bright"]),
        }
        if flow:
            comp["jerk"] = _c(r["flow_jerk"], SCALES["jerk"])
        if r.get("face_sim_first") is not None:
            comp["face"] = _c(1 - r["face_sim_first"], SCALES["face"])
        w = sum(WEIGHTS[k] for k in comp)
        r["frame_drift"] = 0.0 if i == 0 else sum(WEIGHTS[k] * v for k, v in comp.items()) / w
        per.append(r)

    d = np.array([r["frame_drift"] for r in per[1:]] or [0.0])
    med = float(np.median(d)); mad = float(np.median(np.abs(d - med))) + 1e-6
    thr = max(0.25, med + 4 * 1.4826 * mad)
    for r in per:
        r["spike"] = bool(r["index"] > 0 and r["frame_drift"] > thr)
    long_drift = float(1 - np.mean([r["sim_first"] for r in per]))
    mean_d, p95 = float(d.mean()), float(np.percentile(d, 95))
    score = 100 * (0.4 * mean_d + 0.3 * p95 + 0.3 * _c(long_drift, 0.3))
    return {
        "version": "0.1.0",
        "video": str(path),
        "source_fps": src_fps,
        "sample_fps": fps,
        "n_frames": len(per),
        "embedding_model": model,
        "faces_detected_frames": nfaces,
        "aggregate": {
            "drift_score": round(score, 2),
            "mean_frame_drift": round(mean_d, 4),
            "p95_frame_drift": round(p95, 4),
            "long_term_drift": round(long_drift, 4),
            "spike_threshold": round(thr, 4),
            "n_spikes": int(sum(r["spike"] for r in per)),
            "formula": "DriftScore = 100*(0.4*mean(d_t) + 0.3*p95(d_t) + 0.3*clip((1-mean sim_first)/0.3)); "
                       "d_t = weighted mean of clipped components (0.4 semantic 1-sim_prev/0.15, 0.2 hist/0.5, "
                       "0.2 brightness/10, 0.1 flow jerk/2, 0.1 face 1-sim/0.25). HEURISTIC, not validated against human ratings.",
        },
        "frames": per,
    }
