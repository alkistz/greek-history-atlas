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

    odd = []
    for e in c.events:
        for field in ("summary", "body"):
            t = getattr(e, field)
            if t is None or t.el is None:
                continue
            only_en, only_el = digits(t.en) - digits(t.el), digits(t.el) - digits(t.en)
            if only_en or only_el:
                odd.append(
                    f"  event {e.id!r} {field}: en-only {sorted(only_en)} el-only {sorted(only_el)}"
                )
        if e.body and e.body.el and paragraphs(e.body.en) != paragraphs(e.body.el):
            odd.append(
                f"  event {e.id!r} body: {paragraphs(e.body.en)} paragraphs in en, "
                f"{paragraphs(e.body.el)} in el"
            )
    print(f"\nparity anomalies ({len(odd)}) -- advisory, expect false positives")
    for line in odd[:25]:
        print(line)
    if len(odd) > 25:
        print(f"  ... and {len(odd) - 25} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
