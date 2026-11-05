# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. **The request arrives** at `POST /submit` (`app.py::submit`). Flask parses
   the body as JSON. *Adds:* a `payload` dict, or an empty one if the body
   wasn't JSON.
2. **The input is checked.** `text` must be a non-empty string of at most
   10,000 characters, long enough to score, and `creator_id` must be a
   non-empty string. If not, the route stops and returns a 400, and nothing is
   written to the log. *Adds:* a guarantee that everything below gets real
   text.
3. **A `content_id` is assigned**, a new unique ID for this one submission.
   *Adds:* the handle that the log, the response, and any later appeal all
   share.
4. **Signal one reads the text** (`detector.model_signal`). GPT-2, running
   locally, measures how predictable the text is (perplexity), and that is
   turned into a 0–1 score. *Adds:* `model_score`, where higher means more
   likely AI.
5. **Signal two measures the text as text** (`stylometry.style_signal`):
   sentence length spread, vocabulary variety, and punctuation, combined into a
   0–1 score. *Adds:* `style_score`, where higher means more likely AI.
6. **The two signals are combined** (`scoring.combine_signals`) into one 0–1
   number. *Adds:* `confidence`, the combined score, where 0 means confidently
   human and 1 means confidently AI.
7. **The number becomes words** (`scoring.score_to_label`). Thresholds in
   `config.py` pick one of three bands. *Adds:* `guess` (`ai` / `human` /
   `unsure`) and the full-sentence `label` a reader sees.
8. **Everything is logged, then returned.** `audit.log_decision` writes the
   timestamp, ids, both signal scores, the combined score, the guess, the
   label, and `status: "decided"` to `logs/audit.jsonl`. The same fields go
   back to the caller as JSON, and the site shows the reader the `label`.

**Afterwards, if the writer disagrees:** they send the `content_id` and their
reasoning to `POST /appeal`. The appeal is logged beside the original decision
(nothing is overwritten), the status moves to `under_review`, and they get a
confirmation.

The endpoint contract and the false-positive trace from Milestone 1 are in
[design.md](design.md).



---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is to a language model
(`detector.py::model_signal`). GPT-2 runs locally and computes perplexity, a
measure of how surprised it is by each next word. Low perplexity gives a high
score. The raw number goes through a logistic curve so that perplexity 45 maps
to 0.5.

**Why that might differ between human and AI writing:** A language model
writes by repeatedly picking a likely next word, so its output is text a model
finds easy to predict. Human writing tends to wander more: odd word choices,
specific details, abrupt turns.

**What it can't see:** Who actually wrote it. Predictability isn't authorship.
This signal rewards common words in short, ordinary sentences, and plenty of
people write that way: second-language writers, younger writers, anyone writing
plainly on purpose. In my own test, a plainly written human paragraph scored
**0.857**, higher than my clearly-AI sample (0.754). It also misses in the
other direction. AI text with a few unusual word choices swapped in looks
human: my "borderline" sample (AI-style content in casual wording) scored
0.349, below my clearly-human sample (0.445).

### Signal two — the style signal

**What it measures:** The shape of the text, without reading it
(`stylometry.py::style_signal`). It uses three measures:
- **Sentence length spread:** the standard deviation of words per sentence.
- **Type-token ratio:** unique words over total words.
- **Punctuation density:** punctuation marks per word. Every mark counts
  equally, except apostrophes, which come from contractions and possessives
  rather than style.

These are combined into a 0–1 score where higher means more likely AI.

**Why that might differ between human and AI writing:** Generated prose tends
toward even, mid-length sentences, a narrower and safer vocabulary, and tidy
comma-and-full-stop punctuation, because "most likely next word" averages out
to that. Human writing is lumpier: a three-word sentence next to a forty-word
one, a dash where a comma would do.

