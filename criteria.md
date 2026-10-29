# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---

## 1. Human writing is rarely flagged as AI

Of 10 pieces of writing I can show are human, at most 2 get the high-confidence AI label, in each of the three trials.

**Why this target:**
Wrongly telling a real writer their work is AI-generated is the most expensive mistake this system can make, because it accuses someone of cheating on something they wrote themselves. Missing some AI text costs the site very little by comparison. I set the limit at 2 of 10 instead of 1 because the detector model can score differently between runs, but I keep it low because a false accusation is the costliest error. I'd rather have uncertain text land in the "unsure" label than risk an accusation.

---

## 2. Bad input returns a clean error

When `text` is missing, empty, or longer than 10,000 characters, `POST /submit` returns a 400 status with a JSON error message, and the service keeps running and does not write an entry to the log.

**Why this target:**
Bad input shouldn't be able to break the service or slip through as a real submission. Capping the length keeps one huge request from overloading the model and slowing things down for everyone. Rejecting empty or missing text stops the code from failing when it tries to read from a string that isn't there. It also keeps junk entries out of the log, so every score the system gives comes from text it can actually judge.

---

## 3. Appeals always work

For 5 appeals sent with a valid `content_id`, all 5 change the item's status to `under_review` and show up in `GET /log`. An appeal with an unknown `content_id` returns a 404 and changes nothing.

**Why this target:**
A writer who appeals and hears nothing back has no way to fix a wrong decision, so the appeal path has to work every time. Failing quietly on a bad ID would also hide real problems from me, so it needs a clear error.

---

## 4. Formal human writing is not flagged as AI

Of 5 formal pieces I can show are human (such as a research paper or a cover letter), at most 1 gets the high-confidence AI label, in each of the three trials. These 5 pieces are separate from the 10 in criterion 1.

**Why this target:**
Human writing with clean grammar and consistent punctuation can look AI-like to the detector, and a writer should not be accused of cheating just because their style is formal. This is the hardest case for my system, so I'm testing it on its own instead of letting it hide inside the general false positive average. I'm holding it to the same rate as my overall limit because a wrongful accusation costs a writer the same no matter how formal their writing is.

---

## 5. Same text gets the same result

Submitting the same text 5 times produces combined scores within 0.10 of each other (highest minus lowest), and the same label all 5 times, in each of the three trials.

**Why this target:**
A writer's result shouldn't depend on when they happened to submit. If the score drifts between runs, the same piece could be called human one time and AI the next, and the person who gets the AI label has been accused for no real reason. I allow a small amount of variation because the detector model can score slightly differently between runs, but not enough to change the label.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->