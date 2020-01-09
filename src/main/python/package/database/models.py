from datetime import datetime

from pony.orm import select, Database, PrimaryKey, Optional, Required, Set



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
        activite = Required('Activite')
        sections = Set("Section")



    class Section(db.Entity):
        id = PrimaryKey(int, auto=True)
        created = Required(datetime, default=datetime.now)
        modified = Optional(datetime)
        page = Required(Page)
        content = Optional(str)
        content_type = Optional(str)


        def before_insert(self):
            self.modified = self.created

        def before_update(self):
            self.modified = datetime.now()


