import mimesis
import random
from pony.orm import db_session
gen = mimesis.Generic("fr")

from package.database import db

def f_annee():
        with db_session:
            return db.Annee(niveau="cm1")

def f_matiere(nom = None, annee=None):
    nom = nom or random.choice(["Français", "Math", "Anglais", "Histoire"])
    annee = annee or f_annee()
    with db_session:
        return db.Matiere(annee=annee, nom=nom)


def f_activite(famille=None, matiere=None):
    activites = ((0, "Exercice"), (1, "Leçon"), (2, "Divers"))
    famille = famille or random.choice(activites)[0]
    nom = activites[famille][1]
    matiere = matiere or f_matiere()
    with db_session:
        return db.Activite(nom=nom, famille=famille, matiere=matiere)


def f_page(created=None, activite=None):
    created = created or gen.datetime.datetime(start=2019, end=2020)
    activite = activite or f_activite()
    with db_session:
        return db.Page(created=created, activite=activite)

def f_section(created=None, page=None, content=None, content_type=None):
    created = created or gen.datetime.datetime(start=2019, end=2020)
    page = page or f_page()
    content = content or gen.text.sentence()
    content_type= content_type or "str"
    with db_session:
        return db.Section(created=created, page=page)


@db_session
def populate_database():
    annee = f_annee()
    matieres = [f_matiere("Math", annee),f_matiere("Français", annee),f_matiere("Histoire", annee),f_matiere("Anglais", annee),]
    activites = []
    for m in matieres:
        for i in range(3):
            activites.append(f_activite(famille=i, matiere=m))

    for i in range(100):
        f_page(activite=random.choice(activites))
