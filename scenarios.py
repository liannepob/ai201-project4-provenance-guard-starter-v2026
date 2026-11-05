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
            "Last weekend I was with friends and I went around the city.",
            "To make bubble tea first I would boil some water for the pearls and then I would make the tea with some drink mix and then I will add ice and then combine them together.",
            "When something went wrong I first took a step back and addressed the situation and then came up with different types of solutions that would work for this situation and then decided on what i was going to do.",
            "My favorite place to be at is my bed room with some privacy and being able to sleep, get work done, and eat in the same place.",
            "In my opinion the new Spiderman movie was really good just really long I thought that it was very entertaining but I was not expecting it to be that long.",
            'I would let a friend know in this way, "Hey im running late right now, I will let you know once im 5 minutes out."',
            "I first wake up, brush teeth and then make bed, do skincare, change, and then leave room to get breakfast then go study or go class",
            "Right now in Calculus 3 we are learning about double integrals which is partial integration, you first integrate with respect to d value closest to the equation and then continue to the last d value and then you simplify and get the solution",
            "Someone who influenced me was a family member they push me to work hard each day, but also have a good balance with work and not overowkr myself since a good work life balance is real worth",
            "I want to push my web application to the app store by learning swift and then adding a gemini api key into it and create real revenue from users",
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
            "I am a sophmore in college and I am studying Computer Science, I want to work for your company to use my technical skills form school and personal projects in a corprate work setting with others. I have proficency in SQL, python, CSS, HTML, Javascript and Java. Thank you for your consideration.",
            "Dear Professor Bob, I was wondering If I was able to reschedule time for me to take Quiz 4 as I have a family event I need to attend.",
            "I created a website/web application for individuals with food allergies to dine out safely by tracking different places to eat at, and track their allergies on the websie. I used CSS, HTML, Python, SQL, GooglePlaces API, SendGrid API, and JSON to complete this.",
            "I agree that AI should not be used when first learning about a subject like computer science fundumentals since it can taint the understanding of computer science at an early stage making you think that you understand the topic when you dont acutally. I think it is best saved for people who have been in the industry or students alreayd proficicient in coding.",
            "To whom it may concern, I ordered 10 Piece cooking pot and it only came with 9 pieces, I would like a partial refund or an exchange of this product if possible. Best",
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
