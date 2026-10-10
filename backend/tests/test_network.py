from app.modules.network import crud


def test_shared_events_are_counted_once_per_event(corpus):
    shared = crud.shared_events(corpus)
    pair = ("constantine-i", "venizelos")
    assert len(shared[pair]) == 9
    assert len({e.id for e in shared[pair]}) == 9


def test_every_figure_is_a_node_and_no_edge_dangles(corpus):
    g = crud.figure_graph(corpus)
    ids = {n["id"] for n in g["nodes"]}
    assert ids == {f.id for f in corpus.figures}
    for e in g["edges"]:
        assert e["source"] < e["target"], "one edge per unordered pair"
        assert {e["source"], e["target"]} <= ids
        assert e["events"] or e["relations"], "an edge needs a reason"


def test_a_tie_without_a_shared_event_is_still_an_edge(corpus):
    """Tsaldaris and his nephew never stand on one event; the tie is the edge."""
    g = crud.figure_graph(corpus)
    edge = next(
        e
        for e in g["edges"]
        if (e["source"], e["target"]) == ("tsaldaris-konstantinos", "tsaldaris-panagis")
    )
    assert edge["events"] == []
    assert edge["relations"][0]["kind"] == "kin"


def test_betweenness_on_a_path():
    """On a -- b -- c every shortest path runs through b and none through the ends."""
    score = crud.betweenness(["a", "b", "c"], {("a", "b"), ("b", "c")})
    assert score == {"a": 0.0, "b": 1.0, "c": 0.0}


def test_bridges_are_not_simply_the_busiest(corpus):
    """The point of the measure: who connects eras is a different question from
    who appears most. Venizelos leads by events; he does not lead by betweenness."""
    g = crud.figure_graph(corpus)
    by_events = max(g["nodes"], key=lambda n: len(n["events"]))["id"]
    by_bridging = max(g["nodes"], key=lambda n: n["betweenness"])["id"]
    assert by_events == "venizelos"
    assert by_bridging != by_events


def test_connections_describe_the_other_figure(corpus):
    conns = {c["id"]: c for c in crud.connections_of(corpus, "george-i")}
    assert conns["constantine-i"]["relations"] == [{"kind": "child", "note": None}]
    assert len(conns["constantine-i"]["events"]) == 5
    # strongest first
    assert [c["id"] for c in crud.connections_of(corpus, "george-i")][0] == "constantine-i"


def test_network_route_and_figure_detail(client):
    body = client.get("/api/network/figures").json()
    assert len(body["nodes"]) == 78
    assert {"id", "polity", "events", "degree", "betweenness"} <= body["nodes"][0].keys()
    kemal = next(n for n in body["nodes"] if n["id"] == "kemal")
    assert kemal["polity"] == "turkey"
    detail = client.get("/api/figures/venizelos").json()
    assert detail["connections"][0]["id"] == "constantine-i"
    assert detail["polity"] is None
