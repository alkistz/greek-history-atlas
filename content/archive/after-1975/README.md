# After 1975: archived, not published

The atlas ends with the Constitution of 11 June 1975. Everything in this folder was in
the corpus before that cut, and none of it is loaded: the backend reads
`content/events/` and `content/figures/` and the top-level YAML files, never anything
under `content/archive/`. It is kept so that a later "after 1975" section can start
from written, reviewed entries rather than from nothing.

## Why 1975

The map stops moving in 1947, and its only later change is Cyprus's independence in
1960. The corpus's own arcs close in 1974–75: the junta falls, the monarchy is voted out,
and the 1975 constitution settles what the state is. After that the timeline would give
a quarter of its width to a static map and nine scattered events.

## What is here

| file | entries |
|---|---|
| `events/` | `ec-accession-1981`, `pasok-first-government-1981`, `imia-crisis-1996`, `euro-adoption-2001`, `athens-olympics-2004`, `first-memorandum-2010`, `bailout-referendum-2015`, `prespa-agreement-2018`, `tempi-disaster-2023` |
| `figures/` | `simitis`, `papandreou-giorgos`, `tsipras`, `mitsotakis-kyriakos`: the four people who appear only in those events |
| `instruments.yaml` | `accession-1979`, `prespa-2018` |
| `places.yaml` | `brussels`, `psarades`, `imia`, `tempi`: places used only by those events |
| `sources.yaml` | `siani-davies-2017`: the one work cited only by those entries |
| `threads.yaml` | the five threads that ran past 1975, as they stood before the cut |
| `relations.yaml` | the three ties that name an archived figure, moved here when the figure network was merged |

Figures who also appear before 1975, such as Andreas Papandreou and Konstantinos
Karamanlis, stayed in the corpus. Their archived appearances are recorded only in the
archived events' `figures` lists.

## Restoring an entry

1. Move the file back into `content/events/` or `content/figures/`, and the matching
   blocks from `instruments.yaml`, `places.yaml`, `sources.yaml` and `relations.yaml` back
   into the top-level files.
2. Put the event back in its threads, taking the summary from `threads.yaml` here if
   the thread's ending changes with it.
3. Raise `SCOPE_END` in `backend/app/core/scope.py`. Validation refuses any event or
   instrument dated on or after it, so step 1 alone fails at load time.
4. `make check`.

The review blocks are as they were on 20 September 2026. Anything restored is stale
against its sources by however long it has sat here, and needs a fresh pass.
