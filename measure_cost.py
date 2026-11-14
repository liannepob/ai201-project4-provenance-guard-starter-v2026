#!/usr/bin/env python3
"""
Measure what one run costs (capstone).

    python app.py                       # in one terminal
    python measure_cost.py              # in another: 10 runs, 6.5s apart
    python measure_cost.py --runs 10 --pace 0

"One run" is one POST /submit. This service calls no paid API, so API spend is
$0 and the real cost is compute: seconds of wall-clock time per request, with
the first request (which loads the model into memory) reported separately from
the warm ones.

Timings come from two places so they can be cross-checked: the client's own
stopwatch, and `duration_ms` in logs/requests.jsonl, matched by the
X-Request-ID header the server sends back.

The default pace stays under the 10-per-minute rate limit in config.py. Pass
--pace 0 only if you have turned rate limiting off.
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

import requests

import config
import request_log

SAMPLES = ["clearly_human", "clearly_ai", "plain_human", "borderline"]


def load_texts() -> list[str]:
    texts = []
    for name in SAMPLES:
        path = Path(config.ROOT) / "samples" / f"{name}.json"
        texts.append(json.loads(path.read_text(encoding="utf-8"))["text"])
    return texts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--pace", type=float, default=6.5,
                        help="seconds between requests (default stays under 10/min)")
    parser.add_argument("--url", default=f"http://{config.HOST}:{config.PORT}")
    args = parser.parse_args()

    texts = load_texts()
    rows = []
    for i in range(args.runs):
        text = texts[i % len(texts)]
        started = time.perf_counter()
        try:
            resp = requests.post(
                f"{args.url}/submit",
                json={"text": text, "creator_id": "cost_measure"},
                timeout=120,
            )
        except requests.RequestException as exc:
            print(f"run {i + 1}: could not reach the service ({exc}). Is app.py running?")
            return 1
        client_s = time.perf_counter() - started
        rows.append({
            "run": i + 1,
            "status": resp.status_code,
            "client_seconds": round(client_s, 3),
            "request_id": resp.headers.get("X-Request-ID"),
        })
        print(f"run {i + 1:>2}  status {resp.status_code}  {client_s:6.2f}s")
        if args.pace and i < args.runs - 1:
            time.sleep(args.pace)

    # Match each run to the server's own duration_ms.
    server = {e.get("request_id"): e.get("duration_ms") for e in request_log.read_entries()}
    for r in rows:
        ms = server.get(r["request_id"])
        r["server_seconds"] = round(ms / 1000, 3) if ms is not None else None

    ok = [r for r in rows if r["status"] == 200]
    warm = [r["client_seconds"] for r in ok[1:]]
    print()
    print(f"runs: {len(rows)}   succeeded: {len(ok)}")
    if ok:
        print(f"first run (cold, model load): {ok[0]['client_seconds']:.2f}s")
    if warm:
        print(f"warm runs: n={len(warm)}  mean {statistics.mean(warm):.2f}s  "
              f"median {statistics.median(warm):.2f}s  "
              f"min {min(warm):.2f}s  max {max(warm):.2f}s")
    allc = [r["client_seconds"] for r in ok]
    if allc:
        print(f"all successful runs: mean {statistics.mean(allc):.2f}s")
    print("API spend per run: $0.00 (no hosted model; gpt2 runs locally)")

    out = config.RESULTS_DIR / "cost_measurement.json"
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nper-run rows written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
