import argparse
from .analyze import analyze
from .report import write_report


def main(argv=None):
    p = argparse.ArgumentParser(prog="driftwatch", description="Measure temporal drift in videos")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze")
    a.add_argument("video"); a.add_argument("--out", default="report")
    a.add_argument("--fps", type=float, default=2.0); a.add_argument("--max-frames", type=int, default=300)
    a.add_argument("--backend", choices=["auto", "clip", "pixel"], default="auto")
    a.add_argument("--no-faces", action="store_true"); a.add_argument("--no-flow", action="store_true")
    args = p.parse_args(argv)
    res = analyze(args.video, fps=args.fps, max_frames=args.max_frames, backend=args.backend,
                  faces=not args.no_faces, flow=not args.no_flow)
    out = write_report(res, args.out)
    ag = res["aggregate"]
    print(f"DriftScore {ag['drift_score']} | spikes {ag['n_spikes']} | frames {res['n_frames']} | report {out}/report.html")


if __name__ == "__main__":
    main()
