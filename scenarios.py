"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

# Criterion 5 sends this one text five times. It's the lightly-edited AI
# sample from unit 7 (samples/borderline.json), which scores in the unsure band.
_REPEATED_TEXT = (
    "Time management matters more than people admit, especially now that work "
    "moves as fast as it does. If you're organised you hit deadlines, and you're "
    "less frazzled doing it. A few things actually help. Prioritise — work out "
    "what genuinely matters and do that first. Cut the interruptions; "
    "notifications wreck focus and the damage is worse than it feels at the "
    "time. And take breaks, short ones, often."
)

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # ⚠️ PUT YOUR OWN WRITING HERE. Not AI text, not a sample from the web —
        # things you actually wrote. This is the criterion that matters most and
        # it's meaningless with someone else's prose.
        "texts": [
            "REPLACE ME with a paragraph you wrote yourself.",
            "REPLACE ME with another one. Ten pieces is the usual number.",
        ],
    },
    {
        "name": "bad input",
        "criterion": 2,
        # Target: every one of these gets a 400 with a JSON error, and none of
        # them adds a line to the audit log (compare GET /health's log_entries
        # before and after the run).
        "bodies": [
            {"creator_id": "eval_bad_missing"},                  # no text field
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": "x" * 10_001, "creator_id": "eval_bad_huge"},  # one over the cap
        ],
    },
    # Criterion 3, appeals, needs a submission and then an appeal against the
    # content_id that came back, which this file can't express. It runs from
    # run_appeals.py instead: python run_appeals.py --label before
    {
        "name": "formal human writing",
        "criterion": 4,
        # ⚠️ Five formal pieces YOU wrote — a cover letter, a report, an essay.
        # Separate from the ten above.
        "texts": [
            "REPLACE ME with a formal piece you wrote yourself.",
        ],
    },
    {
        "name": "same text five times",
        "criterion": 5,
        # Target: within each trial, the five combined scores are within 0.10 of
        # each other and all five get the same label.
        "texts": [_REPEATED_TEXT] * 5,
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
