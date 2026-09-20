"""Rules for the two review tracks, shared by every entry that carries prose."""

from __future__ import annotations

from app.core.models import LangText, Review


def langs_present(*texts: LangText | None) -> set[str]:
    """The languages an entry is actually written in.

    Greek is optional on the model, so a pass that read only English is complete
    for an entry that has only English and incomplete for one that has both.
    """
    langs = {"en"}
    if any(t is not None and t.el is not None for t in texts):
        langs.add("el")
    return langs


def check_review(review: Review | None, present: set[str], owner: str) -> list[str]:
    """What a recorded pass has to say to be worth recording.

    The two texts are translations of one another, so a fact wrong in one is wrong
    in both. `clean` therefore means "every language this entry has was read and
    they agree" -- a pass over English alone cannot conclude it.
    """
    if review is None:
        return []

    problems: list[str] = []
    for track in ("auto", "manual"):
        p = getattr(review, track)
        if p is None:
            continue
        at = f"{owner}: review.{track}"

        if p.result == "unresolved" and not p.note:
            problems.append(f"{at}: 'unresolved' needs a note saying what could not be settled")
        if track == "manual" and not p.by:
            problems.append(f"{at}: a manual pass records who made it")
        if p.result == "clean":
            missing = present - set(p.langs)
            if missing:
                problems.append(
                    f"{at}: cannot be 'clean' without reading {', '.join(sorted(missing))}; "
                    "the two texts say the same thing, so one of them is not a sample"
                )
    return problems
