"""Where the atlas ends.

The corpus stops at the Constitution of 11 June 1975. The map stops moving in 1947 and
its only later change is Cyprus's independence in 1960; the arcs the corpus follows
close with the fall of the junta and the constitution that replaced everything it had
enacted. What came after is archived under ``content/archive/after-1975/`` and not
loaded.

The end is named here rather than derived from the last event, because it is an
editorial decision, not a fact about the data: deriving it would let one stray entry
quietly stretch the timeline by fifty years. Half-open like every other period in the
corpus, and out to the start of the next year so the last event is not pinned to the
very end of the track with nowhere to scrub past it.
"""

from datetime import date

SCOPE_END = date(1976, 1, 1)
