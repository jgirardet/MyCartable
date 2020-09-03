from uuid import UUID, uuid4

from package.database.mixins import ColorMixin
from pony.orm import Required, Optional, Set, PrimaryKey, Database


def class_style(db: Database) -> "Style":
    class Style(db.Entity, ColorMixin):
        styleId = PrimaryKey(UUID, auto=True, default=uuid4)
        _fgColor = Required(int, size=32, unsigned=True, default=4278190080)
        _bgColor = Required(int, size=32, unsigned=True, default=0)
        family = Optional(str)
        underline = Required(bool, default=False)
        pointSize = Optional(float)
        strikeout = Required(bool, default=False)
        weight = Optional(int)

        # penser à ajouter dans to_dict
        annotation = Optional("Annotation")
        tableau_cell = Optional("TableauCell")
        linked_objs = ["annotation", "tableau_cell"]

        def __init__(self, **kwargs):
            super().__init__(**self.adjust_kwargs(**kwargs))

        def to_dict(self, **kwargs):
            dico = super().to_dict(
                exclude=["_bgColor", "_fgColor"] + self.linked_objs, **kwargs
            )
            dico["bgColor"] = self.bgColor
            dico["fgColor"] = self.fgColor
            dico["styleId"] = str(self.styleId)
            return dico

        def set(self, **kwargs):
            super().set(**self.adjust_kwargs(**kwargs))

        def adjust_kwargs(self, **kwargs):
            colors = ["fgColor", "bgColor"]
            for col in colors:
                if col in kwargs:
                    val = kwargs.pop(col)
                    if val is not None:
                        kwargs["_" + col] = self.color_setter(val)
            return kwargs

    return Style
