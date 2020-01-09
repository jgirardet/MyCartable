from datetime import datetime

from pony.orm import select, Database, PrimaryKey, Optional, Required, Set



def init_models(db: Database):
    class Annee(db.Entity):
        id = PrimaryKey(int, auto=True)
        niveau = Optional(str)
        pages = Set("Page")

    class Matiere(db.Entity):
        id = PrimaryKey(int, auto=True)
        nom = Required(str)
        annee = Required
        activites = Set('Activite')


    class Activite(db.Entity):
        id = PrimaryKey(int, auto=True)
        nom = Required(str)
        pages = Set("Page")
        type = Required(int)
        matiere = Required(Matiere)




    class Page(db.Entity):
        id = PrimaryKey(int, auto=True)
        created = Required(datetime, default = datetime.now)
        sections = Set("Section")
        genre = Required('Activite')
        annee = Required(Annee)



    class Section(db.Entity):
        id = PrimaryKey(int, auto=True)
        created = Required(datetime, default=datetime.now)
        page = Required(Page)


