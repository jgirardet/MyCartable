from datetime import datetime, timedelta

from pony.orm import (
    select,
    PrimaryKey,
    Optional,
    Required,
    Set,
    desc,
)
from package.constantes import ACTIVITES
from .root_db import db
from .mixins import ColorMixin, PositionMixin


class Annee(db.Entity):
    id = PrimaryKey(int)
    niveau = Optional(str)
    groupes = Set("GroupeMatiere")
    user = Required("Utilisateur", reverse="annees")

    def get_matieres(self):
        return select(
            matiere
            for groupe in self.groupes.select()
            for matiere in groupe.matieres.select()
        )


class GroupeMatiere(db.Entity, PositionMixin):
    referent_attribute_name = "annee"
    id = PrimaryKey(int, auto=True)
    nom = Required(str)
    annee = Required(Annee)
    _position = Required(int)
    matieres = Set("Matiere")

    def __init__(self, position=None, annee=None, **kwargs):
        with self.init_position(position, annee) as _position:
            super().__init__(annee=annee, _position=_position, **kwargs)

    def before_delete(self):
        self.before_delete_position()

    def after_delete(self):
        self.after_delete_position()

    def to_dict(**kwargs):
        dico = super().to_dict(**kwargs)
        dico["position"] = dico.pop("_position")
        return dico


class Matiere(db.Entity, ColorMixin, PositionMixin):
    referent_attribute_name = "groupe"

    id = PrimaryKey(int, auto=True)
    nom = Required(str)
    activites = Set("Activite")
    groupe = Required("GroupeMatiere")
    _position = Required(int)
    _fgColor = Required(int, size=32, unsigned=True, default=4278190080)
    fgColor = property(ColorMixin.fgColor_get, ColorMixin.fgColor_set)
    _bgColor = Optional(int, size=32, unsigned=True, default=4294967295)
    bgColor = property(ColorMixin.bgColor_get, ColorMixin.bgColor_set)

    def __init__(
        self, bgColor=None, fgColor=None, groupe=None, position=None, **kwargs
    ):
        if bgColor:
            kwargs["_bgColor"] = ColorMixin.color_setter(bgColor)
        if fgColor:
            kwargs["_fgColor"] = ColorMixin.color_setter(fgColor)
        with self.init_position(position, groupe) as _position:
            super().__init__(groupe=groupe, _position=_position, **kwargs)

    @property
    def activites_list(self):
        return self.to_dict()["activites"]

    def after_insert(self):
        for ac in db.Activite.ACTIVITES:
            Activite(nom=ac.nom, famille=ac.index, matiere=self)

    def to_dict(self, *args, **kwargs):
        res = super().to_dict(
            *args, with_collections=True, exclude=["_fgColor", "_bgColor"], **kwargs
        )
        res["fgColor"] = self.fgColor
        res["bgColor"] = self.bgColor
        res["position"] = res.pop("_position")
        return res

    def pages_par_section(self):
        res = []
        for x in self.activites.select().order_by(Activite.famille):
            entry = x.to_dict()
            entry["pages"] = [
                y.to_dict()
                for y in select(p for p in x.pages).order_by(desc(Page.created))
            ]
            res.append(entry)
        return res

    def before_delete(self):
        self.before_delete_position()

    def after_delete(self):
        self.after_delete_position()


class Activite(db.Entity):

    ACTIVITES = ACTIVITES

    id = PrimaryKey(int, auto=True)
    nom = Required(str)
    famille = Required(int)
    matiere = Required(Matiere)
    pages = Set("Page")


class Page(db.Entity):
    id = PrimaryKey(int, auto=True)
    created = Required(datetime, default=datetime.utcnow)
    modified = Optional(datetime)
    titre = Optional(str, default="")
    activite = Required("Activite")
    sections = Set("Section")
    lastPosition = Optional(int, default=0)

    def before_insert(self):
        self.modified = self.created

    def before_update(self):
        if hasattr(self, "reasonUpdate"):
            del self.reasonUpdate  # block page autoupdate when provient de section
        else:
            self.modified = datetime.utcnow()

    def to_dict(self, *args, **kwargs):
        dico = super().to_dict(*args, **kwargs)
        dico["matiere"] = self.activite.matiere.id
        dico["matiereNom"] = self.activite.matiere.nom
        dico["matiereFgColor"] = self.activite.matiere.fgColor
        dico["matiereBgColor"] = self.activite.matiere.bgColor
        dico["famille"] = self.activite.famille
        dico["created"] = self.created.isoformat()
        dico["modified"] = self.created.isoformat()
        return dico

    def _query_recents(self, annee):
        query = select(
            p
            for p in Page
            if p.modified > datetime.utcnow() - timedelta(days=30)
            and p.activite.matiere.groupe.annee.id == annee
        ).order_by(
            desc(Page.modified)
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
