from pydantic import Field

from app.core.models import FrameId, LangText, Strict


class Region(Strict):
    """A named group of atoms.

    An atom is the grain the map is drawn at; a region is the grain a reader thinks
    in. Membership lives here and nowhere else, so regrouping is a one-file edit
    and costs nothing per event.
    """

    id: str
    name: LangText
    atoms: list[str] = Field(min_length=1)
    # A viewport hint only, where one of the named frames shows the region well.
    # It does not define the region; `atoms` does.
    frame: FrameId | None = None
    summary: LangText | None = None
