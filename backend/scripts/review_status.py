"""What has been reviewed, what has gone stale, and what does not line up.

Three questions, one report:

  reviewed   -- how much of the corpus either pass has reached
  stale      -- entries edited after they were reviewed, so the record now lies
  parity     -- entries whose English and Greek do not carry the same numbers

Staleness comes from git rather than from a digest stored in the file. A stored
hash has to be written back by tooling, is self-referential, and invites hand
editing; git already knows when a file last changed and needs no new field. Its
one weakness is that a whitespace-only commit marks an entry stale, which fails
in the safe direction.

Entries that share a file -- instruments -- can only be stale at file level.

Parity is advisory, not a rule. The two texts are translations of one another, so
the numbers in them should match, but a figure written in words in one language
and digits in the other is a false positive rather than an error. Run `make check`
for the rules; run this to decide where to look next.
"""

import re
import subprocess
import sys
from datetime import date

from app.core.content import load
from app.core.paths import CONTENT, EVENTS_DIR, FIGURES_DIR, INSTRUMENTS_YAML

# A number in either language. Greek groups with '.' and Greek decimals use ',',
# English the reverse, so separators are stripped before comparing.
NUMBER = re.compile(r"\d[\d.,]*\d|\d")


def digits(text: str | None) -> set[str]:
    """Every number in a text, as bare digit strings.

    Digits only, deliberately. Reading English number words too was tried and
    abandoned: English prose uses "one", "first" and "a second" as words rather
    than as quantities, so it invented a mismatch on almost every entry. The
    residue is that "on the twenty-third" against "στις 23" still reports, which
    is a handful of known false positives rather than a flood of them.
    """
    if not text:
        return set()
    return {
        m.group().replace(".", "").replace(",", "").lstrip("0") or "0"
        for m in NUMBER.finditer(text)
    }


def last_commit(path) -> date | None:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", str(path)],
        capture_output=True,
        text=True,
        cwd=CONTENT.parent,
    ).stdout.strip()
    return date.fromisoformat(out) if out else None


def paragraphs(text: str | None) -> int:
    return len([p for p in (text or "").split("\n\n") if p.strip()])


def main() -> int:
    c = load()
    groups = [
        ("events", c.events, lambda e: EVENTS_DIR / f"{e.id}.yaml"),
        ("figures", c.figures, lambda f: FIGURES_DIR / f"{f.id}.yaml"),
        ("instruments", c.instruments, lambda i: INSTRUMENTS_YAML),
    ]

    print("reviewed")
    for label, items, _ in groups:
        auto = sum(1 for x in items if x.review and x.review.auto)
        manual = sum(1 for x in items if x.review and x.review.manual)
        print(f"  {label:12} {auto:4} auto   {manual:4} manual   of {len(items)}")

    stale = []
    for label, items, path_of in groups:
        for x in items:
            if not x.review:
                continue
            changed = last_commit(path_of(x))
            if changed is None:
                continue
            for track in ("auto", "manual"):
                p = getattr(x.review, track)
                if p is not None and changed > p.date:
                    stale.append(
                        f"  {label[:-1]} {x.id!r}: {track} pass {p.date}, edited {changed}"
                    )
    print(f"\nstale ({len(stale)})")
    for line in stale[:20]:
        print(line)

    # Two tiers, because the two kinds of difference are worth very different
    # amounts. A number missing from BOTH sides is a substitution: each language
    # carries a different figure for the same thing, which is how the two Old
    # Style / New Style splits were found. A one-sided difference is nearly always
    # English spelling a number that Greek writes in digits.
    swapped, one_sided = [], []
    kinds = (("event", c.events), ("figure", c.figures), ("instrument", c.instruments))
    for label, items in kinds:
        for x in items:
            for field in ("summary", "body"):
                t = getattr(x, field, None)
                if t is None or t.el is None:
                    continue
                only_en, only_el = digits(t.en) - digits(t.el), digits(t.el) - digits(t.en)
                if not (only_en or only_el):
                    continue
                line = (
                    f"  {label} {x.id!r} {field}: "
                    f"en-only {sorted(only_en)} el-only {sorted(only_el)}"
                )
                (swapped if (only_en and only_el) else one_sided).append(line)
            body = getattr(x, "body", None)
            if body and body.el and paragraphs(body.en) != paragraphs(body.el):
                swapped.append(
                    f"  {label} {x.id!r} body: {paragraphs(body.en)} paragraphs in en, "
                    f"{paragraphs(body.el)} in el"
                )

    print(f"\nmismatched ({len(swapped)}) -- each language carries a different figure")
    for line in swapped:
        print(line)
    print(f"\none-sided ({len(one_sided)}) -- usually English spelling what Greek digits")
    for line in one_sided:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
