#!/usr/bin/env python3
"""
Run criterion 3, the appeal path, three times.  <- UNIT 8, MILESTONE 3

    python app.py                              # in one terminal
    python run_appeals.py --label before       # in another

run_eval.py only sends to /submit, and an appeal needs a real content_id from
a submission first. Each trial here:

  1. submits five texts and keeps the content_ids that come back,
  2. appeals each one and checks the response says under_review,
  3. checks GET /log shows each appeal next to its original decision,
  4. appeals an unknown content_id and checks it gets a 404 and adds nothing
     to the log.

Like run_eval.py, this records what came back and leaves the verdict to you.
"""

import argparse
import datetime as dt
import json
import sys

import config

DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"

TEXTS = [
    "We got to the lake just after nine and the water was still flat. My sister "
    "swam out to the buoy and back twice before I had my shoes off.",
    "The library moved to the new building in March. The quiet room is smaller "
    "now, but the chairs are better and there are plugs at every desk.",
    "I tried the recipe twice. The first time the bread came out dense because I "
    "rushed the second rise. The second time I waited, and it worked.",
    "Our team lost the first three games of the season. Then the coach moved me "
    "to defence, and we won four in a row, which nobody expected.",
    "The bus was late again this morning. I stood at the stop for twenty minutes "
    "and read half a chapter of my book before it finally came.",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print("The `requests` package isn't installed.\n"
              "Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    try:
        requests.get(f"{args.url}/health", timeout=5)
    except Exception:  # noqa: BLE001
        print(f"Nothing answering at {args.url}. Start it:  python app.py",
              file=sys.stderr)
        sys.exit(1)

    def log_entries():
        return requests.get(f"{args.url}/log", timeout=args.timeout).json()["entries"]

    trials = []
    for trial in range(1, args.trials + 1):
        appeals = []
        for i, text in enumerate(TEXTS, 1):
            submitted = requests.post(
                f"{args.url}/submit",
                json={"text": text, "creator_id": f"eval_appeal_{trial}_{i}"},
                timeout=args.timeout,
            )
            content_id = submitted.json().get("content_id")
            appealed = requests.post(
                f"{args.url}/appeal",
                json={"content_id": content_id,
                      "reasoning": "I wrote this myself. Please review it."},
                timeout=args.timeout,
            )
            appeals.append({
                "submit_status": submitted.status_code,
                "content_id": content_id,
                "appeal_status": appealed.status_code,
                "appeal_response": appealed.json(),
            })

        # Every appeal should now sit in the log after its original decision.
        entries = log_entries()
        for appeal in appeals:
            mine = [e for e in entries if e.get("content_id") == appeal["content_id"]]
            appeal["log_statuses"] = [e.get("status") for e in mine]
            appeal["in_log_as_under_review"] = (
                any(e.get("event") == "appeal" and e.get("status") == "under_review"
                    for e in mine)
            )

        before = len(entries)
        unknown = requests.post(
            f"{args.url}/appeal",
            json={"content_id": f"c_unknown_trial{trial}",
                  "reasoning": "I wrote this myself. Please review it."},
            timeout=args.timeout,
        )
        after = len(log_entries())

        result = {
            "appeals": appeals,
            "appeals_under_review": sum(a["in_log_as_under_review"] for a in appeals),
            "unknown_id": {
                "status": unknown.status_code,
                "response": unknown.json(),
                "log_entries_before": before,
                "log_entries_after": after,
            },
        }
        trials.append(result)
        print(f"  trial {trial}: {result['appeals_under_review']}/{len(appeals)} "
              f"under_review in the log · unknown id -> {unknown.status_code}, "
              f"log {before} -> {after}")

    write_report(trials, args)


def write_report(trials, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"appeals_{stamp}{label}.md"

    lines = [
        f"# Appeal run{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_appeals.py::main`",
        "- Service: `app.py::submit`, `app.py::appeal`, `app.py::get_log`",
        f"- {len(trials)} trials · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Trial | Appeals under_review in the log | Unknown id status | Log entries before → after |",
        "|---|---|---|---|",
    ]
    for n, t in enumerate(trials, 1):
        u = t["unknown_id"]
        lines.append(f"| {n} | {t['appeals_under_review']}/{len(t['appeals'])} | "
                     f"{u['status']} | {u['log_entries_before']} → {u['log_entries_after']} |")

    lines += ["", "---", "", "## What actually came back", ""]
    for n, t in enumerate(trials, 1):
        lines += [f"**Trial {n}**", "", "```json", json.dumps(t, indent=2), "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
