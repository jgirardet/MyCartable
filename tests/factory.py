import shutil
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

import mimesis
import random

from PyQt5.QtGui import QColor
from mycartable.defaults.matiere import (
    MATIERE_GROUPE_BASE,
    MATIERES_BASE,
)
from pony.orm import db_session, flush, Database

#
gen = mimesis.Generic("fr")
#
class Faker:
    def __init__(self, db: Database):
        self.db = db
        self.tmpdir = Path(tempfile.gettempdir()) / "mkdbdev"
        self.tmpdir.mkdir(exist_ok=True)

    def f_datetime(self, start=None, end=None, **kwargs):
        end = end or datetime.utcnow()
        start = start or end - timedelta(days=400)
        now = datetime.now()
        while True:
            res = gen.datetime.datetime(start=start.year, end=now.year + 1)
            if start < res <= end:
                return res

    #
    def f_annee(self, id=2019, niveau=None, td=False, **kwargs):

        id = id or random.randint(2018, 2020)
        if isinstance(id, self.db.Annee):
            id = id.id
        niveau = niveau or "cm" + str(id)
        with db_session:
            if self.db.Annee.exists(id=id):
                an = self.db.Annee[id]
            else:
                an = self.db.Annee(id=id, niveau=niveau)
            return an.to_dict() if td else an

    def f_groupeMatiere(self, nom=None, annee=None, td=False, **kwargs):

        annee = annee or self.f_annee(id=annee).id
        with db_session:
            if not self.db.Annee.get(id=annee):
                self.f_annee(id=annee)
        nom = nom or random.choice(["Français", "Math", "Anglais", "Histoire"])
        with db_session:
            item = self.db.GroupeMatiere(nom=nom, annee=annee, **kwargs)
            return item.to_dict() if td else item

    def b_groupeMatiere(self, nb, **kwargs):
        return [self.f_groupeMatiere(**kwargs) for i in range(nb)]

    def f_matiere(
        self,
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
        groupe_args = {}
        if isinstance(groupe, int):
            groupe_args["annee"] = groupe
            groupe = None

        groupe = groupe or self.f_groupeMatiere(**groupe_args)
        # breakpoint()
        flush()
        if isinstance(groupe, self.db.GroupeMatiere):
            groupe = groupe.id
        # white, red, blue, green, orange, pink
        with db_session:
            item = self.db.Matiere(
                nom=nom, groupe=groupe, _fgColor=_fgColor, _bgColor=_bgColor
            )

            return item.to_dict() if td else item

    def b_matiere(self, nb, groupe=None, **kwargs):
        if groupe:
            groupe = groupe if isinstance(groupe, (str, UUID)) else groupe.id
        else:
            groupe = self.f_groupeMatiere()

        return [self.f_matiere(groupe=groupe, **kwargs) for i in range(nb)]

    def f_activite(self, nom=None, matiere=None, td=False, **kwargs):

        nom = nom or gen.text.word()
        matiere = matiere or self.f_matiere()
        with db_session:
            item = self.db.Activite(
                nom=nom,
                matiere=matiere if isinstance(matiere, (str, UUID)) else matiere.id,
            )
            item.flush()
            return item.to_dict() if td else item

    def b_activite(self, nb, matiere=None, nom=None, **kwargs):
        if matiere:
            matiere = matiere if isinstance(matiere, (str, UUID)) else matiere.id
        else:
            matiere = self.f_matiere()
        return [self.f_activite(matiere=matiere, nom=nom) for i in range(nb)]

    def f_page(
        self,
        created=None,
        modified=None,
        activite=None,
        titre=None,
        td=False,
        lastPosition=None,
    ):
        """actvite int = id mais str = index"""
        if isinstance(activite, int):
            m = self.f_matiere(groupe=activite)
            activite = self.f_activite(matiere=m)
        activite = activite or self.f_activite()
        if isinstance(activite, self.db.Activite):
            activite = str(activite.id)
        created = created or self.f_datetime()
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        modified = modified or self.f_datetime()
        if isinstance(modified, str):
            modified = datetime.fromisoformat(modified)
        titre = titre if titre is not None else " ".join(gen.text.words(5))
        with db_session:
            item = self.db.Page(
                created=created,
                modified=modified,
                activite=activite,
                titre=titre,
                lastPosition=lastPosition,
            )
            item.flush()
            return item.to_dict() if td else item

    def b_page(self, n, *args, **kwargs):
        res = [self.f_page(*args, **kwargs) for p in range(n)]
        return res

    def _f_section(
        self, model, *args, created=None, page=None, position=None, td=False, **kwargs
    ):

        page = page or self.f_page().id
        created = created or self.f_datetime()

        with db_session:
            item = getattr(self.db, model)(
                *args,
                created=created,
                page=page,
                position=position,
                **kwargs,
            )
            dico = item.to_dict()  # valid la création
            return dico if td else item

    def f_section(self, **kwargs):
        with db_session:
            return self._f_section("Section", **kwargs)

    def b_section(self, n, *args, **kwargs):
        return [self.f_section(*args, **kwargs) for x in range(n)]

    def f_imageSection(self, path=None, **kwargs):
        tmp = None
        basepath = Path(__file__).parents[1] / "tests" / "resources"
        if path in ["tst_AnnotableImage.png", "sc1.png", "floodfill.png"]:
            path = basepath / path
        elif path:
            path = path
        else:
            path = (
                Path(__file__).parents[1]
                / "tests"
                / "resources"
                / random.choice(["tst_AnnotableImage.png", "sc1.png"])
            )
            tmp = self.tmpdir / (str(uuid.uuid4()) + path.suffix)
            shutil.copy(path, tmp)
        path = tmp if tmp else path
        return self._f_section("ImageSection", path=str(path), **kwargs)

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

    def f_textSection(self, text=None, **kwargs):
        text = text or self.HTML.replace(
            "\n", ""
        )  # gen.text.text(random.randint(0, 10))
        return self._f_section("TextSection", text=text, **kwargs)

    def f_annotation(
        self,
        x=None,
        y=None,
        section=None,
        # style=None,
        td=False,
        classtype=None,
        **kwargs,
    ):

        x = x or random.randrange(10, 100, 10) / 100
        y = y or random.randrange(10, 100, 10) / 100
        section = section or self.f_section().id
        classtype = classtype or self.db.Annotation
        with db_session:
            item = classtype(x=x, y=y, section=section, **kwargs)
            # if style:
            #     item.style = self.db.Style[style]
            return item.to_dict() if td else item

    def f_annotationText(self, text="", **kwargs):

        if text == "empty":
            text = ""
        elif not text:
            text = "".join(gen.text.words(2))
        return self.f_annotation(classtype=self.db.AnnotationText, text=text, **kwargs)

    def f_annotationDessin(
        self,
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
        tool = tool or random.choice(["rect", "fillrect", "ellipse", "trait"])
        startX = startX or random.randrange(10, 100, 10) / 100
        startY = startY or random.randrange(10, 100, 10) / 100
        endX = endX or random.randrange(10, 100, 10) / 100
        endY = endY or random.randrange(10, 100, 10) / 100
        return self.f_annotation(
            classtype=self.db.AnnotationDessin,
            width=width,
            height=height,
            tool=tool,
            startX=startX,
            startY=startY,
            endX=endX,
            endY=endY,
            **kwargs,
        )

    def b_annotation(self, n, *args, **kwargs):
        return [self.f_annotationText(*args, **kwargs) for x in range(n)]

    def f_operationSection(self, string=None, **kwargs):
        string = (
            string
            if string
            else random.choice(
                ["3+2", "8+9", "8,1+5", "23,45+365,2", "32+45", "87+76", "3458+23+827"]
            )
        )

        return self._f_section("OperationSection", string, **kwargs)

    def f_additionSection(self, string=None, **kwargs):
        string = (
            string
            if string
            else random.choice(
                ["3+2", "8+9", "8,1+5", "23,45+365,2", "32+45", "87+76", "3458+23+827"]
            )
        )

        return self._f_section("AdditionSection", string, **kwargs)

    def f_soustractionSection(self, string=None, **kwargs):
        string = (
            string
            if string
            else random.choice(["3-2", "12-3", "12-8", "87-76", "3458-827", "12-3,345"])
        )
        return self._f_section("SoustractionSection", string, **kwargs)

    def f_multiplicationSection(self, string=None, **kwargs):
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

        return self._f_section("MultiplicationSection", string, **kwargs)

    def f_divisionSection(self, string=None, **kwargs):
        string = (
            string
            if string
            else random.choice(
                [
                    "3/2",
                    "251/14",
                    "251/1,4",
                    "13/6",
                    "3458/82",
                    "345,8/82",
                ]
            )
        )

        return self._f_section("DivisionSection", string, **kwargs)

    def f_tableauSection(
        self, lignes=None, colonnes=None, modele="", **kwargs
    ) -> "TableauSection":
        lignes = lignes if lignes is not None else random.randint(0, 10)
        colonnes = colonnes if colonnes is not None else random.randint(0, 10)
        return self._f_section(
            "TableauSection", lignes=lignes, colonnes=colonnes, modele=modele, **kwargs
        )

    def f_tableauCell(self, x=0, y=0, texte=None, style=None, tableau=None, td=False):

        tableau = tableau or self.f_tableauSection(lignes=0, colonnes=0).id
        texte = texte or random.choice(["bla", "bli", "A", "1", "33"])

        with db_session:
            style = style or self.db.Style()
            flush()
            item = getattr(self.db, "TableauCell")(
                x=x,
                y=y,
                tableau=tableau,
                style=style if isinstance(style, (str, UUID)) else style.styleId,
                texte=texte,
            )
            item.flush()
            return item.to_dict() if td else item

    def f_equationSection(self, content=None, **kwargs):
        from mycartable.classeur.sections.equation import TextEquation

        content = (
            content or f"1{TextEquation.FSP}    \n{TextEquation.BARRE*2} + 1\n15    "
        )
        return self._f_section("EquationSection", content=content, **kwargs)

    def f_style(
        self,
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
            item = self.db.Style(
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

    def f_friseSection(self, height=None, titre="", **kwargs):
        height = height or 400
        return self._f_section("FriseSection", titre=titre, height=height, **kwargs)

    def f_zoneFrise(self, ratio=None, frise=None, texte=None, td=False, **kwargs):
        ratio = ratio or 0.2
        texte = texte or gen.text.word()
        if frise:
            frise = (
                frise
                if isinstance(frise, UUID)
                else frise
                if isinstance(frise, str)
                else frise.id
            )
        else:
            frise = self.f_friseSection().id
        with db_session:
            item = self.db.ZoneFrise(ratio=ratio, frise=frise, texte=texte, **kwargs)
            return item.to_dict() if td else item

    def b_zoneFrise(self, n, **kwargs):
        return [self.f_zoneFrise(**kwargs) for i in range(n)]

    def f_friseLegende(
        self, texte=None, relativeX=None, side=False, zone=None, td=False
    ):
        texte = texte or gen.text.word()
        relativeX = relativeX or random.random()
        zone = zone or self.f_zoneFrise().id
        with db_session:
            item = self.db.FriseLegende(
                texte=texte, relativeX=relativeX, side=side, zone=zone
            )
            return item.to_dict() if td else item

    def f_configuration(self, key=None, value=None, td=False):
        key = key or gen.text.word()
        value = value or gen.text.word()
        with db_session:
            item = self.db.Configuration.add(key, value)
            return item.to_dict() if td else item

    def f_lexon(self, td=False):
        with db_session:
            item = self.db.Lexon()
            return item.to_dict() if td else item

    def f_locale(self, id=None, td=False):
        id = id or random.choice(["fr_FR", "en_US", "es_ES", "it_IT", "de_DE"])
        with db_session:
            item = self.db.Locale.get(id=id) or self.db.Locale(id=id)
            return item.to_dict() if td else item

    def f_traduction(self, content=None, lexon=None, locale=None, td=False):
        content = content or gen.text.word()
        lexon = (
            (lexon if isinstance(lexon, int) else lexon.id)
            if lexon
            else self.f_lexon().id
        )
        if locale:
            locale = locale if isinstance(locale, str) else locale.id
        locale = self.f_locale(id=locale).id

        with db_session:
            item = self.db.Traduction(lexon=lexon, content=content, locale=locale)
            return item.to_dict() if td else item

    def bulk(self, fn: str, nb: int, **kwargs):
        return [getattr(self, fn)(**kwargs) for i in range(nb)]

    @db_session
    def populate_database(self):

        user = self.db.Utilisateur(nom="Lenom", prenom="Leprenom")
        annee = self.db.Annee(id=2019, niveau="cm1", user=user)
        # groupes = []
        compteur = 0
        for groupe in MATIERE_GROUPE_BASE:
            gr = self.db.GroupeMatiere(
                annee=annee, bgColor=groupe["bgColor"], nom=groupe["nom"]
            )
            for mat in MATIERES_BASE:
                if mat["groupe"] == groupe["id"]:
                    m = self.db.Matiere(groupe=gr, nom=mat["nom"])
                    compteur += 1
                    ac = self.db.Activite(matiere=m, nom="mdomak")
                    page = self.db.Page(titre="mojkù", activite=ac)
                    for x in range(random.randint(0, 8)):
                        random.choice(
                            [
                                # f_equationSection(
                                #     page=page.id,
                                #     # content=f"""1{TextEquation.FSP}            {TextEquation.FSP}12   1234
                                #     # ―― + 13 + 3 + ――― + ―――― + 1
                                #     # 15            234   789{TextEquation.FSP}    """,
                                # ),
                                #     f_tableauSection(page=page.id),
                                self.f_imageSection(page=page.id),
                                self.f_textSection(page=page.id),
                                # f16_additionSection(page=page.id),
                                # f_soustractionSection(page=page.id),
                                #     f_multiplicationSection(page=page.id),
                                #     f_divisionSection(page=page.id),
                            ]
                        )
            # groupes.append(gr)
