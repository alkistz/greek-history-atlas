from dataclasses import replace
from datetime import date

from conftest import swap

from app.core.content import validate
from app.core.models import Pass, Review
from app.modules.events import crud


def reviewed(corpus, event_id, **kw):
    """The event with a replacement auto pass, for building broken corpora."""
    e = crud.get_event(corpus, event_id)
    fields = {"date": date(2026, 9, 20), "result": "clean", "langs": ["en", "el"], **kw}
    return e.model_copy(update={"review": Review(auto=Pass(**fields))})


def test_recorded_passes_are_well_formed(corpus):
    """Deliberately not a count. The review set grows with every batch, and a test
    that has to be edited each time is a test that will be edited without thought."""
    done = [x for x in (*corpus.events, *corpus.figures) if x.review and x.review.auto]
    assert done, "no pass has been recorded at all"
    assert {x.review.auto.result for x in done} <= {"clean", "corrected", "unresolved"}
    for x in done:
        assert x.review.auto.langs, f"{x.id}: a pass must say what it read"
        if x.review.auto.result != "clean":
            assert x.review.auto.note, f"{x.id}: a non-clean pass should say why"


def test_the_cyprus_thread_is_done(corpus):
    """Batches run by thread, so a thread is the unit that is finished or not."""
    thread = next(t for t in corpus.threads if t.id == "cyprus-question")
    by_id = {e.id: e for e in corpus.events}
    assert all(by_id[i].review and by_id[i].review.auto for i in thread.events)


def test_absent_review_is_valid(corpus):
    """An entry nobody has examined must stay valid and say so by omission, rather
    than being backfilled with a claim nobody made. Asserted as a property: the
    first version of this test checked that some entry was unreviewed, which was
    a fact about the day it was written and broke the moment the sweep finished."""
    assert validate(corpus) == []
    bare = corpus.events[0].model_copy(update={"review": None})
    assert validate(replace(corpus, events=swap(corpus.events, bare))) == []


def test_clean_requires_every_language_the_entry_has(corpus):
    """The two texts are translations, so a fact wrong in one is wrong in both.
    English alone is not a sample of a bilingual entry."""
    bad = reviewed(corpus, "battle-of-navarino", result="clean", langs=["en"])
    problems = validate(replace(corpus, events=swap(corpus.events, bad)))
    assert any("cannot be 'clean' without reading el" in p for p in problems)


def test_a_partial_pass_may_still_report_a_correction(corpus):
    """Only `clean` makes a claim about the whole entry; the other results do not."""
    ok = reviewed(corpus, "battle-of-navarino", result="corrected", langs=["en"])
    assert validate(replace(corpus, events=swap(corpus.events, ok))) == []


def test_unresolved_needs_a_note(corpus):
    bad = reviewed(corpus, "battle-of-navarino", result="unresolved", note=None)
    problems = validate(replace(corpus, events=swap(corpus.events, bad)))
    assert any("'unresolved' needs a note" in p for p in problems)


def test_a_manual_pass_records_who_made_it(corpus):
    e = crud.get_event(corpus, "battle-of-navarino")
    manual = Pass(date=date(2026, 9, 21), result="clean", langs=["en", "el"])
    bad = e.model_copy(update={"review": Review(manual=manual)})
    problems = validate(replace(corpus, events=swap(corpus.events, bad)))
    assert any("a manual pass records who made it" in p for p in problems)


def test_the_two_tracks_are_independent(corpus):
    """An automated pass must never be able to present itself as a human one."""
    famine = crud.get_event(corpus, "great-famine")
    assert famine.review.auto.result == "unresolved"
    assert famine.review.manual is None


def test_a_web_source_needs_a_url(corpus):
    book = next(s for s in corpus.sources if s.id == "hionidou-2006")
    bad = book.model_validate({**book.model_dump(), "kind": "web", "url": None})
    problems = validate(replace(corpus, sources=swap(corpus.sources, bad)))
    assert any("a web source needs a url" in p for p in problems)


def test_the_named_scholar_is_now_cited(corpus):
    """The famine event named Hionidou in prose while citing neither her nor her
    book. Naming an authority is a citation whether or not it is formatted as one."""
    famine = crud.get_event(corpus, "great-famine")
    assert "hionidou-2006" in {c.id for c in famine.sources}
    assert any(s.id == "hionidou-2006" and s.isbn for s in corpus.sources)
