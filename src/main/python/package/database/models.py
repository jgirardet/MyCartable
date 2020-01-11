from datetime import datetime, timedelta

from pony.orm import select, Database, PrimaryKey, Optional, Required, Set, desc


def init_models(db: Database):
    class Annee(db.Entity):
        id = PrimaryKey(int, auto=True)
        niveau = Optional(str)
        matiere = Set("Matiere")

    class Matiere(db.Entity):
        id = PrimaryKey(int, auto=True)
        nom = Required(str)
        annee = Required(Annee)
        activites = Set('Activite')

        @classmethod
        def noms(self):
            return [p.to_dict(only=['id', 'nom']) for p in Matiere.select()]


    class Activite(db.Entity):
        id = PrimaryKey(int, auto=True)
        nom = Required(str)
        famille = Required(int)
        matiere = Required(Matiere)
        pages = Set("Page")




    class Page(db.Entity):
        id = PrimaryKey(int, auto=True)
        created = Required(datetime, default = datetime.now)
        modified = Optional(datetime)
        titre = Required(str)
        activite = Required('Activite')
        sections = Set("Section")

        @classmethod
        def recents(cls):
            query = select(p for p in cls if p.modified < datetime.now() - timedelta(days=30)).order_by(desc(Page.modified))
            res = []
            for p in query:
                a = p.to_dict()
                a['matiere'] = p.activite.matiere.nom
                res.append(a)
            return res

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


