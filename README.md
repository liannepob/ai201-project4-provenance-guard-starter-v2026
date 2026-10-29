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
2. **The input is checked.** `text` must be a non-empty string and
   `creator_id` must be present. If either is wrong, the route stops here and
   returns a 400, and the rejection is written to the log
   (`audit.log_rejection`). *Adds:* a guarantee that everything below gets real
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
(`stylometry.py::style_signal`). It will use three measures:
- **Sentence length spread:** the standard deviation of sentence lengths
  divided by the mean.
- **Type-token ratio:** unique words over total words.
- **Punctuation density:** especially the more personal marks (semicolons,
  dashes, colons, parentheses).

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
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

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
  -d '{"text": "...", "creator_id": "..."}'
```

```json

```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json

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

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



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
