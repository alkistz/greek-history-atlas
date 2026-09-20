from dataclasses import replace

from conftest import swap

from app.core.content import validate
from app.modules.figures import crud
from app.modules.figures.validate import lifetime_warnings


def test_figures_link_back_to_their_events(corpus):
    events = crud.events_of(corpus, "kolokotronis")
    assert [(e.id, role) for e, role in events] == [
        ("revolution-outbreak", "commander"),
        ("fall-of-tripolitsa", "commander"),
    ]


def test_listing_is_chronological_by_birth(corpus):
    born = [f.born.date for f in crud.list_figures(corpus) if f.born]
    assert born == sorted(born)


def test_no_figure_is_linked_outside_its_lifetime(corpus):
    assert lifetime_warnings(corpus) == []


def test_lifetime_warning_is_reported_not_fatal(corpus):
    navarino = next(e for e in corpus.events if e.id == "battle-of-navarino")
    linked = navarino.model_validate(
        {
            **navarino.model_dump(exclude={"body_html"}),
            "figures": [{"figure": "byron", "role": "witness"}],
        }
    )
    broken = replace(corpus, events=swap(corpus.events, linked))
    assert validate(broken) == []
    assert any("postdates the death of 'byron'" in w for w in lifetime_warnings(broken))


def test_unknown_place_and_reversed_dates_are_rejected(corpus):
    fig = crud.get_figure(corpus, "otto")
    bad = fig.model_validate(
        {
            **fig.model_dump(exclude={"body_html"}),
            "born": {"date": "1870-01-01", "place": "atlantis"},
            "died": {"date": "1860-01-01"},
        }
    )
    problems = validate(replace(corpus, figures=swap(corpus.figures, bad)))
    assert any("unknown born place 'atlantis'" in p for p in problems)
    assert any("is not before died" in p for p in problems)


def test_body_is_rendered_to_html(corpus):
    fig = crud.get_figure(corpus, "byron")
    assert "<em>Childe Harold</em>" in fig.body_html.en
