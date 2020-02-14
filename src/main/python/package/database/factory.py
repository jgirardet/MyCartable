from datetime import datetime, timedelta
from pathlib import Path

import mimesis
import random

from PySide2.QtGui import QColor
from package.constantes import ACTIVITES, FILES, MATIERES
from pony.orm import db_session

gen = mimesis.Generic("fr")

from package.database import db


def f_datetime(start=None, end=None):
    end = end or datetime.utcnow()
    start = start or end - timedelta(days=400)
    now = datetime.now()

    while True:
        res = gen.datetime.datetime(start=start.year, end=now.year + 1)
        if start < res <= end:
            return res


def f_annee(niveau=None):
    niveau = niveau or "cm1"
    with db_session:
        return db.Annee(niveau=niveau)


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
    created=None, page=None, position=0, td=False,
):
    with db_session:
        created = created or f_datetime()
        page = page or f_page(td=True)["id"]

        item = db.Section(created=created, page=page, position=position,)
        item.flush()
        return item.to_dict() if td else item


def b_section(n, *args, **kwargs):
    return [f_section(*args, **kwargs) for x in range(n)]


def f_imageSection(
    created=None, page=None, path=None, position=0, td=False,
):
    with db_session:
        created = created or f_datetime()
        page = page or f_page(td=True)["id"]

        path = path or str(
            Path(__file__).parents[5].absolute()
            / "tests"
            / "resources"
            / "tst_AnnotableImage.png"
        )

        item = db.ImageSection(
            created=created, page=page, path=path, position=position,
        )
        item.flush()
        return item.to_dict() if td else item


def f_textSection(created=None, page=None, position=0, td=False, text=None):
    with db_session:
        created = created or f_datetime()
        page = page or f_page(td=True)["id"]

        text = text or gen.text.text(random.randint(0, 10))

        item = db.TextSection(created=created, page=page, text=text, position=position,)
        item.flush()
        return item.to_dict() if td else item


def f_stabylo(
    relativeX=None,
    relativeY=None,
    relativeWidth=None,
    relativeHeight=None,
    td=False,
    section=None,
    color=None,
):
    relativeX = relativeX or random.randint(0, 100) / 100
    relativeY = relativeY or random.randint(0, 100) / 100
    relativeWidth = relativeWidth or random.randint(0, 100) / 100
    relativeHeight = relativeHeight or random.randint(0, 100) / 100
    section = section or f_section().id
    color = QColor(color).rgba() if color else None

    with db_session:
        item = db.Stabylo(
            relativeX=relativeX,
            relativeY=relativeY,
            relativeWidth=relativeWidth,
            relativeHeight=relativeHeight,
            section=section,
            color=color,
        )
        return item.to_dict() if td else item


def b_stabylo(n, *args, **kwargs):
    return [f_stabylo(*args, **kwargs) for x in range(n)]


def f_annotationText(relativeX=None, relativeY=None, text=None, td=False, section=None):
    relativeX = relativeX or random.randint(0, 100) / 100
    relativeY = relativeY or random.randint(0, 100) / 100
    text = text or " ".join(gen.text.words(2))
    section = section or f_section().id

    with db_session:
        item = db.AnnotationText(
            relativeX=relativeX, relativeY=relativeY, text=text, section=section
        )
        return item.to_dict() if td else item


def b_annotation(n, *args, **kwargs):
    return [f_annotationText(*args, **kwargs) for x in range(n)]


@db_session
def populate_database(matieres_list=MATIERES, nb_page=100):
    annee = f_annee()
    matieres = [f_matiere(x, annee) for x in matieres_list]

    activites = db.Activite.select()[:]
    for i in range(nb_page):
        a = f_page(activite=random.choice(activites))
        for x in range(random.randint(0, 14)):
            random.choice([f_imageSection(page=a.id), f_textSection(page=a.id)])
