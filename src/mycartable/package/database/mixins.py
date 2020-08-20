from contextlib import contextmanager

from PySide2.QtGui import QColor
from pony.orm import Required
from pony.orm.core import Entity, Attribute, select, Optional, EntityProxy, max, flush


class ColorMixin:
    @staticmethod
    def color_getter(value):
        if value is None:
            return QColor("transparent")
        return QColor.fromRgba(value)

    @staticmethod
    def color_setter(value):
        if isinstance(value, QColor):
            return value.rgba()
        elif isinstance(value, str):
            return QColor(value).rgba()
        elif isinstance(value, int):
            return value
        elif isinstance(value, tuple):
            return QColor(*value).rgba()
        else:
            return None

    def fgColor_get(self):
        return self.color_getter(self._fgColor)

    def fgColor_set(self, value):
        res = self.color_setter(value)
        if res:
            self._fgColor = self.color_setter(value)

    def bgColor_get(self):
        return self.color_getter(self._bgColor)

    def bgColor_set(self, value):
        res = self.color_setter(value)
        if res:
            self._bgColor = self.color_setter(value)


class PositionMixin:
    """Mixin qui apporte la possibilté d'ordonner la collection

    Dans la nouvelle classe :
        - spécifier `referent_attribute_name` comme class attribute. Correspond à
        l'autre côté de la collection.
        - créer `_position = Required(int)
        - modifier les fonctions suivantes:
              ```
            def __init__(self, position=None, ref=None, **kwargs):
                 with self.init_position(position, ref) as _position:
                    super().__init__(ref=ref, _position=_position, **kwargs)

            def before_delete(self):
                self.before_delete_position()

            def after_delete(self):
                self.after_delete_position()

            def to_dict():
                dico = super().to_dict(*args, **kwargs)
                dico["position"] = dico.pop("_position")
                return dico

            ```

    """

    referent_attribute_name: str
    base_class_position: Optional(Entity) = None

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new):
        self._position = self._recalcule_position(self._position, new)

    @classmethod
    def get_by_position(cls, ref_id):
        base_class = cls.base_class_position or cls
        return select(
            p
            for p in base_class
            if getattr(p, base_class.referent_attribute_name).id == ref_id
        ).order_by(base_class._position)

    def get_referent(self):
        return getattr(self, self.referent_attribute_name)

    def _recalcule_position(self, old, new, query=None):
        base_class = self.base_class_position or self.__class__
        if old == new:
            return new
        query = (
            query
            if query is not None
            else base_class.get_by_position(self.get_referent().id)
        )
        if new >= query.count():
            return query.count()

        elif old < new:
            for sec in query:
                if old < sec.position <= new and sec != self:
                    sec._position -= 1
        else:
            # elif old > new:
            for sec in query:
                if new <= sec.position < old:
                    sec._position += 1
        return new

    @contextmanager
    def init_position(self, pos, ref):
        base_class = self.base_class_position or self.__class__
        if isinstance(ref, (Entity, EntityProxy)):
            ref = ref.id
        nb = self.get_by_position(ref).count()
        if pos is not None:
            if pos >= nb:
                yield nb

            else:
                query = select(
                    p
                    for p in base_class
                    if getattr(p, self.referent_attribute_name).id == ref
                    and p.position >= pos
                )
                for s in query:
                    s._position += 1
                yield pos
        else:

            query = select(
                s
                for s in base_class
                if getattr(s, self.referent_attribute_name).id == ref
            )
            new_pos = query.count()
            yield new_pos
        flush()

    def before_delete_position(self):
        ref = self.get_referent()
        self._positionbackup = (
            ref.__class__,
            ref.id,
        )

    def after_delete_position(self):
        base_class = self.base_class_position or self.__class__
        n = 0
        # self_class = self.__class__
        # try:
        referent = self._positionbackup[0][self._positionbackup[1]]
        # except:
        #     return
        children = select(
            p
            for p in base_class
            if getattr(p, self.referent_attribute_name) == referent
        ).order_by(base_class._position)
        for s in children:
            s._position = n
            n += 1
