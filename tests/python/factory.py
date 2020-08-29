from datetime import datetime, timedelta
from pathlib import Path

#
import mimesis
import random

#
from PySide2.QtGui import QColor
from package.default_matiere import MATIERE_GROUPE, MATIERES
from pony.orm import db_session, flush

#
gen = mimesis.Generic("fr")
#
from package.database import db

from package.database.models import *


def f_datetime(start=None, end=None):
    end = end or datetime.utcnow()
    start = start or end - timedelta(days=400)
    now = datetime.now()

    while True:
        res = gen.datetime.datetime(start=start.year, end=now.year + 1)
        if start < res <= end:
            return res


def f_user(nom="lenom", prenom="leprenom", td=False):
    with db_session:
        user = Utilisateur.user() or Utilisateur(nom=nom, prenom=prenom)
        return user.to_dict() if td else user


#
def f_annee(id=2019, niveau=None, user=None, td=False):
    id = id or random.randint(2018, 2020)
    if isinstance(id, db.Annee):
        id = id.id
    niveau = niveau or "cm" + str(id)
    with db_session:
        if user is not None:
            user = user if isinstance(user, str) else str(user.id)
        else:
            user = f_user()
            # user = Utilisateur.user()
        if db.Annee.exists(id=id):
            an = db.Annee[id]
        else:
            an = db.Annee(id=id, niveau=niveau, user=user)
        return an.to_dict() if td else an


def f_groupeMatiere(nom=None, annee=None, **kwargs):
    annee = annee or f_annee(id=annee).id
    with db_session:
        if not Annee.get(id=annee):
            f_annee(id=annee)
    nom = nom or random.choice(["Français", "Math", "Anglais", "Histoire"])
    with db_session:
        return db.GroupeMatiere(nom=nom, annee=annee, **kwargs)


def b_groupeMatiere(nb, **kwargs):

    return [f_groupeMatiere(**kwargs) for i in range(nb)]


def f_matiere(
    nom=None,
    groupe=None,
    bgColor=None,
    fgColor=None,
    _bgColor=None,
    _fgColor=None,
    td=False,
):
    nom = nom or random.choice(["Français", "Math", "Anglais", "Histoire"])
    color_codes = [
        4294967295,
        4294901760,
        4278190335,
        4278222848,
        4294944000,
        4294951115,
    ]
    if fgColor:
        _fgColor = QColor(fgColor).rgba()
    else:
        _fgColor = _fgColor or random.choice(color_codes)
    if bgColor:
        _bgColor = QColor(bgColor).rgba()
    else:
        _bgColor = _bgColor or random.choice(color_codes)
    groupe = groupe or f_groupeMatiere()
    flush()
    if isinstance(groupe, db.GroupeMatiere):
        groupe = groupe.id
    # white, red, blue, green, orange, pink
    with db_session:
        item = db.Matiere(nom=nom, groupe=groupe, _fgColor=_fgColor, _bgColor=_bgColor)

        return item.to_dict() if td else item


def b_matiere(nb, groupe=None, **kwargs):
    if groupe:
        groupe = groupe if isinstance(groupe, (str, UUID)) else groupe.id
    else:
        groupe = f_groupeMatiere()

    return [f_matiere(groupe=groupe, **kwargs) for i in range(nb)]


def f_activite(nom=None, matiere=None, td=False):
    nom = nom or gen.text.word()
    matiere = matiere or f_matiere()
    with db_session:
        item = db.Activite(
            nom=nom, matiere=matiere if isinstance(matiere, (str, UUID)) else matiere.id
        )
        item.flush()
        return item.to_dict() if td else item


def b_activite(nb, matiere=None, nom=None):
    if matiere:
        matiere = matiere if isinstance(matiere, (str, UUID)) else matiere.id
    else:
        matiere = f_matiere()
    return [f_activite(matiere=matiere, nom=nom) for i in range(nb)]


