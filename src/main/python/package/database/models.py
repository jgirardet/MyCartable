from datetime import datetime, timedelta

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
        created = Required(datetime, default=datetime.now)
        modified = Optional(datetime)
        titre = Optional(str)
        activite = Required("Activite")
        sections = Set("Section")

        def _query_recents(self):
            query = select(
                p for p in Page if p.modified > datetime.now() - timedelta(days=30)
            ).order_by(
                desc(Page.modified)
            )  # pragma: no cover_all
            return query

        def to_dict(self, *args, **kwargs):
            dico = super().to_dict(*args, **kwargs)
            dico["matiere"] = self.activite.matiere.id
            dico["matiereNom"] = self.activite.matiere.nom
            dico["activiteIndex"] = self.activite.famille
            return dico


        @classmethod
        def recents(cls):
            return [p.to_dict() for p in cls._query_recents(cls)]

        @staticmethod
        def new_page(activite, titre=""):
            return Page(titre=titre, activite=activite).to_dict()

        @property
        def content(self):
            return [p.to_dict() for p in self.sections.order_by(Section.position)]

        def before_insert(self):
            self.modified = self.created

    class Section(db.Entity):
        id = PrimaryKey(int, auto=True)
        created = Required(datetime, default=datetime.now)
        modified = Optional(datetime)
        page = Required(Page)
        content = Optional(str)
        content_type = Optional(str)
        position = Optional(int, default=0)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.updating_position = False

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
            if self.updating_position:
                self.updating_position = False
            else:
                self.modified = datetime.now()
                self.page.modified = self.modified


        def _update_position(self):
            n=1
            for x in self.page.content:
                if n == self.position:
                    n+=1
                x.updating_position = True # do not update modified on position
                x.position = n
                n+=1
