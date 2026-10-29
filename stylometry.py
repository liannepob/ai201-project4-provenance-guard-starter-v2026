"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics

import config


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies. ← TODO

    Returns:
        A float. Decide yourself what scale it's on and which direction means
        "more human" — then write that down, because your combining rule
        depends on knowing it.

    A hint on what you're reaching for: the standard deviation of sentence
    lengths, probably divided by the mean so a long text and a short one are
    comparable. `statistics.stdev` is imported for you.

    Watch the edge case: a one-sentence submission has no spread at all, and
    `stdev` raises on fewer than two values. Decide what that should return
    before the attack set decides for you.

    Mine: the standard deviation of words per sentence, in words. Higher means
    more human. Fewer than two sentences returns 0.0 — but `style_signal`
    treats that case as neutral rather than reading 0.0 as "perfectly even".
    """
    lengths = [len(words(s)) for s in sentences(text)]
    if len(lengths) < 2:
        return 0.0
    return statistics.stdev(lengths)


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words. ← TODO

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length. ← TODO

    Returns:
        A float. Whether you count all punctuation or only some kinds — commas,
        semicolons, dashes — is a real choice. Semicolons and em dashes are
        more interesting than full stops, because they vary more between
        writers.

    Mine: every punctuation mark counts (full stops, commas, dashes, quotes,
    brackets) except apostrophes, which come from contractions and possessives
    rather than style. Higher means more human. No words returns 0.0.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    marks = re.findall(r"[^\w\s'’]", text)
    return len(marks) / len(tokens)


# ── Scaling ──────────────────────────────────────────────────────────────────

def _scale(value: float, ai_end: float, human_end: float) -> float:
    """
    Clamped straight line: `ai_end` or beyond -> 1.0, `human_end` or beyond
    -> 0.0, linear in between. The anchors live in config.py.
    """
    score = (human_end - value) / (human_end - ai_end)
    return min(max(score, 0.0), 1.0)


def scaled_measures(text: str) -> dict:
    """
    Each measure on 0–1, higher = more likely AI. A measure that can't be
    taken on this text is None. Split out from `style_signal` so the terminal
    can print the pieces.
    """
    if len(words(text)) < config.STYLE_MIN_WORDS:
        return {"spread": None, "variety": None, "punctuation": None}

    spread = None
    if len(sentences(text)) >= 2:
        spread = _scale(sentence_length_spread(text),
                        config.SPREAD_AI, config.SPREAD_HUMAN)

    return {
        "spread": spread,
        "variety": _scale(type_token_ratio(text), config.TTR_AI, config.TTR_HUMAN),
        "punctuation": _scale(punctuation_density(text),
                              config.PUNCT_AI, config.PUNCT_HUMAN),
    }


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.** ← TODO

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.

    Mine: the plain average of whichever scaled measures could be taken. Text
    under STYLE_MIN_WORDS words gets STYLE_NEUTRAL, because the measures are
    noise at that length and noise shouldn't count against a writer.
    """
    taken = [v for v in scaled_measures(text).values() if v is not None]
    if not taken:
        return config.STYLE_NEUTRAL
    return round(sum(taken) / len(taken), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    def show(value):
        return "n/a" if value is None else f"{value:.4f}"

    scaled = scaled_measures(text)

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"{'measure':<24} {'raw':>8}   {'scaled (1 = AI)':>15}")
    print(f"{'sentence_length_spread':<24} {sentence_length_spread(text):>8.4f}   {show(scaled['spread']):>15}")
    print(f"{'type_token_ratio':<24} {type_token_ratio(text):>8.4f}   {show(scaled['variety']):>15}")
    print(f"{'punctuation_density':<24} {punctuation_density(text):>8.4f}   {show(scaled['punctuation']):>15}")
    print(f"\nstyle_signal             {style_signal(text)}   (higher = more likely AI)")
    if len(words(text)) < config.STYLE_MIN_WORDS:
        print(f"(under {config.STYLE_MIN_WORDS} words — returned the neutral score)")