def f_page(created=None, activite=None, titre=None, td=False, lastPosition=None):
    """actvite int = id mais str = index"""
    activite = activite or f_activite()
    if isinstance(activite, Activite):
        activite = str(activite.id)
    created = created or f_datetime()
    titre = titre or " ".join(gen.text.words(5))
    with db_session:
        item = db.Page(
            created=created, activite=activite, titre=titre, lastPosition=lastPosition
        )
        item.flush()
        return item.to_dict() if td else item


def b_page(n, *args, **kwargs):
    res = [f_page(*args, **kwargs) for p in range(n)]
    return res


def _f_section(
    model, *args, created=None, page=None, position=None, td=False, **kwargs,
):
    page = page or f_page().id
    created = created or f_datetime()

    with db_session:
        item = getattr(db, model)(
            *args, created=created, page=page, position=position, **kwargs,
        )
        dico = item.to_dict()  # valid la création
        return dico if td else item


def f_section(**kwargs):
    with db_session:
        return _f_section("Section", **kwargs)


def b_section(n, *args, **kwargs):
    return [f_section(*args, **kwargs) for x in range(n)]


def f_imageSection(path=None, **kwargs):

    path = path or str(
        Path(__file__).parents[4].absolute()
        / "tests"
        / "resources"
        / random.choice(["tst_AnnotableImage.png", "sc1.png"])
    )

    return _f_section("ImageSection", path=path, **kwargs)


HTML = """
<body>
<p>ligne normale</p>
<h1>titre</h1>
<h2>titre seconde</h2>
<p>debut de ligne <span style="color: red;">rouge</span> suite de ligne</p>
<h3>titre seconde</h3>
<h4>titre seconde</h4>
<p>du style en fin de <span style="color: purple;">lingne</span></p>
<p>debut de ligne <span style="color: red;">rouge</span> suite de ligne</p>
</body>
"""


HTML2 = """
<body>
<p>ligne normale</p>
</body>
"""


def f_textSection(text=None, **kwargs):
    text = text or HTML.replace("\n", "")  # gen.text.text(random.randint(0, 10))
    return _f_section("TextSection", text=text, **kwargs)


def f_annotation(
    x=None, y=None, section=None, style=None, td=False, classtype=None, **kwargs
):
    x = x or random.randrange(10, 100, 10) / 100
    y = y or random.randrange(10, 100, 10) / 100
    section = section or f_section().id
    classtype = classtype or db.Annotation
    with db_session:
        item = classtype(x=x, y=y, section=section, **kwargs)
        if style:
            item.style = db.Style[style]
        return item.to_dict() if td else item


def f_annotationText(text="", **kwargs):
    if text == "empty":
        text = ""
    elif not text:
        text = "".join(gen.text.words(2))
    return f_annotation(classtype=db.AnnotationText, text=text, **kwargs)


def f_annotationDessin(
    width=None,
    height=None,
    tool=None,
    startX=None,
    startY=None,
    endX=None,
    endY=None,
    **kwargs,
):
    width = width or random.randrange(10, 100, 10) / 100
    height = height or random.randrange(10, 100, 10) / 100
    tool = random.choice(["rect", "fillrect", "ellipse", "trait"])
    startX = startX or random.randrange(10, 100, 10) / 100
    startY = startY or random.randrange(10, 100, 10) / 100
    endX = endX or random.randrange(10, 100, 10) / 100
    endY = endY or random.randrange(10, 100, 10) / 100
    return f_annotation(
        classtype=db.AnnotationDessin,
        width=width,
        height=height,
        tool=tool,
        startX=startX,
        startY=startY,
        endX=endX,
        endY=endY,
        **kwargs,
    )


def b_annotation(n, *args, **kwargs):
    return [f_annotationText(*args, **kwargs) for x in range(n)]


