from package.database.mixins import ColorMixin
from pony.orm import Required, Optional, Set

from .root_db import db


class Style(db.Entity, ColorMixin):
    _fgColor = Required(int, size=32, unsigned=True, default=4278190080)
    fgColor = property(ColorMixin.fgColor_get, ColorMixin.fgColor_set)
    _bgColor = Required(int, size=32, unsigned=True, default=0)
    bgColor = property(ColorMixin.bgColor_get, ColorMixin.bgColor_set)
    family = Optional(str)
    underline = Required(bool, default=False)
    pointSize = Optional(float)
    strikeout = Required(bool, default=False)
    weight = Optional(int)

    annotation = Optional("Annotation")
    tableau_cell = Optional("TableauCell")

    def __init__(self, **kwargs):
        super().__init__(**self.adjust_kwargs(**kwargs))

    def to_dict(self, **kwargs):
        dico = super().to_dict(exclude=["_bgColor", "_fgColor"], **kwargs)
        linked_objs = ["annotation", "tableau_cell"]
        for obj in linked_objs:
            if not getattr(self, obj):
                dico.pop(obj)
        dico["bgColor"] = self.bgColor
        dico["fgColor"] = self.fgColor
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
