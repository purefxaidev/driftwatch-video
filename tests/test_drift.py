import json
from driftwatch.synth import make_video
from driftwatch.analyze import analyze
from driftwatch.cli import main


def test_stable_vs_abrupt(tmp_path):
    s = analyze(make_video(tmp_path / "s.mp4", "stable"), fps=5, backend="pixel")
    a = analyze(make_video(tmp_path / "a.mp4", "abrupt"), fps=5, backend="pixel")
    assert a["aggregate"]["drift_score"] > s["aggregate"]["drift_score"] + 10
    assert a["aggregate"]["n_spikes"] >= 2
    assert s["aggregate"]["n_spikes"] == 0


def test_cli_outputs(tmp_path):
    v = make_video(tmp_path / "a.mp4", "abrupt")
    main(["analyze", str(v), "--out", str(tmp_path / "r"), "--backend", "pixel", "--fps", "5"])
    d = json.loads((tmp_path / "r" / "drift.json").read_text())
    assert len(d["frames"]) == d["n_frames"] and "drift_score" in d["aggregate"]
    assert (tmp_path / "r" / "drift_chart.png").stat().st_size > 1000
    assert (tmp_path / "r" / "report.html").exists()
