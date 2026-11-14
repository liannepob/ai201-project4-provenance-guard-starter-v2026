#!/usr/bin/env python3
"""
Run the five Capstone criteria, three trials each (capstone).

    python3 run_capstone.py --label before
    python3 run_capstone.py --label after

Stop any copy of app.py you have running first. This script starts the service
itself, once per trial, because criterion 4 is about the first request after a
restart, so every trial needs a real cold start.

Each trial, in this order:
  1. start the service (fresh process, empty rate-limit counters)
  2. send 10 valid POST /submit requests            -> criteria 1, 3, 4
  3. send 3 with missing text, 3 with text > 10,000 -> criterion 2
  4. read the new lines of logs/requests.jsonl      -> criteria 1, 3, 4, 5
  5. stop the service

It reports what happened. It does NOT decide MET or MISSED: the Verdict column
comes back blank because that call is yours, against the targets in criteria.md.

Everything is written to results/capstone_<label>_<timestamp>.md: the table,
and under it the real log lines each trial produced.

Where criteria.md is silent, this script had to pick. Those picks are listed in
ASSUMPTIONS below and printed in the report, so you can see them.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

import config
import request_log

ASSUMPTIONS = [
    "Criterion 1: the 10 requests are 10 valid POST /submit requests (the first is the cold one).",
    "Criterion 2: criteria.md gives no count, so 3 missing-text and 3 over-10,000-character requests are sent; "
    "the cell shows how many of those 6 returned a 4xx or 5xx.",
    "Criterion 3: 'warm' means every POST /submit logged after the first one in the trial "
    "(this includes the 6 rejected requests, which are fast).",
    "Criterion 4: the first POST /submit of the trial, measured by duration_ms in logs/requests.jsonl.",
    "Criterion 5: lines for /ping, /health, 404s and empty-body requests are skipped; "
    "'includes a field' means the key is present, even if its value is empty.",
]

WARM_LIMIT_MS = 100.0      # criterion 3
COLD_LIMIT_MS = 3750.0     # criterion 4
REQUIRED_FIELDS = ["timestamp", "request_id", "method", "path", "status",
                   "duration_ms", "input", "output"]
SAMPLES = ["clearly_human", "clearly_ai", "plain_human", "borderline"]
CREATOR = "capstone_trial"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def load_texts() -> list[str]:
    return [
        json.loads((config.ROOT / "samples" / f"{n}.json").read_text(encoding="utf-8"))["text"]
        for n in SAMPLES
    ]


def service_up(url: str) -> bool:
    try:
        return requests.post(f"{url}/ping", json={"message": "up?"}, timeout=3).status_code == 200
    except requests.RequestException:
        return False


def start_service(url: str):
    env = dict(os.environ, AI201_DEBUG="0")   # no reloader, so one process to stop
    proc = subprocess.Popen(
        [sys.executable, "app.py"], cwd=config.ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 90
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("app.py exited on startup. Run `python3 app.py` by hand to see why.")
        if service_up(url):
            return proc
        time.sleep(0.5)
    proc.terminate()
    raise RuntimeError("the service didn't answer /ping within 90 seconds")


def stop_service(proc) -> None:
    if proc is None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def post_submit(url: str, body: dict) -> dict:
    started = time.perf_counter()
    try:
        r = requests.post(f"{url}/submit", json=body, timeout=120)
        return {"status": r.status_code, "request_id": r.headers.get("X-Request-ID"),
                "client_ms": round((time.perf_counter() - started) * 1000, 1)}
    except requests.RequestException as exc:
        return {"status": None, "request_id": None, "error": str(exc),
                "client_ms": round((time.perf_counter() - started) * 1000, 1)}


def run_trial(url: str, spawn: bool, pace: float, texts: list[str]) -> dict:
    since = now_iso()
    proc = start_service(url) if spawn else None
    sent = {"valid": [], "missing": [], "oversize": []}
    try:
        def pause():
            if pace:
                time.sleep(pace)

        for i in range(10):
            sent["valid"].append(post_submit(url, {"text": texts[i % len(texts)], "creator_id": CREATOR}))
            pause()
        for _ in range(3):
            sent["missing"].append(post_submit(url, {"creator_id": CREATOR}))
            pause()
        for _ in range(3):
            sent["oversize"].append(post_submit(url, {"text": "word " * 2100, "creator_id": CREATOR}))
            pause()
    finally:
        stop_service(proc)

    entries = [e for e in request_log.read_entries() if e.get("timestamp", "") >= since]
    return {"since": since, "sent": sent, "entries": entries}


def score_trial(trial: dict) -> dict:
    entries, sent = trial["entries"], trial["sent"]
    logged_ids = {e.get("request_id") for e in entries}

    # 1. of the 10 valid requests, how many appear in the file
    ids = [r["request_id"] for r in sent["valid"]]
    c1 = sum(1 for i in ids if i and i in logged_ids)

    # 2. of the 6 bad requests, how many got a 4xx or 5xx
    bad = sent["missing"] + sent["oversize"]
    c2 = sum(1 for r in bad if r["status"] is not None and r["status"] >= 400)

    submits = [e for e in entries if e.get("path") == "/submit" and e.get("method") == "POST"]

    # 3. every warm /submit (all but the first) at most 100 ms
    warm = [e["duration_ms"] for e in submits[1:] if isinstance(e.get("duration_ms"), (int, float))]
    c3_ok = sum(1 for d in warm if d <= WARM_LIMIT_MS)

    # 4. the first /submit
    cold = submits[0]["duration_ms"] if submits else None

    # 5. every counted line has every field
    def skipped(e):
        return (e.get("path") in ("/ping", "/health") or e.get("status") == 404
                or (e.get("input") or {}).get("body") == "not_a_json_object")
    counted = [e for e in entries if not skipped(e)]
    complete = [e for e in counted if all(f in e for f in REQUIRED_FIELDS)]
    incomplete = [e for e in counted if e not in complete]

    return {
        "c1": f"{c1}/10",
        "c2": f"{c2}/{len(bad)}",
        "c3": f"{c3_ok}/{len(warm)} at or under {WARM_LIMIT_MS:g} ms (max {max(warm):.1f} ms)" if warm else "no warm requests logged",
        "c4": f"{cold:.1f} ms" if cold is not None else "no /submit logged",
        "c5": f"{len(complete)}/{len(counted)} lines complete",
        "incomplete": incomplete,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--label", default="before", help="before or after")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--pace", type=float, default=6.5,
                    help="seconds between requests (default stays under the 10-per-minute limit)")
    ap.add_argument("--url", default=f"http://{config.HOST}:{config.PORT}")
    ap.add_argument("--no-spawn", action="store_true",
                    help="use a service that is already running. Criterion 4 is NOT valid this way.")
    args = ap.parse_args()

    if not args.no_spawn and service_up(args.url):
        print(f"Something is already answering at {args.url}. Stop that copy of app.py first,\n"
              f"so every trial gets a real cold start.")
        return 1

    texts = load_texts()
    trials = []
    for n in range(1, args.trials + 1):
        print(f"\n=== Trial {n} of {args.trials} ===")
        try:
            trial = run_trial(args.url, not args.no_spawn, args.pace, texts)
        except RuntimeError as exc:
            print(f"Trial {n} failed: {exc}")
            return 1
        scored = score_trial(trial)
        trials.append((trial, scored))
        print(f"  1 coverage {scored['c1']}   2 bad input {scored['c2']}   3 warm {scored['c3']}")
        print(f"  4 cold {scored['c4']}   5 fields {scored['c5']}")

    rows = [
        ("1. Of 10 requests, at least 7 appear in requests.jsonl", "7 of 10", "c1"),
        ("2. Missing or oversized text returns 4xx/5xx", "all (no count given)", "c2"),
        ("3. Every warm /submit takes at most 0.1 s (duration_ms)", "every one", "c3"),
        ("4. First /submit after restart at most 3.75 s (duration_ms)", "at most 3750 ms", "c4"),
        ("5. Every counted log line has all 8 fields", "every line", "c5"),
    ]
    lines = ["| Criterion | Target | " + " | ".join(f"Run {i}" for i in range(1, len(trials) + 1)) + " | Verdict |",
             "|---|---|" + "---|" * len(trials) + "---|"]
    for name, target, key in rows:
        cells = " | ".join(s[key] for _, s in trials)
        lines.append(f"| {name} | {target} | {cells} |  |")
    table = "\n".join(lines)

    print("\n" + table)
    print("\nVerdict is blank on purpose: you call MET or MISSED against criteria.md.")

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = config.RESULTS_DIR / f"capstone_{args.label}_{stamp}.md"
    doc = [f"# Capstone run: {args.label}", "", f"Run at {stamp}. `python3 run_capstone.py --label {args.label}`", "",
           table, "", "## What this script assumed", ""]
    doc += [f"- {a}" for a in ASSUMPTIONS]
    for i, (trial, scored) in enumerate(trials, 1):
        doc += ["", f"## Trial {i}: real output", "",
                f"Source: `logs/requests.jsonl`, written by `request_log.py::init_app` (lines since {trial['since']}).", "",
                "```"]
        doc += [json.dumps(e, ensure_ascii=False) for e in trial["entries"]]
        doc += ["```"]
        if scored["incomplete"]:
            doc += ["", "Lines missing a field:", "```"]
            doc += [json.dumps(e, ensure_ascii=False) for e in scored["incomplete"]]
            doc += ["```"]
    out.write_text("\n".join(doc) + "\n", encoding="utf-8")
    print(f"\nFull output (with the real log lines for each trial): {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
