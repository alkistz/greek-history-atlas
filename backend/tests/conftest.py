"""Shared fixtures. The corpus loads once per session; tests that want a broken
corpus use `dataclasses.replace` so new Corpus fields never break old tests."""

import pytest
from fastapi.testclient import TestClient

from app.core.content import load
from app.main import app


@pytest.fixture(scope="session")
def corpus():
    return load()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def swap(items, replacement):
    """The list with the item of the same id replaced. For building broken corpora."""
    return [replacement if it.id == replacement.id else it for it in items]
