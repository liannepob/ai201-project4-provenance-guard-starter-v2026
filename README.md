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
   10,000 characters, long enough to score, with at least one letter and no
   control characters (added in unit 8), and `creator_id` must be a
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

Most real writing lands in this band, so most writers will read this label
about their own work. I wanted it to say plainly that the system can't tell,
and then answer the question a worried writer would ask next: does this mean
I'm in trouble? So it says outright that no conclusion is being drawn about
them and that nothing happens to their post. It never uses the word "AI" as a
verdict, only as one of two possibilities.



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

**Moment 1 (unit 7): checking my acceptance criteria**

- *What I asked for:* I pasted my five draft criteria into Claude and asked
  whether each one could be checked by someone who couldn't ask me what I
  meant.
- *What came back:* It didn't rewrite them. It pointed out that criteria 1
  and 3 contradicted each other (a 1,000- versus 10,000-character limit), that
  I only covered two of the required areas, and that criterion 5 would
  probably pass automatically because the detector scores the same text the
  same way every time.
- *What I changed:* I made the length limit 10,000 everywhere and replaced
  the duplicate bad-input criterion with one about appeals, which gave me a
  third area. I kept criterion 5 as written, and in unit 8 it did pass
  automatically, which is why I now say my targets were partly too easy.

**Moment 2 (unit 7): building the style signal**

- *What I asked for:* I asked Claude to build `stylometry.py` with three
  measures, simple clamped scaling, and constants in `config.py`, then run it
  on my samples.
- *What came back:* Working code, plus two findings I hadn't expected: on my
  samples, vocabulary variety pointed the wrong way (the AI text had the most
  varied vocabulary), and a plainly written human paragraph scored 0.787, the
  most AI-looking of everything I tested.
- *What I changed:* I kept the standard direction for vocabulary variety
  rather than tuning it to four samples, and I wrote both findings into my
  signal blind spots. The plain-writing problem showed up again in unit 8 as
  FP05.

**Moment 3 (unit 8): choosing my improvement**

- *What I asked for:* I asked Claude to lower my AI cutoff from 0.80 to 0.70.
- *What came back:* Instead of making the change, it checked my attack scores
  first: at 0.70, no extra AI text would be caught (the evasions scored
  0.37–0.56), but five more real writers would be labeled AI, including the
  non-native speaker (FP03).
- *What I changed:* I dropped the cutoff change and used input validation
  instead, which fixed MF03 and MF04 without flagging anyone new.

**Moment 4 (unit 8): diagnosing PI02**

- *What I asked for:* I gave Claude my rough diagnoses, including that the
  PI02 injection worked because GPT-2 read the instruction and followed it.
- *What came back:* It corrected that: GPT-2 doesn't follow instructions, it
  only measures predictability, so tokens like `SYSTEM:` and `guess=human`
  raised perplexity and lowered the score. The injection worked as noise, not
  as a command.
- *What I changed:* I rewrote my PI02 diagnosis to say that, and grouped it
  with EV01 and the junk inputs under one problem: signal one reads anything
  unusual as human.

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
| 1. My own writing labeled high-confidence AI | ≤ 2 of 10 | 0/10 | 0/10 | 0/10 | MET |
| 2. Bad input gets a 400 and no log entry | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 3. Appeals reach `under_review` in the log; unknown id gets a 404 and changes nothing | 5 of 5 + 404 | 5/5, 404 | 5/5, 404 | 5/5, 404 | MET |
| 4. Formal writing labeled high-confidence AI | ≤ 1 of 5 | 0/5 | 0/5 | 0/5 | MET |
| 5. Same text 5 times: score spread and label | ≤ 0.10, same label | 0.00, same | 0.00, same | 0.00, same | MET |

Sources: criteria 1, 2, 4 and 5 from `results/run_2026-11-04_1840_before.md`
(`run_eval.py::main`). Criterion 3 from `results/appeals_2026-11-04_1800_before.md`
(`run_appeals.py::main`), a script I added because `run_eval.py` only sends to
`/submit` and an appeal needs a real `content_id` first. For criterion 2's "no
log entry" part, `GET /health` showed 180 log entries before the run and 240
after: exactly the 60 decisions from criteria 1, 4 and 5, so the 9 bad-input
requests added nothing. All three trials came out identical for every
criterion, as expected, since neither signal is random.

