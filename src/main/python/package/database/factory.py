from datetime import datetime, timedelta

import mimesis
import random

from package.constantes import ACTIVITES, FILES
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


def f_page(created=None, activite=None, titre=None, td=False, matiere=None):
    """actvite int = id mais str = index"""
    with db_session:
        created = created or f_datetime()

        if matiere:
            if activite is None:
                activite = random.choice(db.Matiere[matiere].activites.select()[:])
            else:
                activite = db.Activite.get(matiere=matiere, famille=int(activite))
        elif activite:
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


def b_page(n, *args, **kwargs):
    res = [f_page(*args, **kwargs) for p in range(n)]
    return res


def f_section(
    created=None,
    page=None,
    content=None,
    content_type=None,
    position=0,
    td=False,
    img=False,
):
    with db_session:
        created = created or f_datetime()
        page = page or f_page(td=True)["id"]

        if img:
            content = "essai.jpg"
            content_type = "img"
        else:
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
        return item.to_dict() if td else item


def b_section(n, *args, **kwargs):
    return [f_section(*args, **kwargs) for x in range(n)]


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
        a = f_page(activite=random.choice(activites))
        for x in range(random.randint(0, 14)):
            random.choice([f_section(page=a.id), f_section(page=a.id, img=True)])
