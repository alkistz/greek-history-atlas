"""One request per route, checking shape rather than content."""


def test_atoms_is_a_feature_collection(client):
    body = client.get("/api/atoms").json()
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 25
    assert {f["properties"]["external"] for f in body["features"]} == {True, False}


def test_context_is_one_land_feature(client):
    body = client.get("/api/context").json()
    assert [f["id"] for f in body["features"]] == ["land"]
    assert body["features"][0]["geometry"]["type"] in ("Polygon", "MultiPolygon")


def test_meta_has_epochs_and_polities(client):
    body = client.get("/api/meta").json()
    assert body["epochs"][0] == "1821-01-01"
    assert {p["id"] for p in body["polities"]} >= {"ottoman", "gr-kingdom"}


def test_control_rows_use_yaml_aliases(client):
    row = client.get("/api/control").json()[0]
    assert {"atom", "polity", "kind", "from", "to"} <= row.keys()


def test_events_list_is_sorted_and_lean(client):
    events = client.get("/api/events").json()
    starts = [e["period"][0] for e in events]
    assert starts == sorted(starts)
    assert "body_html" not in events[0]
    assert "frame" in events[0]


def test_event_detail_resolves_links(client):
    body = client.get("/api/events/battle-of-navarino").json()
    assert body["body_html"]["en"].startswith("<p>")
    assert "body" not in body
    assert {f["id"] for f in body["figures"]} == {"codrington", "ibrahim-pasha"}
    assert body["place"]["name"]["en"] == "Navarino Bay"
    assert body["sources"][0]["author"]
    assert client.get("/api/events/nope").status_code == 404


def test_event_detail_names_places_as_of_the_date(client):
    body = client.get("/api/events/treaty-of-constantinople-1832").json()
    assert body["place"]["name"]["en"] == "Constantinople"
    assert body["instrument"]["id"] == "constantinople-1832"


def test_figures_list_and_detail(client):
    listed = client.get("/api/figures").json()
    assert "body_html" not in listed[0]
    detail = client.get("/api/figures/venizelos").json()
    ids = [e["id"] for e in detail["events"]]
    assert {"treaty-of-bucharest-1913", "treaty-of-lausanne-1923"} <= set(ids)
    assert [e["period"][0] for e in detail["events"]] == sorted(
        e["period"][0] for e in detail["events"]
    )
    assert detail["born"]["place"]["name"]["en"] == "Mournies"
    assert client.get("/api/figures/nope").status_code == 404


def test_instruments_places_sources(client):
    inst = client.get("/api/instruments/bucharest-1913").json()
    assert len(inst["control"]) == 5
    assert inst["events"][0]["id"] == "treaty-of-bucharest-1913"
    assert client.get("/api/instruments/nope").status_code == 404
    assert any(p["id"] == "smyrna" for p in client.get("/api/places").json())
    assert any(s["id"] == "clogg-2021" for s in client.get("/api/sources").json())