**What it can't see:** Meaning. Anything that changes the shape without
changing the substance moves it: breaking long sentences into short ones,
adding typos (which raise word variety), or pasting in a quotation or a list.
That makes it cheap to fool on purpose. It is also length-sensitive, because
type-token ratio falls as text gets longer, so a short piece and a long piece
aren't directly comparable. And like signal one, it can mistake a plain,
evenly paced human writer for a machine.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** A weighted average of the two signals. Both are on 0–1 with
higher meaning more likely AI, so the combined score is on the same scale.
When the signals disagree, the score lands between them, so strong
disagreement tends to end up in the unsure band.

**The numbers:** model signal weight **0.5**, style signal weight **0.5**
(`WEIGHT_MODEL_SIGNAL` and `WEIGHT_STYLE_SIGNAL` in `config.py`).

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**
My clearly-human sample (a first-person piece about a bad night and a
coworker who notices). The model signal scored it **0.445**, close to unsure,
because GPT-2 found it fairly predictable. The style signal scored it
**0.178**, firmly human, because its sentence lengths vary widely (spread of
15 words). The 50/50 average gives **0.311**, which is under the 0.35 human
threshold, so it gets the human label. Here the style signal pulls a
borderline model reading back to the right answer.



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – under 0.35 | We think this text was written by a person, because it flows naturally. |
| unsure | 0.35 – under 0.80 | We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post. |
| high-confidence AI | 0.80 – 1.00 | Our tools suggest this text was written by an AI tool, but we could be wrong. If you wrote it yourself, you can appeal and it will be marked for review. |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d @samples/plain_human.json
```

```json
{
  "confidence": 0.8216,
  "content_id": "c_08008ac0b540",
  "guess": "ai",
  "label": "Our tools suggest this text was written by an AI tool, but we could be wrong. If you wrote it yourself, you can appeal and it will be marked for review.",
  "model_score": 0.8567,
  "style_score": 0.7865
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_08008ac0b540", "reasoning": "I wrote this myself. English is my second language, so I write plainly."}'
```

```json
{
  "content_id": "c_08008ac0b540",
  "message": "We've received your appeal. A person will review this decision.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=2"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.8216,
      "content_id": "c_08008ac0b540",
      "creator_id": "demo_instructor",
      "guess": "ai",
      "label": "Our tools suggest this text was written by an AI tool, but we could be wrong. If you wrote it yourself, you can appeal and it will be marked for review.",
      "model_score": 0.8567,
      "status": "decided",
      "style_score": 0.7865,
      "timestamp": "2026-11-02T00:18:01+00:00"
    },
    {
      "content_id": "c_08008ac0b540",
      "creator_id": "demo_instructor",
      "event": "appeal",
      "reasoning": "I wrote this myself. English is my second language, so I write plainly.",
      "status": "under_review",
      "timestamp": "2026-11-02T00:18:01+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 10 per minute, 200 per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->
A real writer needs time to think and put their ideas into words, so they
might submit a few pieces an hour. That is far below 10 a minute or 200 a
day, so the limits never get in their way. A script doesn't need that time and
can send hundreds of variations a minute to find where my thresholds sit. 10 a
minute slows that to a crawl, and 200 a day caps how much it can learn in one
day.

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->
Per `creator_id` when the request has a usable one, otherwise per IP address
(`app.py::rate_limit_key`).

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
$ python run_attacks.py --flood 15
15 submissions as 'flood_tester' against http://127.0.0.1:5000
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

From `results/flood_2026-11-04_1726.md`: the first 10 went through and the
next 5 were refused with 429, matching the 10-per-minute limit.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

Source: `results/attack_run_2026-11-04_1738_before.md`, produced by
`run_attacks.py --set attack_set --label before`. 56 attacks, 0 crashes.

**How I marked HELD or BROKE:** an attack BROKE if it got what it was going
for. AI text labeled `unsure` counts as BROKE, because it wasn't caught. Human
text labeled `unsure` counts as HELD, because the writer wasn't accused.
Malformed input HELD if it was rejected or labeled `unsure`, and BROKE if junk
got a confident `human` or `ai` label. A prompt injection BROKE if the result
did what the instruction asked, or if the log or label was corrupted.

| Family | Attacks | HELD | BROKE |
|---|---|---|---|
| evasion | 10 | 1 | 9 |
| false_positive | 8 | 7 | 1 |
| prompt_injection | 6 | 5 | 1 |
| malformed (text) | 8 | 6 | 2 |
| malformed (request) | 12 | 12 | 0 |
| flood_same_creator | 12 | 12 | 0 |
| **Total** | **56** | **43** | **13** |

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


**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

From `logs/audit.jsonl`, in this order: FP05, FP03, EV01, EV05, EV09, PI02,
PI05, MF03, MF04, and one rate-limit rejection from the flood rows (FL01_11).

```json
{"timestamp": "2026-11-05T01:38:43+00:00", "content_id": "c_91fe59f97748", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.8651, "combined_score": 0.8328, "label": "Our tools suggest this text was written by an AI tool, but we could be wrong. If you wrote it yourself, you can appeal and it will be marked for review.", "status": "decided"}
{"timestamp": "2026-11-05T01:38:43+00:00", "content_id": "c_d0c494873515", "creator_id": "attacker_FP03", "guess": "unsure", "model_score": 0.8051, "style_score": 0.7911, "combined_score": 0.7981, "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.", "status": "decided"}
{"timestamp": "2026-11-05T01:38:42+00:00", "content_id": "c_e45179033d59", "creator_id": "attacker_EV01", "guess": "human", "model_score": 0.1635, "style_score": 0.5294, "combined_score": 0.3464, "label": "We think this text was written by a person, because it flows naturally.", "status": "decided"}
{"timestamp": "2026-11-05T01:38:42+00:00", "content_id": "c_5bffbb69dcc8", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.3417, "combined_score": 0.3315, "label": "We think this text was written by a person, because it flows naturally.", "status": "decided"}
{"timestamp": "2026-11-05T01:38:43+00:00", "content_id": "c_7019206c7a00", "creator_id": "attacker_EV09", "guess": "unsure", "model_score": 0.7042, "style_score": 0.4153, "combined_score": 0.5597, "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.", "status": "decided"}
{"timestamp": "2026-11-05T01:38:43+00:00", "content_id": "c_8baff6d3b555", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.2634, "combined_score": 0.2339, "label": "We think this text was written by a person, because it flows naturally.", "status": "decided"}
{"timestamp": "2026-11-05T01:38:43+00:00", "content_id": "c_b5ce378d6482", "creator_id": "attacker_PI05", "guess": "unsure", "model_score": 0.6401, "style_score": 0.1826, "combined_score": 0.4113, "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.", "status": "decided"}
{"timestamp": "2026-11-05T01:38:43+00:00", "content_id": "c_c2f732cf0dc0", "creator_id": "attacker_MF03", "guess": "human", "model_score": 0.0, "style_score": 0.5, "combined_score": 0.25, "label": "We think this text was written by a person, because it flows naturally.", "status": "decided"}
{"timestamp": "2026-11-05T01:38:43+00:00", "content_id": "c_31c581f18eef", "creator_id": "attacker_MF04", "guess": "human", "model_score": 0.0112, "style_score": 0.5, "combined_score": 0.2556, "label": "We think this text was written by a person, because it flows naturally.", "status": "decided"}
{"timestamp": "2026-11-05T01:38:44+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "10 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**FP05: a person's technical documentation was labeled AI.** It scored 0.833
combined (model 0.801, style 0.865), over my 0.80 cutoff, so the writer was
told "Our tools suggest this text was written by an AI tool." Technical
writing uses standard, predictable wording and short, evenly sized
instructions, and both of my signals read that as machine-like. This is the
worst outcome because it is the exact mistake my system is built to avoid: a
real person accused of not writing their own work, with an appeal as their
only way to clear it.



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