**Real output from one trial**, pasted as text, naming the file and function
that produced it. All from trial 1.

*Criterion 1, my own writing* (`run_eval.py::main`, `results/run_2026-11-04_1840_before.md`):

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5458,
    "model_score": 0.5917,
    "style_score": 0.5,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "Last weekend I was with friends and I went around the city."
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6667,
    "model_score": 0.5048,
    "style_score": 0.8286,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "To make bubble tea first I would boil some water for the pearls and th"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6529,
    "model_score": 0.8058,
    "style_score": 0.5,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "When something went wrong I first took a step back and addressed the s"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.497,
    "model_score": 0.6237,
    "style_score": 0.3704,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "My favorite place to be at is my bed room with some privacy and being "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6376,
    "model_score": 0.6084,
    "style_score": 0.6667,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "In my opinion the new Spiderman movie was really good just really long"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2401,
    "model_score": 0.4601,
    "style_score": 0.02,
    "label": "We think this text was written by a person, because it flows naturally.",
    "sent": "I would let a friend know in this way, \"Hey im running late right now,"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2051,
    "model_score": 0.2101,
    "style_score": 0.2,
    "label": "We think this text was written by a person, because it flows naturally.",
    "sent": "I first wake up, brush teeth and then make bed, do skincare, change, a"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4615,
    "model_score": 0.2579,
    "style_score": 0.6651,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "Right now in Calculus 3 we are learning about double integrals which i"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3483,
    "model_score": 0.1183,
    "style_score": 0.5784,
    "label": "We think this text was written by a person, because it flows naturally.",
    "sent": "Someone who influenced me was a family member they push me to work har"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2878,
    "model_score": 0.0756,
    "style_score": 0.5,
    "label": "We think this text was written by a person, because it flows naturally.",
    "sent": "I want to push my web application to the app store by learning swift a"
  }
]
```

*Criterion 2, bad input* (`run_eval.py::main`, same file):

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_bad_missing\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  }
]
```

*Criterion 3, appeals* (`run_appeals.py::main`, `results/appeals_2026-11-04_1800_before.md`):

```json
{
  "appeals": [
    {
      "submit_status": 200,
      "content_id": "c_7b6063c523a4",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_7b6063c523a4",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_df64132ed2d1",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_df64132ed2d1",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_034a69c3c44b",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_034a69c3c44b",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_34acb1da53a4",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_34acb1da53a4",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_a33b41f13289",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_a33b41f13289",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    }
  ],
  "appeals_under_review": 5,
  "unknown_id": {
    "status": 404,
    "response": {
      "error": "not_found",
      "message": "No submission found with content_id \"c_unknown_trial1\"."
    },
    "log_entries_before": 100,
    "log_entries_after": 100
  }
}
```

