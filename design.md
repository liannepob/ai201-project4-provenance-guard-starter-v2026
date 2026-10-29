# Provenance Guard — design notes (Milestone 1)

Written before building the scoring, labels, or appeal. The submission path and
both signals with their blind spots are in the README under **What This Does**
and **Signals and Scoring**. This file holds the other two parts of Milestone 1:
the false-positive trace and the endpoint contract.

---

## Tracing the false positive

**Who:** A nurse who moved to the country two years ago and writes in careful,
plain English. They submit a short personal piece they wrote themselves:

> I moved to this city two years ago for work. At first it was hard because I
> did not know anyone. I work in a hospital as a nurse. The work is busy but I
> like to help people. On weekends I go to the park and I call my family at
> home. My English is better now and I have some good friends. I think the most
> important thing is to be patient.

**Signal one:** I ran this through `python detector.py`. Perplexity was
**14.7** and `model_signal` was **0.857**. That's higher than my clearly-AI
sample (0.754). To GPT-2, common words in short sentences are exactly what a
machine would write.

**Signal two:** This probably doesn't help them. Seven sentences of similar
length, simple vocabulary, and nothing but full stops: on every measure the
style signal is likely to call this AI-ish too, so both signals agree, and
they're both wrong.

**The score:** With the starter's 50/50 weights and a style score of even 0.5,
the combined score is about 0.68. That's over the 0.65 AI threshold, so the
writer gets the **high-confidence AI** label. If the style signal also leans AI
(say 0.7), the score is about 0.78.

**What they see:** Whatever the high-confidence AI label says. Right now that's
a statement, on their own work, that a machine probably wrote it. They have no
technical way to see why, and they're the writer least equipped to argue with
a confident-sounding system in their second language.

**What they can do:** Use `POST /appeal` with the `content_id` from their
submission and a sentence of reasoning. The item moves to `under_review`, the
appeal sits in the log next to the original decision, and they get a
confirmation. Nothing is automatically re-scored. A person has to look at it.

**What this decides:**
- The **AI threshold has to sit high enough** that plain human writing doesn't
  clear it on signal one alone. At 0.65 with a 50/50 split, it doesn't.
- The **high-confidence AI label must not read as a verdict.** It should say
  what the system thinks, that it might be wrong, and how to appeal, in plain
  words.
- The **appeal must work from the label alone**: the writer needs the
  `content_id` and a clear way in, not a support email.
- The signals agreeing isn't proof. Both of mine share the same blind spot
  (plain writing), so agreement between them on plain text is weaker evidence
  than it looks.

---

## Endpoint contract

All requests and responses are JSON (`Content-Type: application/json`).
Every error response has the same shape:
`{"error": "<code>", "message": "<sentence a person can read>"}`.

### `POST /submit`

**Request**

| Field | Type | Required | Rules |
|---|---|---|---|
| `text` | string | yes | Must contain non-whitespace characters. Very short text (fewer than ~3 tokens) can't be scored and is rejected. Text past ~400 tokens is still accepted, but only the first ~400 tokens are scored by signal one. |
| `creator_id` | string | yes | Non-empty. Identifies the writer. It isn't checked against any account. |

**Response: `200 OK`**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Unique ID for this submission. Needed to appeal. |
| `guess` | string | One of `"ai"`, `"human"`, `"unsure"`. |
| `confidence` | number, 0–1 | The combined score. **0 = confidently human, 1 = confidently AI.** It is not "how sure of the guess": 0.10 means confidently human. |
| `label` | string | The full sentence shown to the reader. |
| `model_score` | number, 0–1 | Signal one on its own. Higher = more likely AI. |
| `style_score` | number, 0–1 | Signal two on its own. Higher = more likely AI. |

```json
{
  "content_id": "3f2b9c1e8a7d4f60b5e2c9a1d7f3e8b4",
  "guess": "unsure",
  "confidence": 0.52,
  "label": "<the unsure label text>",
  "model_score": 0.61,
  "style_score": 0.43
}
```

**Errors**

| Status | `error` | When |
|---|---|---|
| 400 | `bad_request` | Body isn't JSON, `text` is missing, not a string, or blank, `creator_id` is missing, or the text is too short to score. Also logged as a rejection. |
| 503 | `detector_unavailable` | The local model couldn't load. |

### `POST /appeal`

**Request**

| Field | Type | Required | Rules |
|---|---|---|---|
| `content_id` | string | yes | Must match a submission already in the audit log. |
| `reasoning` | string | yes | Non-empty. The writer's explanation, in their words. |

**Response: `200 OK`**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | The item appealed. |
| `status` | string | Always `"under_review"`. |
| `message` | string | A plain confirmation to the writer that the appeal was received and a person will review it. |

```json
{
  "content_id": "3f2b9c1e8a7d4f60b5e2c9a1d7f3e8b4",
  "status": "under_review",
  "message": "<confirmation text>"
}
```

**Errors**

| Status | `error` | When |
|---|---|---|
| 400 | `bad_request` | Body isn't JSON, or `content_id` or `reasoning` is missing or blank. |
| 404 | `not_found` | No submission with that `content_id` exists in the log. |

**Behaviour notes**
- The appeal never overwrites the original decision. It is appended to the log
  after it (`audit.log_appeal`), using the `creator_id` from the original
  submission.
- Appealing the same item twice is allowed. Each appeal is logged and returns
  200.
- No re-scoring happens on appeal.
