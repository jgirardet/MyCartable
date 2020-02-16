from datetime import datetime, timedelta
from pathlib import Path

from PySide2.QtCore import QUrl
from PySide2.QtGui import QColor
from pony.orm import select, Database, PrimaryKey, Optional, Required, Set, desc, flush
from package.constantes import ACTIVITES


def init_models(db: Database):
    class Annee(db.Entity):
        id = PrimaryKey(int, auto=True)
        niveau = Optional(str)
        matiere = Set("Matiere")

    class Matiere(db.Entity):
        id = PrimaryKey(int, auto=True)
        nom = Required(str)
        annee = Required(Annee)
        activites = Set("Activite")

        @classmethod
        def noms(self):
            return [p.nom for p in Matiere.select()]

        @property
        def activites_list(self):
            return self.to_dict()["activites"]

        def after_insert(self):
            for ac in ACTIVITES:
                Activite(nom=ac.nom, famille=ac.index, matiere=self)

        def to_dict(self, *args, **kwargs):
            return super().to_dict(*args, with_collections=True, **kwargs)

    class Activite(db.Entity):

        ACTIVITES = ACTIVITES

        id = PrimaryKey(int, auto=True)
        nom = Required(str)
        famille = Required(int)
        matiere = Required(Matiere)
        pages = Set("Page")

        @classmethod
        def pages_by_matiere_and_famille(cls, matiere_id, famille):
            if not matiere_id:
                return []
            elif isinstance(matiere_id, str):
                matiere = select(
                    p for p in Matiere if p.nom == matiere_id
                )  # pragma: no cover_all
                if matiere:
                    matiere = matiere.first()
                else:
                    return []
            else:
                matiere = db.Matiere.get(id=matiere_id)
                if not matiere:
                    return []
            activite = Activite.get(matiere=matiere.id, famille=famille)

            if activite:
                return [
                    p.to_dict() for p in activite.pages.order_by(desc(Page.created))
                ]
            return []

    class Page(db.Entity):
        id = PrimaryKey(int, auto=True)
        created = Required(datetime, default=datetime.utcnow)
        modified = Optional(datetime)
        titre = Optional(str)
        activite = Required("Activite")
        sections = Set("Section")

        def _query_recents(self):
            query = select(
                p for p in Page if p.modified > datetime.utcnow() - timedelta(days=30)
            ).order_by(
                desc(Page.modified)
            )  # pragma: no cover_all
            return query

        def to_dict(self, *args, **kwargs):
            dico = super().to_dict(*args, **kwargs)
            dico["matiere"] = self.activite.matiere.id
            dico["matiereNom"] = self.activite.matiere.nom
            dico["famille"] = self.activite.famille
            dico["created"] = self.created.isoformat()
            dico["modified"] = self.created.isoformat()
            return dico

        @classmethod
        def recents(cls):
            return [p.to_dict() for p in cls._query_recents(cls)]

        @staticmethod
        def new_page(activite, titre=""):
            return Page(titre=titre, activite=activite).to_dict()

        @property
        def content(self):
            return [p for p in self.sections.order_by(Section.position)]

        @property
        def content_dict(self):
            return [p.to_dict() for p in self.content]

        def before_insert(self):
            self.modified = self.created

        #
        def before_update(self):
            self.modified = datetime.utcnow()

    class Section(db.Entity):
        id = PrimaryKey(int, auto=True)
        created = Required(datetime, default=datetime.utcnow)
        modified = Optional(datetime)
        page = Required(Page)
        position = Optional(int, default=0)  # minimum = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.updating_position = False

        def to_dict(self, *args, **kwargs):
            dico = super().to_dict(*args, **kwargs)
            dico["created"] = self.created.isoformat()
            dico["modified"] = self.modified.isoformat()
            return dico

        def before_insert(self):
            self.modified = self.created
            self.page.modified = self.modified

            count = self.page.sections.count()
            if not self.position or count < self.position:
                # it seems that
                self.position = self.page.sections.count()
            else:
                self._update_position()

        def before_update(self):
            if getattr(self, "updating_position", None):
                self.updating_position = False
            else:
                self.modified = datetime.utcnow()
                self.page.modified = self.modified

        def _update_position(self):
            n = 1
            for x in self.page.content:
                if n == self.position:
                    n += 1
                x.updating_position = True  # do not update modified on position
                x.position = n
                n += 1

    class ImageSection(Section):
        path = Optional(str)
        annotations = Set("Annotation")

        def __init__(self, *args, **kwargs):
            path = kwargs.pop("path")
            if isinstance(path, Path):
                path = str(path)
            elif isinstance(path, QUrl):
                path = path.toString()
            super().__init__(*args, path=path, **kwargs)

    class TextSection(Section):
        text = Optional(str)

    class Annotation(db.Entity):
        id = PrimaryKey(int, auto=True)
        relativeX = Required(float)
        relativeY = Required(float)
        section = Required(ImageSection)
        color = Optional(int, size=32, unsigned=True)

        def __init__(self, *args, **kwargs):
            color = kwargs.pop("color", None)
            if color and isinstance(color, QColor):
                color = color.rgba()
            super().__init__(*args, color=color, **kwargs)

        def to_dict(self, *args, **kwargs):
            dico = super().to_dict(*args, **kwargs)
            dico["color"] = QColor(dico["color"]) if dico["color"] else None
            return dico

        def before_insert(self):
            self.section.before_update()

        def before_delete(self):
            if Section.exists(id=self.section.id):
                self.section.before_update()

    class Stabylo(Annotation):
        relativeWidth = Required(float)
        relativeHeight = Required(float)

    class AnnotationText(Annotation):
        text = Optional(str)
        underline = Optional(bool, default=False)
