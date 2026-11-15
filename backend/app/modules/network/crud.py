"""The figure network: who stood in the same event as whom, and why.

Nothing here is authored. Participations are written on events and ties in
relations.yaml; this folds both into one graph over figures, so the frontend
draws from a single payload and the same numbers appear on every page.

The analysis is deliberately modest: shared-event counts, degree and
betweenness. All three measure the corpus as written -- Venizelos leads because
the editor listed him twenty-six times -- so they describe this atlas's shape,
not Greek history's, and the page says so.
"""

from collections import defaultdict, deque
from typing import Any

from app.core.content import Corpus
from app.modules.relations.models import Relation

Pair = tuple[str, str]


def _pair(a: str, b: str) -> Pair:
    return (a, b) if a < b else (b, a)


def shared_events(corpus: Corpus) -> dict[Pair, list[Any]]:
    """Every pair of figures on one event, with the events they share, by date."""
    out: dict[Pair, list[Any]] = defaultdict(list)
    for e in sorted(corpus.events, key=lambda e: (e.period[0], e.id)):
        figures = sorted({p.figure for p in e.figures})
        for i, a in enumerate(figures):
            for b in figures[i + 1 :]:
                out[_pair(a, b)].append(e)
    return out


def ties(corpus: Corpus) -> dict[Pair, list[Relation]]:
    out: dict[Pair, list[Relation]] = defaultdict(list)
    for r in corpus.relations:
        out[r.pair()].append(r)
    return out


def betweenness(nodes: list[str], edges: set[Pair]) -> dict[str, float]:
    """Brandes' betweenness on an unweighted, undirected graph, normalised to
    [0, 1]. Seventy-eight nodes: the cost is nothing, and the number is the one
    that says who bridges otherwise separate parts of the corpus, which a count
    of events cannot."""
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    score = dict.fromkeys(nodes, 0.0)
    for s in nodes:
        stack: list[str] = []
        preds: dict[str, list[str]] = {n: [] for n in nodes}
        sigma = dict.fromkeys(nodes, 0)
        sigma[s] = 1
        dist = dict.fromkeys(nodes, -1)
        dist[s] = 0
        queue = deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in adj[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    preds[w].append(v)
        delta = dict.fromkeys(nodes, 0.0)
        while stack:
            w = stack.pop()
            for v in preds[w]:
                delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
            if w != s:
                score[w] += delta[w]

    # Undirected, so every path was found from both ends: halve, then divide by
    # the number of pairs a node could sit between.
    n = len(nodes)
    scale = 1 / ((n - 1) * (n - 2)) if n > 2 else 0.0
    return {k: round(v * scale, 4) for k, v in score.items()}


def _event_ref(e) -> dict[str, Any]:
    return {"id": e.id, "date": e.period[0].isoformat()}


def figure_graph(corpus: Corpus) -> dict[str, Any]:
    """Nodes are every figure; an edge is a pair that shares an event or a tie."""
    shared = shared_events(corpus)
    tied = ties(corpus)
    pairs = sorted(set(shared) | set(tied))
    node_ids = [f.id for f in corpus.figures]
    between = betweenness(node_ids, set(pairs))
    degree: dict[str, int] = defaultdict(int)
    for a, b in pairs:
        degree[a] += 1
        degree[b] += 1

    own: dict[str, list[Any]] = defaultdict(list)
    for e in sorted(corpus.events, key=lambda e: (e.period[0], e.id)):
        for p in e.figures:
            own[p.figure].append(e)

    nodes = [
        {
            "id": f.id,
            "name": f.name.model_dump(mode="json"),
            "roles": f.roles,
            "polity": f.polity,
            "born": f.born.date.isoformat() if f.born else None,
            "died": f.died.date.isoformat() if f.died else None,
            "events": [_event_ref(e) for e in own[f.id]],
            "degree": degree[f.id],
            "betweenness": between[f.id],
        }
        for f in corpus.figures
    ]
    edges = [
        {
            "source": a,
            "target": b,
            "events": [_event_ref(e) for e in shared.get((a, b), [])],
            # As written: `from` is the kind of `to`. The frontend turns it round.
            "relations": [r.model_dump(mode="json", by_alias=True) for r in tied.get((a, b), [])],
        }
        for a, b in pairs
    ]
    return {"nodes": nodes, "edges": edges}


def connections_of(corpus: Corpus, figure_id: str) -> list[dict[str, Any]]:
    """One figure's neighbourhood, for the figure page: who they shared events
    with and what each is to them, strongest first."""
    from app.modules.relations.crud import relations_of

    names = {f.id: f.name for f in corpus.figures}
    shared = shared_events(corpus)
    by_other: dict[str, dict[str, Any]] = {}

    def entry(other: str) -> dict[str, Any]:
        return by_other.setdefault(
            other,
            {
                "id": other,
                "name": names[other].model_dump(mode="json"),
                "events": [],
                "relations": [],
            },
        )

    for (a, b), events in shared.items():
        if figure_id not in (a, b):
            continue
        other = b if a == figure_id else a
        entry(other)["events"] = [e.id for e in events]
    for other, kind, row in relations_of(corpus, figure_id):
        entry(other)["relations"].append(
            {"kind": kind, "note": row.note.model_dump(mode="json") if row.note else None}
        )

    return sorted(
        by_other.values(),
        key=lambda c: (-len(c["events"]), -len(c["relations"]), c["name"]["en"]),
    )