*Criterion 4, formal writing* (`run_eval.py::main`, `results/run_2026-11-04_1840_before.md`):

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3807,
    "model_score": 0.4999,
    "style_score": 0.2615,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "I am a sophmore in college and I am studying Computer Science, I want "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.543,
    "model_score": 0.4721,
    "style_score": 0.6138,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "Dear Professor Bob, I was wondering If I was able to reschedule time f"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2182,
    "model_score": 0.3586,
    "style_score": 0.0778,
    "label": "We think this text was written by a person, because it flows naturally.",
    "sent": "I created a website/web application for individuals with food allergie"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3679,
    "model_score": 0.3485,
    "style_score": 0.3873,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "I agree that AI should not be used when first learning about a subject"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3507,
    "model_score": 0.3983,
    "style_score": 0.303,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "To whom it may concern, I ordered 10 Piece cooking pot and it only cam"
  }
]
```

*Criterion 5, same text five times* (`run_eval.py::main`, same file):

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3689,
    "model_score": 0.3489,
    "style_score": 0.3888,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "Time management matters more than people admit, especially now that wo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3689,
    "model_score": 0.3489,
    "style_score": 0.3888,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "Time management matters more than people admit, especially now that wo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3689,
    "model_score": 0.3489,
    "style_score": 0.3888,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "Time management matters more than people admit, especially now that wo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3689,
    "model_score": 0.3489,
    "style_score": 0.3888,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "Time management matters more than people admit, especially now that wo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3689,
    "model_score": 0.3489,
    "style_score": 0.3888,
    "label": "We aren't sure whether this text was written by a person or by an AI tool. We are not drawing any conclusion about you or your work, and nothing will happen to your post.",
    "sent": "Time management matters more than people admit, especially now that wo"
  }
]
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

**How I reached each verdict.** A criterion is MET only if its target held in
all three trials. All five did, and all three trials were identical every time.

1. **MET.** 0 of my 10 pieces got the AI label in any trial; the highest score
   was 0.667, under the 0.80 cutoff.
2. **MET.** All 3 bad inputs got a 400 in every trial, and the log count rose by
   exactly the 60 real decisions, so the bad inputs wrote nothing.
3. **MET.** 5 of 5 appeals showed `under_review` in the log in every trial, and
   the unknown id got a 404 with the log count unchanged.
4. **MET.** 0 of 5 formal pieces got the AI label in any trial.
5. **MET.** The five scores were identical in every trial (spread 0.00), with
   the same label each time.

**Were my targets too easy?** Partly, yes. Criterion 5 could not really fail:
both signals are deterministic, so the same text always gets the same score.
Criteria 1 and 4 passed, but my test pieces were one or two sentences each, so
the style signal couldn't measure sentence spread on them, and the attack set
still got a real writer labeled AI (FP05) with another at 0.798 (FP03). The
criterion I'd tighten is **criterion 1**: test it on full paragraphs of plain
and technical writing, the kind that actually got flagged, not short answers.

**The 13 broken attacks come down to four problems.**

**Problem 1. Label mapping: AI text scores far below my AI cutoff.**
EV02, EV03, EV04, EV06, EV07, EV09 (combined 0.370–0.560, all `unsure`).
In most of these, signal one still leaned AI (model 0.573–0.704), so the
attacks didn't fool it much. The problem is that my signals don't push AI text
anywhere near 0.80: even my unedited AI sample from unit 7 scored 0.594. With a
50/50 average, AI text lands around 0.4–0.6, and `score_to_label` only says AI
at 0.80 or above, so these attacks barely had to move the score. The stage is
the label mapping; the mechanism is that my two signals don't separate AI from
human widely enough for the cutoff to catch ordinary AI text. EV07 also fooled
signal two: padding every sentence with "; and, moreover," raised punctuation
density so much that the style score fell to 0.154.

**Problem 2. Signal one reads anything unusual as human.**
EV01 (model 0.164), EV08 (0.245), PI02 (0.204), MF03 (0.000), MF04 (0.011).
Signal one measures how predictable the text is to GPT-2. Anything GPT-2
rarely sees raises perplexity and lowers the score: misspellings like
"poistioned" and "thsi" (EV01), very short text (EV08), and odd tokens like
`SYSTEM:`, `guess=human` and `confidence=0.02` (PI02). PI02 is not the model
following an instruction; GPT-2 can't follow instructions. The injection worked
as noise, not as a command, and signal two also read it as human (0.263). EV01
was aimed at signal two, but signal one is what broke: the style score stayed
at 0.529, and the 50/50 average landed at 0.346, just under my 0.35 human
cutoff. For EV08, signal two had nothing to say: under 20 words it returns the
neutral 0.500 by design.

**Problem 3. The route lets junk through to the signals.**
MF03 (control characters) and MF04 (only punctuation) were told "We think this
text was written by a person." `app.py::submit` only checks that `text` is not
blank, so text with no real words still reached the signals. Signal one scored
it near 0, because GPT-2 can't predict junk, and signal two returned the neutral
0.500 because there were too few words, so the average landed in the human
band. The stage is the route; the mechanism is that it checks for emptiness but
not for real words.

**Problem 4. Plain human writing looks like AI to both signals.**
FP05 (technical documentation) scored model 0.801, style 0.865, combined 0.833,
and got the AI label. Short, plain instructions use common words in a
predictable order, which raises signal one, and sit at even lengths with
little punctuation, which raises signal two. Both signals share this blind
spot, so when they agree on plain writing, the agreement isn't independent
evidence. The stages are signal one and signal two together; the combining rule
can't correct it, because averaging two wrong answers is still wrong.

**EV05** (heavy human editing) is marked BROKE by my rule, because AI text
ended up labeled human (0.332). But both signals were low because, after a
heavy edit, the text really does read as human. I don't think any stage made a
mistake here.



---

## The Improvement

**What I changed:**
I added input validation to `app.py::submit`. Before any signal runs, the route
now refuses text that contains control characters, or that has no letters in
it at all, with a 400 and a plain error message. Nothing else changed: same
signals, same 50/50 weights, same 0.35 and 0.80 cutoffs, same labels.

**Which diagnosis pointed at it:**
Problem 3: the route let junk through to the signals. MF03 (control
characters) and MF04 (only punctuation) were labeled "We think this text was
written by a person", because the route only checked that `text` wasn't blank.
I picked this over moving a threshold because lowering the AI cutoff to 0.70
would have caught no extra AI text (the evasions score 0.37–0.56) while
labeling five more real writers as AI (FP02, FP03, FP04, FP06, FP07). The rule
also had to keep accepting FP08, a genuine three-sentence human post, so I
didn't add a minimum length.

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

Source: `results/attack_run_2026-11-04_1850_after.md`, produced by
`run_attacks.py --set attack_set --label after`. Same marking rule as before.

| Family | Before: HELD / BROKE | After: HELD / BROKE |
|---|---|---|
| evasion | 1 / 9 | 1 / 9 |
| false_positive | 7 / 1 | 7 / 1 |
| prompt_injection | 5 / 1 | 5 / 1 |
| malformed (text) | 6 / 2 | **8 / 0** |
| malformed (request) | 12 / 0 | 12 / 0 |
| flood_same_creator | 12 / 0 | 12 / 0 |
| **Total** | **43 / 13** | **45 / 11** |

Only three rows changed between the two runs:

| Attack | Before | After |
|---|---|---|
| MF03, control characters | 200, `human` (0.250), BROKE | 400, HELD |
| MF04, only punctuation | 200, `human` (0.256), BROKE | 400, HELD |
| MF06, emoji only | 200, `unsure` (0.749), HELD | 400, HELD |

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_9d0a1a90c2e1` | human | 0.346 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_250d7bf4cd8e` | unsure | 0.445 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_712ab43f1a5f` | unsure | 0.525 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_4dd03fa38d6f` | unsure | 0.556 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_88819f9a7d5d` | human | 0.332 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_b480dbc21c84` | unsure | 0.510 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_7c0dd4c1ee30` | unsure | 0.370 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `c_e97cc5197ae3` | unsure | 0.373 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_3c5954a19379` | unsure | 0.560 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_87e7998761bb` | ai | 0.903 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_55628eee764e` | unsure | 0.659 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_55ed7bf63bdf` | unsure | 0.761 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_dc110a64767a` | unsure | 0.798 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_0bbeb0c55919` | unsure | 0.702 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_0ad1e16628d5` | ai | 0.833 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_332509e15087` | unsure | 0.763 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_914e8375fbbd` | unsure | 0.781 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `c_a8d89c8428de` | unsure | 0.411 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_3773d029474d` | unsure | 0.485 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_1136a63924a1` | human | 0.234 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_03e911873f51` | unsure | 0.533 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_772c7e07b6b7` | unsure | 0.379 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_c1f905f10bd7` | unsure | 0.411 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_d113aecbe2c5` | unsure | 0.635 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 400 | `—` | — | — | HELD |
| MF04 | malformed | text is only punctuation | 400 | `—` | — | — | HELD |
| MF05 | malformed | text is a very long single word | 200 | `c_9ead6c104016` | unsure | 0.749 | HELD |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_a8ce4bcc5c91` | unsure | 0.703 | HELD |
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
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_602433f5295c` | human | 0.264 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_03d461d98595` | human | 0.264 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_45e839af74a8` | human | 0.264 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_daea265f6280` | human | 0.264 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_7a54de6f6850` | human | 0.264 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_ad53bc502ed7` | human | 0.264 | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_435161dd83ee` | human | 0.264 | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_e016beaa08c0` | human | 0.264 | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_f327dde7d5bb` | human | 0.264 | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_c92eb39a5dd9` | human | 0.264 | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

