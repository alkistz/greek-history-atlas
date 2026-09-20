"""Markdown to HTML, done once at load time.

Content is authored in the repo, so it is trusted and no sanitiser is applied. The
frontend renders the result with `{@html}` and adds no Markdown dependency of its own.
"""

from markdown_it import MarkdownIt

from app.core.models import LangText

_md = MarkdownIt("commonmark")


def render_markdown(text: str) -> str:
    return _md.render(text)


def render_lang_text(text: LangText | None) -> LangText | None:
    if text is None:
        return None
    return LangText(
        en=render_markdown(text.en),
        el=render_markdown(text.el) if text.el is not None else None,
    )
