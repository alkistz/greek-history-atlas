"""The four routes the frontend depends on, plus the event detail route."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_atoms_is_a_feature_collection(client):
    body = client.get("/api/atoms").json()
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 19


def test_meta_has_epochs_and_polities(client):
    body = client.get("/api/meta").json()
    assert body["epochs"][0] == "1821-01-01"
    assert {p["id"] for p in body["polities"]} >= {"ottoman", "gr-kingdom"}


def test_control_rows_use_yaml_aliases(client):
    row = client.get("/api/control").json()[0]
    assert {"atom", "polity", "kind", "from", "to"} <= row.keys()


def test_events_are_sorted(client):
    starts = [e["period"][0] for e in client.get("/api/events").json()]
    assert starts == sorted(starts)


def test_event_detail_and_404(client):
    assert client.get("/api/events/revolution-outbreak").json()["id"] == "revolution-outbreak"
    assert client.get("/api/events/nope").status_code == 404