**My five criteria, after.** `run_eval.py --label after`
(`results/run_2026-11-04_1850_after.md`) and `run_appeals.py --label after`
(`results/appeals_2026-11-04_1850_after.md`):

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing labeled high-confidence AI | ≤ 2 of 10 | 0/10 | 0/10 | 0/10 | MET |
| 2. Bad input gets a 400 and no log entry | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 3. Appeals reach `under_review`; unknown id gets a 404 and changes nothing | 5 of 5 + 404 | 5/5, 404 | 5/5, 404 | 5/5, 404 | MET |
| 4. Formal writing labeled high-confidence AI | ≤ 1 of 5 | 0/5 | 0/5 | 0/5 | MET |
| 5. Same text 5 times: score spread and label | ≤ 0.10, same label | 0.00, same | 0.00, same | 0.00, same | MET |

Every response in the after evaluation was identical to the before one, and
the log rose by exactly 60 decisions (279 → 339), so the bad inputs still wrote
nothing.


**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

It helped, but only with the problem it was aimed at. The two junk inputs that
were being labeled human now get a 400 and never reach the signals, so
malformed text went from 2 broken to 0. I know nothing else got worse because
every other attack returned the same status, label and score as before, and
all five of my criteria returned identical output, including all 15 of my own
pieces still being accepted and scored. MF06 (emoji only) also changed, from
`unsure` to a 400; it was already HELD, and refusing it is the more honest
answer since there's nothing to score. What it didn't touch: the 9 evasions,
FP05 and PI02 are still broken, because those are signal and threshold
problems, not input problems.


