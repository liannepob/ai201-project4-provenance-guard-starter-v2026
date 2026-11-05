# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-04 17:38
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_e45179033d59` | human | 0.346 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_dcc393a7aa5c` | unsure | 0.445 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_57552b58d72a` | unsure | 0.525 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_ae7442880d67` | unsure | 0.556 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_5bffbb69dcc8` | human | 0.332 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_e11aa117d086` | unsure | 0.510 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_56d686c438ad` | unsure | 0.370 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `c_dc855279ffe1` | unsure | 0.373 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_7019206c7a00` | unsure | 0.560 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_93d450fc68f1` | ai | 0.903 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_1a65c6929e35` | unsure | 0.659 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_dd9208c9f771` | unsure | 0.761 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_d0c494873515` | unsure | 0.798 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_360254c88ad8` | unsure | 0.702 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_91fe59f97748` | ai | 0.833 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_bb90b42dad7c` | unsure | 0.763 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_35035c5f63d3` | unsure | 0.781 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `c_3bd5405b385d` | unsure | 0.411 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_827c17e0291b` | unsure | 0.485 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_8baff6d3b555` | human | 0.234 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_7582f790fbd2` | unsure | 0.533 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_985cf1adaad5` | unsure | 0.379 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_b5ce378d6482` | unsure | 0.411 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_e35fbcbd7354` | unsure | 0.635 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `c_c2f732cf0dc0` | human | 0.250 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `c_31c581f18eef` | human | 0.256 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `c_a29d1483454c` | unsure | 0.749 | HELD |
| MF06 | malformed | text is emoji only | 200 | `c_baab2bb01993` | unsure | 0.749 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_11042393549e` | unsure | 0.703 | HELD |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_f837d516fbf1` | human | 0.264 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_2001de2cf85e` | human | 0.264 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_0e7a065e9809` | human | 0.264 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_bee8734104c1` | human | 0.264 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_47deda21485f` | human | 0.264 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_2fbdade2e88f` | human | 0.264 | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_e179ccbad55d` | human | 0.264 | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_f80e0797b687` | human | 0.264 | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_45d00e0bf409` | human | 0.264 | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_775bae141fce` | human | 0.264 | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_e45179033d59",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.3464,
  "model_score": 0.1635,
  "style_score": 0.5294,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_dcc393a7aa5c",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.4449,
  "model_score": 0.5943,
  "style_score": 0.2954,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_57552b58d72a",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5251,
  "model_score": 0.6662,
  "style_score": 0.3839,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_ae7442880d67",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.5564,
  "model_score": 0.6114,
  "style_score": 0.5013,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_5bffbb69dcc8",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3315,
  "model_score": 0.3212,
  "style_score": 0.3417,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_e11aa117d086",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.51,
  "model_score": 0.5727,
  "style_score": 0.4473,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_56d686c438ad",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.3699,
  "model_score": 0.5862,
  "style_score": 0.1536,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_dc855279ffe1",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.3726,
  "model_score": 0.2452,
  "style_score": 0.5,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_7019206c7a00",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.5597,
  "model_score": 0.7042,
  "style_score": 0.4153,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_93d450fc68f1",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.9029,
  "model_score": 0.9792,
  "style_score": 0.8266,
  "label": "Our tools suggest this text was written by an AI tool, but we could be wrong. If you wrote it yourself, you can appeal and it will be marked for review.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_1a65c6929e35",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.659,
  "model_score": 0.6175,
  "style_score": 0.7005,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_dd9208c9f771",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.7606,
  "model_score": 0.7387,
  "style_score": 0.7825,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_d0c494873515",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.7981,
  "model_score": 0.8051,
  "style_score": 0.7911,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_360254c88ad8",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.7024,
  "model_score": 0.8329,
  "style_score": 0.5718,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_91fe59f97748",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.8328,
  "model_score": 0.8005,
  "style_score": 0.8651,
  "label": "Our tools suggest this text was written by an AI tool, but we could be wrong. If you wrote it yourself, you can appeal and it will be marked for review.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_bb90b42dad7c",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.7633,
  "model_score": 0.8814,
  "style_score": 0.6452,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_35035c5f63d3",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.7815,
  "model_score": 0.8816,
  "style_score": 0.6814,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c_3bd5405b385d",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.4112,
  "model_score": 0.3223,
  "style_score": 0.5,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_827c17e0291b",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.4849,
  "model_score": 0.4625,
  "style_score": 0.5073,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_8baff6d3b555",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2339,
  "model_score": 0.2044,
  "style_score": 0.2634,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_7582f790fbd2",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5331,
  "model_score": 0.5943,
  "style_score": 0.4718,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_985cf1adaad5",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.3785,
  "model_score": 0.4998,
  "style_score": 0.2571,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_b5ce378d6482",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.4113,
  "model_score": 0.6401,
  "style_score": 0.1826,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_e35fbcbd7354",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.6351,
  "model_score": 0.5583,
  "style_score": 0.7118,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "c_c2f732cf0dc0",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.25,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c_31c581f18eef",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.2556,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c_a29d1483454c",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.7488,
  "model_score": 0.9976,
  "style_score": 0.5,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "c_baab2bb01993",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.7485,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_11042393549e",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.7032,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "c_f837d516fbf1",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "c_2001de2cf85e",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c_0e7a065e9809",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "c_bee8734104c1",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c_47deda21485f",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "c_2fbdade2e88f",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "c_e179ccbad55d",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "c_f80e0797b687",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "c_45d00e0bf409",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "c_775bae141fce",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this text was written by a person, because it flows naturally.",
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
