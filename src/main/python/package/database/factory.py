from datetime import datetime, timedelta
from pathlib import Path

import mimesis
import random

from PySide2.QtGui import QColor
from package.constantes import ACTIVITES, MATIERES
from package.files_path import FILES
from package.operations.api import convert_addition, create_operation
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


def f_annee(id=2019, niveau=None, td=False):
    id = id or random.randint(2018, 2020)
    if isinstance(id, db.Annee):
        id = id.id
    niveau = niveau or "cm" + str(id)
    with db_session:
        if db.Annee.exists(id=id):
            an = db.Annee[id]
        else:
            an = db.Annee(id=id, niveau=niveau)
        return an.to_dict() if td else an


def f_matiere(nom=None, annee=None):
    nom = nom or random.choice(["Français", "Math", "Anglais", "Histoire"])
    with db_session:
        annee = f_annee(annee)
        return db.Matiere(annee=annee, nom=nom)


#
# def f_activite(famille=None, matiere=None):
#     activites = ((0, "Exercice"), (1, "Leçon"), (2, "Divers"))
#     famille = famille if famille is not None else random.choice(activites)[0]
#     nom = activites[famille][1]
#     with db_session:
#         matiere = matiere or f_matiere()
#         return db.Activite(nom=nom, famille=famille, matiere=matiere)


def f_page(
    created=None, activite=None, titre=None, td=False, matiere=None, lastPosition=None
):
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
        item = db.Page(
            created=created, activite=activite, titre=titre, lastPosition=lastPosition
        )
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


def f_annotationText(
    relativeX=None,
    relativeY=None,
    text=None,
    td=False,
    section=None,
    color=None,
    underline=False,
):
    relativeX = relativeX or random.randint(0, 100) / 100
    relativeY = relativeY or random.randint(0, 100) / 100
    text = text or " ".join(gen.text.words(2))
    section = section or f_section().id
    color = QColor(color).rgba() if color else None

    with db_session:
        item = db.AnnotationText(
            relativeX=relativeX,
            relativeY=relativeY,
            text=text,
            section=section,
            color=color,
            underline=underline,
        )
        return item.to_dict() if td else item


def b_annotation(n, *args, **kwargs):
    return [f_annotationText(*args, **kwargs) for x in range(n)]


def _operation_section(model, string, created=None, page=None, position=0, td=False):
    with db_session:
        created = created or f_datetime()
        page = page or f_page(td=True)["id"]

        item = getattr(db, model)(
            string, created=created, page=page, position=position,
        )
        item.flush()
        return item.to_dict() if td else item


def f_additionSection(string=None, created=None, page=None, position=0, td=False):
    string = (
        string
        if string
        else random.choice(
            ["3+2", "8+9", "8,1+5", "23,45+365,2", "32+45", "87+76", "3458+23+827"]
        )
    )

    return _operation_section("AdditionSection", string, created, page, position, td)


def f_soustractionSection(string=None, created=None, page=None, position=0, td=False):
    string = (
        string
        if string
        else random.choice(["3-2", "12-3", "12-8", "87-76", "3458-827", "12-3,345"])
    )

    return _operation_section(
        "SoustractionSection", string, created, page, position, td
    )


def f_multiplicationSection(string=None, created=None, page=None, position=0, td=False):
    string = (
        string
        if string
        else random.choice(
            [
                "3*2",
                "25,1*1,48",
                "8*12",
                "87*76",
                "3458*827",
                "8,7*76",
                "345,8*8,27",
                "12*3,345",
            ]
        )
    )

    return _operation_section(
        "MultiplicationSection", string, created, page, position, td
    )


def f_divisionSection(string=None, created=None, page=None, position=0, td=False):
    string = (
        string
        if string
        else random.choice(["3/2", "251/14", "251/1,4", "13/6", "3458/82", "345,8/82",])
    )

    return _operation_section("DivisionSection", string, created, page, position, td)


def f_tableauSection(
    rows=None, columns=None, created=None, page=None, position=0, td=False
):
    rows = rows or random.randint(1, 10)
    columns = columns or random.randint(1, 10)
    created = created or f_datetime()
    page = page or f_page(td=True)["id"]
    with db_session:
        item = getattr(db, "TableauSection")(
            rows=rows, columns=columns, created=created, page=page, position=position,
        )
        item.flush()
        return item.to_dict() if td else item


@db_session
def populate_database(matieres_list=MATIERES, nb_page=100):
    annee = f_annee(id=2019, niveau="cm1")
    f_annee(id=2018, niveau="ce2")
    matieres = [f_matiere(x, annee) for x in matieres_list]

    activites = db.Activite.select()[:]
    for i in range(nb_page):
        a = f_page(activite=random.choice(activites))
        for x in range(random.randint(0, 14)):
            random.choice(
                [
                    # f_imageSection(page=a.id),
                    f_textSection(page=a.id),
                    f_additionSection(page=a.id),
                    f_soustractionSection(page=a.id),
                    f_multiplicationSection(page=a.id),
                    f_divisionSection(page=a.id),
                    f_tableauSection(page=a.id),
                ]
            )