def f_additionSection(string=None, **kwargs):
    string = (
        string
        if string
        else random.choice(
            ["3+2", "8+9", "8,1+5", "23,45+365,2", "32+45", "87+76", "3458+23+827"]
        )
    )

    return _f_section("AdditionSection", string, **kwargs)


def f_soustractionSection(string=None, **kwargs):
    string = (
        string
        if string
        else random.choice(["3-2", "12-3", "12-8", "87-76", "3458-827", "12-3,345"])
    )
    return _f_section("SoustractionSection", string, **kwargs)


def f_multiplicationSection(string=None, **kwargs):
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

    return _f_section("MultiplicationSection", string, **kwargs)


def f_divisionSection(string=None, **kwargs):
    string = (
        string
        if string
        else random.choice(["3/2", "251/14", "251/1,4", "13/6", "3458/82", "345,8/82",])
    )

    return _f_section("DivisionSection", string, **kwargs)


def f_tableauSection(lignes=None, colonnes=None, modele="", **kwargs) -> TableauSection:
    lignes = lignes if lignes is not None else random.randint(0, 10)
    colonnes = colonnes if colonnes is not None else random.randint(0, 10)
    return _f_section(
        "TableauSection", lignes=lignes, colonnes=colonnes, modele=modele, **kwargs
    )


def f_tableauCell(x=0, y=0, texte=None, style=None, tableau=None, td=False):
    tableau = tableau or f_tableauSection(lignes=0, colonnes=0).id
    texte = texte or random.choice(["bla", "bli", "A", "1", "33"])

    with db_session:
        style = style or db.Style()
        flush()
        item = getattr(db, "TableauCell")(
            x=x,
            y=y,
            tableau=tableau,
            style=style if isinstance(style, (str, UUID)) else style.styleId,
            texte=texte,
        )
        item.flush()
        return item.to_dict() if td else item


from package.database_mixins.equation_mixin import TextEquation


def f_equationSection(
    content=f"1{TextEquation.FSP}    \n{TextEquation.BARRE*2} + 1\n15    ", **kwargs
):
    return _f_section("EquationSection", content=content, **kwargs)


def f_style(
    fgColor=None,
    bgColor=None,
    family="",
    underline=False,
    pointSize=None,
    strikeout=False,
    weight=None,
    td=False,
    **kwargs,
):

    with db_session:
        item = Style(
            fgColor=fgColor,
            bgColor=bgColor,
            family=family,
            underline=underline,
            pointSize=pointSize,
            strikeout=strikeout,
            weight=weight,
            **kwargs,
        )
        return item.to_dict() if td else item


@db_session
def populate_database(matieres_list=MATIERES, nb_page=100):
    user = db.Utilisateur(nom="Lenom", prenom="Leprenom")
    annee = Annee(id=2019, niveau="cm1", user=user)
    Annee(id=2018, niveau="ce2", user=user)
    [db.GroupeMatiere(**x, annee=annee.id) for x in MATIERE_GROUPE]
    flush()
    matieres = [db.Matiere(**x) for x in matieres_list]
    flush()
    #
    for m in matieres:
        for i in range(3):
            f_activite(matiere=m.id)


#
#     activites = db.Activite.select()[:]
#     for i in range(nb_page):
#         a = f_page(activite=random.choice(activites))
#         for x in range(random.randint(0, 8)):
#             random.choice(
#                 [
#                     f_equationSection(
#                         page=a.id,
#                         # content=f"""1{TextEquation.FSP}            {TextEquation.FSP}12   1234
#                         # ―― + 13 + 3 + ――― + ―――― + 1
#                         # 15            234   789{TextEquation.FSP}    """,
#                     ),
#                     f_tableauSection(page=a.id),
#                     f_imageSection(page=a.id),
#                     f_textSection(page=a.id),
#                     f_additionSection(page=a.id),
#                     f_soustractionSection(page=a.id),
#                     f_multiplicationSection(page=a.id),
#                     f_divisionSection(page=a.id),
#                 ]
#             )
