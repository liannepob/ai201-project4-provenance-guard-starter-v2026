"""
The request log (capstone).

audit.py records DECISIONS. This records REQUESTS: every call that reaches the
service, whether it succeeded, was rejected, or crashed, with how long it took.

One JSON object per line in logs/requests.jsonl. Fields:

    timestamp     when the request arrived (UTC, ISO 8601)
    request_id    short id, also returned in the X-Request-ID header
    method, path  what was asked for
    status        the HTTP status that went back
    duration_ms   wall-clock time for the whole request
    input         what came in: text length, a short preview, creator_id
    output        what went out: content_id, guess, label, scores, or the error code
    stages        optional per-stage timings (model_ms, style_ms)
    error         set when a request failed (4xx/5xx) or an exception escaped

A failure that shows up only as an absence is one you'll never find, so
errors are written too, including unhandled exceptions, which come back as a
JSON 500 instead of an HTML crash page.
"""

import json
import threading
import time
import uuid
from datetime import datetime, timezone

from flask import g, jsonify, request

import config

REQUEST_LOG = config.LOG_DIR / "requests.jsonl"
PREVIEW_CHARS = 60
_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def note(**stages) -> None:
    """Record a stage timing for the current request, e.g. note(model_ms=812.4)."""
    if not hasattr(g, "stages"):
        g.stages = {}
    g.stages.update(stages)


def _summarize_input(payload) -> dict:
    if not isinstance(payload, dict):
        return {"body": "not_a_json_object"}
    text = payload.get("text")
    summary = {"creator_id": payload.get("creator_id")}
    if isinstance(text, str):
        summary["text_chars"] = len(text)
        summary["text_preview"] = text[:PREVIEW_CHARS]
    elif "text" in payload:
        summary["text_type"] = type(text).__name__
    else:
        summary["text"] = "missing"
    if "content_id" in payload:
        summary["content_id"] = payload.get("content_id")
    return summary


def _summarize_output(body) -> dict:
    if not isinstance(body, dict):
        return {}
    keep = ("content_id", "guess", "label", "confidence", "model_score",
            "style_score", "status", "error", "message")
    out = {k: body[k] for k in keep if k in body}
    # The label text is long; the first words identify which of the three it was.
    if isinstance(out.get("label"), str):
        out["label"] = out["label"][:40]
    return out


def _write(entry: dict) -> None:
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False)
    with _lock:
        with REQUEST_LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def read_entries(limit: int | None = None) -> list[dict]:
    """Read the request log back, oldest first. Bad lines are skipped."""
    if not REQUEST_LOG.exists():
        return []
    entries = []
    for line in REQUEST_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries[-limit:] if limit else entries


def init_app(app) -> None:
    """Attach the logger to a Flask app. Leaves every route untouched."""

    @app.before_request
    def _start():
        g.request_id = f"r_{uuid.uuid4().hex[:10]}"
        g.started = time.perf_counter()
        g.ts = _now()
        g.exception = None

    @app.errorhandler(Exception)
    def _unhandled(exc):
        # HTTP errors (404, 405, 429...) keep their own response.
        from werkzeug.exceptions import HTTPException
        if isinstance(exc, HTTPException):
            return exc
        g.exception = f"{type(exc).__name__}: {exc}"
        return jsonify({
            "error": "internal_error",
            "message": "Something went wrong on our side. The request was logged.",
            "request_id": g.request_id,
        }), 500

    @app.after_request
    def _finish(response):
        if not hasattr(g, "started"):
            return response
        duration_ms = round((time.perf_counter() - g.started) * 1000, 1)
        response.headers["X-Request-ID"] = g.request_id

        body = response.get_json(silent=True) if response.is_json else None
        payload = request.get_json(silent=True)

        entry = {
            "timestamp": g.ts,
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "input": _summarize_input(payload),
            "output": _summarize_output(body),
        }
        if getattr(g, "stages", None):
            entry["stages"] = g.stages
        if response.status_code >= 400:
            entry["error"] = (
                g.exception
                or (body or {}).get("error")
                or f"http_{response.status_code}"
            )
        _write(entry)
        return response
