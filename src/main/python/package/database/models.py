from datetime import datetime, timedelta

from pony.orm import select, Database, PrimaryKey, Optional, Required, Set, desc, flush



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

    class Activite(db.Entity):
        id = PrimaryKey(int, auto=True)
        nom = Required(str)
        famille = Required(int)
        matiere = Required(Matiere)
        pages = Set("Page")

        @classmethod
        def pages_by_matiere_and_famille(cls, matiere_id, famille):
            matiere = db.Matiere.get(id=matiere_id)
            if matiere:
                activite = db.Activite.get(lambda p: p.matiere.id==matiere_id and p.famille==famille)
            else:
                return []
            if activite:
                return [p.to_dict() for p in activite.pages.order_by(Page.created)]
            return []




    class Page(db.Entity):
        id = PrimaryKey(int, auto=True)
        created = Required(datetime, default=datetime.now)
        modified = Optional(datetime)
        titre = Optional(str)
        activite = Required("Activite")
        sections = Set("Section")

        def _query_recents(self):
            return select(
                p for p in Page if p.modified > datetime.now() - timedelta(days=30)
            ).order_by(desc(Page.modified))

        def to_dict(self, *args, **kwargs):
            dico = super().to_dict(*args, **kwargs)
            dico["matiere"] = self.activite.matiere.id
            dico["matiereNom"] = self.activite.matiere.nom
            return dico

        @classmethod
        def recents(cls):
            return [p.to_dict() for p in cls._query_recents(cls)]

        @staticmethod
        def new_page(activite, titre=""):
            return Page(titre=titre, activite=activite).to_dict()

        def before_insert(self):
            self.modified = self.created

    class Section(db.Entity):
        id = PrimaryKey(int, auto=True)
        created = Required(datetime, default=datetime.now)
        modified = Optional(datetime)
        page = Required(Page)
        content = Optional(str)
        content_type = Optional(str)

        def before_insert(self):
            self.modified = self.created
            self.page.modified = self.modified

        def before_update(self):
            self.modified = datetime.now()
            self.page.modified = self.modified
