from datetime import datetime, timedelta

import mimesis
import random

from package.constantes import ACTIVITES
from pony.orm import db_session

gen = mimesis.Generic("fr")

from package.database import db


def f_datetime(start=None, end=None):
    end = end or datetime.now()
    start = start or end - timedelta(days=400)
    now = datetime.now()

    while True:
        res = gen.datetime.datetime(start=start.year, end=now.year + 1)
        if start < res <= end:
            return res


def f_annee():
    with db_session:
        return db.Annee(niveau="cm1")


def f_matiere(nom=None, annee=None):
    nom = nom or random.choice(["Français", "Math", "Anglais", "Histoire"])
    with db_session:
        annee = annee or f_annee()
        return db.Matiere(annee=annee, nom=nom)


#
# def f_activite(famille=None, matiere=None):
#     activites = ((0, "Exercice"), (1, "Leçon"), (2, "Divers"))
#     famille = famille if famille is not None else random.choice(activites)[0]
#     nom = activites[famille][1]
#     with db_session:
#         matiere = matiere or f_matiere()
#         return db.Activite(nom=nom, famille=famille, matiere=matiere)


def f_page(created=None, activite=None, titre=None, td=False):
    """actvite int = id mais str = index"""
    with db_session:
        created = created or f_datetime()
        if activite:
            if isinstance(activite, int):
                activite = activite
            elif isinstance(activite, str):
                m = f_matiere()
                m.flush()
                activite = m.activites_list[int(activite)]
        else:
            m = f_matiere()
            m.flush()
            activite = random.choice(m.activites.select()[:])
        titre = titre or " ".join(gen.text.words(5))
        item = db.Page(created=created, activite=activite, titre=titre)
        item.flush()
        return item.to_dict() if td else item


def b_page(n, td=False, created=None, activite=None, titre=None):
    res = [f_page(created, activite, titre, td) for p in range(n)]
    return res


def f_section(created=None, page=None, content=None, content_type=None, position=0, td=False):
    with db_session:
        created = created or f_datetime()
        page = page or f_page(td=True)['id']
        content = content or gen.text.sentence()
        content_type = content_type or "str"

        item = db.Section(
            created=created,
            page=page,
            content=content,
            content_type=content_type,
            position=position,
        )
        item.flush()
        # print(item.page.content(), "dans fac")
        return item.to_dict() if td else item

def b_section(n, *args, **kwargs ):
    return [f_section(*args, **kwargs) for p in range(n)]


@db_session
def populate_database(matieres_list=None, nb_page=100):
    annee = f_annee()
    if matieres_list is not None:
        matieres = [f_matiere(x, annee) for x in matieres_list]
    else:
        matieres = [
            f_matiere("Math", annee),
            f_matiere("Français", annee),
            f_matiere("Histoire", annee),
            f_matiere("Anglais", annee),
        ]

    activites = db.Activite.select()[:]
    for i in range(nb_page):
        f_page(activite=random.choice(activites))
