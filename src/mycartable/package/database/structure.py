import datetime
from typing import Tuple
from uuid import UUID, uuid4

from pony.orm import (
    select,
    PrimaryKey,
    Optional,
    Required,
    Set,
    desc,
    Database,
    Json,
)

from .mixins import ColorMixin, PositionMixin


def class_structure(
    db: Database,
) -> Tuple["Configuration", "Annee", "GroupeMatiere", "Matiere", "Activite", "Page"]:
    class Configuration(db.Entity):
        key = PrimaryKey(str)
        field = Required(str)

        EASY_TYPES = [str, int, bool, float, datetime.datetime, datetime.date]

        str_value = Optional(str)
        int_value = Optional(int)
        bool_value = Optional(bool)
        float_value = Optional(float)
        uuid_value = Optional(UUID)
        datetime_value = Optional(datetime.datetime)
        date_value = Optional(datetime.date)
        json_value = Optional(Json)

        @classmethod
        def add(cls, key, value):
            field = cls._get_field(value)
            item = cls.get(key=key)
            if item:
                if field != item.field:  # old != new, erase old
                    setattr(item, item.field, Configuration._get_blank(item.field))
                item.field = field
                setattr(item, field, value)
            else:
                Configuration(**{"key": key, "field": field, field: value})

        @classmethod
        def option(cls, key):
            if item := Configuration.get(key=key):
                return getattr(item, item.field)

        @staticmethod
        def _get_field(value: str) -> str:
            res = ""
            if type(value) in Configuration.EASY_TYPES:
                res = value.__class__.__name__
            elif isinstance(value, UUID):
                res = "uuid"
            elif isinstance(value, (list, dict)):
                res = "json"
            else:
                raise ValueError(f"Le type {type(value)} n'est pas valide")
            return res + "_value"

        @staticmethod
        def _get_blank(value):
            if value == "json_value":
                return {}
            elif value == "str_value":
                return ""
            else:
                return None

        @classmethod
        def all(self):
            return {c.key: getattr(c, c.field) for c in Configuration.select()}

    class Annee(db.Entity):
        id = PrimaryKey(int)
        niveau = Optional(str)
        groupes = Set("GroupeMatiere")

        def get_matieres(self):
            return select(
                matiere for groupe in self.groupes for matiere in groupe.matieres
            ).order_by(lambda m: (m.groupe.position, m.position))

    class GroupeMatiere(db.Entity, PositionMixin, ColorMixin):
        referent_attribute_name = "annee"
        id = PrimaryKey(UUID, auto=True, default=uuid4)
        nom = Required(str)
        annee = Required(Annee)
        _position = Required(int)
        _fgColor = Required(int, size=32, unsigned=True, default=4278190080)
        _bgColor = Optional(int, size=32, unsigned=True, default=4294967295)
        matieres = Set("Matiere")

        def __init__(
            self, position=None, annee=None, bgColor=None, fgColor=None, **kwargs
        ):
            kwargs = self.adjust_kwargs_color(bgColor, fgColor, kwargs)
            with self.init_position(position, annee) as _position:
                super().__init__(annee=annee, _position=_position, **kwargs)

        def __repr__(self):
            return f"GroupeMatiere[{self.nom} {self.annee.id}]"

        def before_delete(self):
            self.before_delete_position()

        def after_delete(self):
            self.after_delete_position()

        def to_dict(self, **kwargs):
            dico = super().to_dict(exclude=["_fgColor", "_bgColor"], **kwargs)
            dico["position"] = dico.pop("_position")
            dico["fgColor"] = self.fgColor
            dico["bgColor"] = self.bgColor
            dico["id"] = str(self.id)
            return dico

    class Matiere(db.Entity, ColorMixin, PositionMixin):
        referent_attribute_name = "groupe"

        id = PrimaryKey(UUID, auto=True, default=uuid4)
        nom = Required(str)
        groupe = Required("GroupeMatiere")
        _position = Required(int)
        _fgColor = Required(int, size=32, unsigned=True, default=4278190080)
        _bgColor = Optional(int, size=32, unsigned=True, default=4294967295)
        activites = Set("Activite")

        def __init__(
            self, bgColor=None, fgColor=None, groupe=None, position=None, **kwargs
        ):
            kwargs = self.adjust_kwargs_color(bgColor, fgColor, kwargs)
            with self.init_position(position, groupe) as _position:
                super().__init__(groupe=groupe, _position=_position, **kwargs)

        def __repr__(self):
            return f"Matiere[{self.nom}]"

        @property
        def activites_list(self):
            return self.to_dict()["activites"]

        def to_dict(self):
            dico = super().to_dict(exclude=["_fgColor", "_bgColor", "_position"])
            dico.update(
                {
                    "id": str(self.id),
                    "groupe": str(self.groupe.id),
                    "fgColor": self.fgColor,
                    "bgColor": self.bgColor,
                    "position": self.position,
                    "activites": [
                        str(x.id) for x in self.activites.order_by(lambda x: x.position)
                    ],
                }
            )
            return dico

        def before_delete(self):
            self.before_delete_position()

        def after_delete(self):
            self.after_delete_position()

    class Activite(db.Entity, PositionMixin):
        referent_attribute_name = "matiere"

        id = PrimaryKey(UUID, auto=True, default=uuid4)
        nom = Required(str)
        matiere = Required(Matiere)
        _position = Required(int)
        pages = Set("Page")

        def __init__(self, position=None, matiere=None, **kwargs):
            with self.init_position(position, matiere) as _position:
                super().__init__(matiere=matiere, _position=_position, **kwargs)

        def before_delete(self):
            self.before_delete_position()

        def after_delete(self):
            self.after_delete_position()

        def to_dict(
            self,
        ):
            dico = super().to_dict(exclude=["_position"])
            dico.update(
                {
                    "id": str(self.id),
                    "position": self.position,
                    "matiere": str(self.matiere.id),
                    "pages": [str(p.id) for p in self.pages],
                }
            )
            return dico

        def pages_by_created(self):
            return [y.to_dict() for y in self.pages.order_by(desc(Page.created))]

    class Page(db.Entity):
        id = PrimaryKey(UUID, auto=True, default=uuid4)
        created = Required(datetime.datetime, default=datetime.datetime.utcnow)
        modified = Optional(datetime.datetime)
        titre = Optional(str, default="")
        activite = Required("Activite")
        lastPosition = Optional(int, default=0)
        sections = Set("Section")

        def before_insert(self):
            self.modified = self.created

        def before_update(self):
            if hasattr(self, "reasonUpdate"):
                del self.reasonUpdate  # block page autoupdate when provient de section
            else:
                self.modified = datetime.datetime.utcnow()

        def to_dict(self):
            dico = super().to_dict()
            dico.update(
                {
                    "id": str(self.id),
                    "created": self.created.isoformat(),
                    "modified": self.modified.isoformat(),
                    "activite": str(self.activite.id),
                    "annee": self.activite.matiere.groupe.annee.id,
                    "lastPosition": self.lastPosition,
                    "sections": [
                        str(s.id) for s in self.sections.order_by(lambda x: x.position)
                    ],
                    "matiere": str(self.activite.matiere.id),
                    "matiereNom": self.activite.matiere.nom,
                    "matiereFgColor": self.activite.matiere.fgColor,
                    "matiereBgColor": self.activite.matiere.bgColor,
                }
            )
            return dico

        def _query_recents(self, annee):
            query = (
                select(p for p in Page if p.activite.matiere.groupe.annee.id == annee)
                .order_by(desc(Page.modified))
                .limit(50)
            )  # pragma: no cover_all
            return query

        @classmethod
        def recents(cls, annee):
            return [p.to_dict() for p in cls._query_recents(cls, annee)]

        @staticmethod
        def new_page(activite, titre=""):
            return Page(titre=titre, activite=activite).to_dict()

        @property
        def content(self):
            return [p for p in self.sections.order_by(db.Section._position)]

    return Configuration, Annee, GroupeMatiere, Matiere, Activite, Page
