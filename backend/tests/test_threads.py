from dataclasses import replace

from conftest import swap

from app.core.content import validate
from app.modules.events import crud as events
from app.modules.threads import crud


def test_every_thread_event_exists(corpus):
    known = {e.id for e in corpus.events}
    for thread in corpus.threads:
        assert set(thread.events) <= known, f"{thread.id} points at events that do not exist"


def test_reading_order_is_chronological(corpus):
    """The YAML list is a set; order is derived, so it cannot contradict the timeline."""
    for thread in corpus.threads:
        dates = [e.period[0] for e in crud.events_of(corpus, thread)]
        assert dates == sorted(dates), f"{thread.id} is out of order"


def test_threads_may_overlap(corpus):
    """1922 belongs to three arcs at once. That is the point, not a duplication."""
    arcs = {t.id for t in crud.threads_of(corpus, "burning-of-smyrna")}
    assert {"great-idea", "asia-minor-catastrophe"} <= arcs


def test_neighbours_walk_the_arc(corpus):
    thread = crud.get_thread(corpus, "asia-minor-catastrophe")
    previous, following = crud.neighbours(corpus, thread, "burning-of-smyrna")
    assert previous.id == "turkish-great-offensive-1922"
    assert following.id == "revolution-1922-trial-of-the-six"


def test_the_ends_of_an_arc_have_one_neighbour(corpus):
    thread = crud.get_thread(corpus, "war-of-independence")
    ordered = crud.events_of(corpus, thread)
    assert crud.neighbours(corpus, thread, ordered[0].id)[0] is None
    assert crud.neighbours(corpus, thread, ordered[-1].id)[1] is None


def test_threads_fix_the_dead_ends(corpus):
    """Why this file exists. `related` is "same atom within two years", which finds
    nothing for most of a corpus that is two thirds post-1900 and a third in Athens."""
    by_proximity = [e for e in corpus.events if events.related(corpus, e)]
    by_arc = [e for e in corpus.events if crud.threads_of(corpus, e.id)]
    assert len(by_proximity) < len(corpus.events) * 0.5
    assert len(by_arc) > len(corpus.events) * 0.9


def test_an_unknown_event_is_rejected(corpus):
    thread = crud.get_thread(corpus, "cyprus-question")
    bad = thread.model_validate({**thread.model_dump(), "events": [*thread.events, "atlantis"]})
    problems = validate(replace(corpus, threads=swap(corpus.threads, bad)))
    assert any("unknown event 'atlantis'" in p for p in problems)


def test_a_repeated_event_is_rejected(corpus):
    thread = crud.get_thread(corpus, "cyprus-question")
    bad = thread.model_validate(
        {**thread.model_dump(), "events": [*thread.events, "eoka-campaign-begins"]}
    )
    problems = validate(replace(corpus, threads=swap(corpus.threads, bad)))
    assert any("'eoka-campaign-begins' listed 2 times" in p for p in problems)


def test_threads_index(client):
    body = client.get("/api/threads").json()
    assert len(body) == 19
    independence = next(t for t in body if t["id"] == "war-of-independence")
    assert independence["count"] == 9
    assert independence["span"] == ["1821-04-06", "1833-02-06"]
    # Ids, in reading order, but not the events themselves: enough to filter a
    # ledger by arc in one request, without carrying 127 titles to do it.
    assert independence["events"][0] == "revolution-outbreak"
    assert len(independence["events"]) == independence["count"]
    assert all(isinstance(i, str) for i in independence["events"])


def test_thread_detail(client):
    body = client.get("/api/threads/cyprus-question").json()
    ids = [e["id"] for e in body["events"]]
    assert ids[0] == "greek-appeal-to-the-un-on-cyprus"
    assert ids[-1] == "turkish-invasion-of-cyprus-1974"
    assert body["name"]["el"] == "Το Κυπριακό"
    assert client.get("/api/threads/nope").status_code == 404


def test_event_detail_carries_its_arcs(client):
    body = client.get("/api/events/burning-of-smyrna").json()
    arcs = {t["id"]: t for t in body["threads"]}
    assert "asia-minor-catastrophe" in arcs
    assert arcs["asia-minor-catastrophe"]["next"]["id"] == "revolution-1922-trial-of-the-six"
    assert arcs["asia-minor-catastrophe"]["previous"]["id"] == "turkish-great-offensive-1922"


def test_an_event_that_opens_an_arc_has_no_previous(client):
    body = client.get("/api/events/revolution-outbreak").json()
    arc = next(t for t in body["threads"] if t["id"] == "war-of-independence")
    assert arc["previous"] is None
    assert arc["next"]["id"] == "fall-of-tripolitsa"