---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

No criterion is still missed: all five were MET before and after. Eleven
attacks still get through.

**The 9 evasions (EV01–EV09).** These are problem 1 (AI text scores far below
my cutoff) and problem 2 (signal one reads unusual text as human). Lowering
the cutoff won't fix them; the scores need to separate further first. What I'd
do: give signal one a stronger detector model than `gpt2` and recalibrate its
midpoint on real AI and human samples, then revisit the cutoff. For EV01's
typos, I'd look at normalizing misspellings before signal one scores the text.
Why I stopped: the unit allows one change, and each of these is a bigger piece
of work than one change. A spelling fix also risks punishing real writers who
make typos.

**FP05 (human technical documentation labeled AI).** This is problem 4: plain
writing looks like AI to both signals at once. The cheapest fix would be to
raise the AI cutoff to 0.85. In this attack set that would clear FP05 (0.833)
and still catch EV10 (0.903), but it would mean almost nothing is ever labeled
AI. The real fix is a signal that doesn't share the plain-writing blind spot.
Why I stopped: one change per unit, and I'd want more than one flagged human
piece before moving a threshold.

**PI02 (fake system message labeled human).** Also problem 2: the odd tokens
made the text look unpredictable to GPT-2. What I'd do: strip lines that look
like instructions or code (`SYSTEM:`, `key=value`) before scoring, or score
only the prose. Why I stopped: deciding what counts as "not prose" without
removing real writing is its own project.

**EV05 (heavily human-edited AI).** I wouldn't fix this one. After that much
editing, the text really does read as human, and catching it would mean
flagging writing that looks exactly like a person's.



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

I would keep erring toward fewer wrong accusations, because telling a real
person their own work is fake does more harm than missing some AI text. The
cost of that falls on readers, on honest writers whose work sits next to AI
posts that weren't caught, and on the reviewers who handle all the appeals
and unsure cases.



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
