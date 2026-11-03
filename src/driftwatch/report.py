import html, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def write_chart(res, path):
    fr = res["frames"]; t = [r["time_s"] for r in fr]
    fig, ax = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
    ax[0].plot(t, [r["sim_first"] for r in fr], label="sim to first")
    ax[0].plot(t, [r["sim_prev"] for r in fr], label="sim to previous")
    fs = [(r["time_s"], r["face_sim_first"]) for r in fr if r.get("face_sim_first") is not None]
    if fs:
        ax[0].plot(*zip(*fs), "o-", ms=3, label="face sim to first")
    ax[0].set_ylabel("cosine sim"); ax[0].legend(fontsize=8); ax[0].set_title(
        f"DriftWatch — DriftScore {res['aggregate']['drift_score']}  ({Path(res['video']).name})")
    ax[1].plot(t, [r["brightness_delta"] for r in fr], label="brightness Δ (L*)")
    ax[1].plot(t, [r["hist_dist"] * 10 for r in fr], label="hist dist ×10")
    if "flow_jerk" in fr[0]:
        ax[1].plot(t, [r["flow_jerk"] for r in fr], label="flow jerk (px)")
    ax[1].legend(fontsize=8)
    ax[2].plot(t, [r["frame_drift"] for r in fr], color="k", label="frame drift d_t")
    ax[2].axhline(res["aggregate"]["spike_threshold"], ls="--", color="r", lw=1, label="spike threshold")
    for r in fr:
        if r["spike"]:
            for a in ax:
                a.axvspan(r["time_s"] - 0.25 / res["sample_fps"], r["time_s"] + 0.25 / res["sample_fps"], color="r", alpha=0.2)
    ax[2].set_ylim(0, 1); ax[2].set_xlabel("time (s)"); ax[2].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


def write_report(res, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    (out / "drift.json").write_text(json.dumps(res, indent=2))
    write_chart(res, out / "drift_chart.png")
    a = res["aggregate"]
    spikes = ", ".join(f"{r['time_s']}s" for r in res["frames"] if r["spike"]) or "none"
    rows = "".join(f"<tr><td>{html.escape(k)}</td><td>{html.escape(str(v))}</td></tr>" for k, v in a.items())
    (out / "report.html").write_text(f"""<!doctype html><meta charset=utf-8><title>DriftWatch report</title>
<style>body{{font-family:sans-serif;max-width:960px;margin:2em auto}}td{{border-bottom:1px solid #ddd;padding:4px}}</style>
<h1>DriftWatch report</h1><p>Video: <code>{html.escape(res['video'])}</code> · {res['n_frames']} frames @ {res['sample_fps']} fps ·
model: {html.escape(res['embedding_model'])} · faces in {res['faces_detected_frames']} frames</p>
<h2>DriftScore: {a['drift_score']} / 100</h2><p>Spikes at: {spikes}</p>
<img src="drift_chart.png" style="width:100%"><table>{rows}</table>
<p><em>DriftScore is a heuristic and has not been validated against human ratings.</em></p>""")
    return out
