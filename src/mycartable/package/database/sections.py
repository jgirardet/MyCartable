import json
from datetime import datetime
import re
from typing import Tuple
from uuid import UUID, uuid4

from PySide2.QtGui import QColor
from functools import cached_property
from package.exceptions import MyCartableOperationError
from package.operations.api import create_operation
from pony.orm import (
    Required,
    PrimaryKey,
    Optional,
    Set,
    Database,
    ObjectNotFound,
    Json,
)
from .mixins import ColorMixin, PositionMixin


def class_section(
    db: Database,
) -> Tuple[
    "Section",
    "ImageSection",
    "TextSection",
    "TableDataSection",
    "OperationSection",
    "AdditionSection",
    "SoustractionSection",
    "MultiplicationSection",
    "DivisionSection",
    "EquationSection",
    "Annotation",
    "AnnotationText",
    "AnnotationDessin",
    "TableauSection",
    "TableauCell",
    "FriseSection",
    "ZoneFrise",
    "FriseLegende",
]:
    class Section(db.Entity, PositionMixin):
        referent_attribute_name = "page"

        id = PrimaryKey(UUID, auto=True, default=uuid4)
        created = Required(datetime, default=datetime.utcnow)
        modified = Optional(datetime)
        page = Required("Page")
        _position = Required(int)
        annotations = Set("Annotation")

        def __repr__(self):
            return f"{self.__class__.__name__}[page={self.page.id}, position={self._position}]"

        def __new__(cls, *args, **kwargs):
            cls.base_class_position = Section
            return super().__new__(cls)

        def __init__(self, *args, page=None, position=None, **kwargs):
            with self.init_position(position, page) as _position:
                super().__init__(*args, _position=_position, page=page, **kwargs)

        def to_dict(self, **kwargs):
            dico = super().to_dict(exclude=["_position"], **kwargs)
            dico.update(
                {
                    "id": str(self.id),
                    "created": self.created.isoformat(),
                    "modified": self.modified.isoformat(),
                    "position": self.position,
                    "page": str(self.page.id),
                }
            )
            return dico

        def before_insert(self):
            self.modified = self.created
            self.page.modified = self.modified

        def before_update(self):
            self.modified = datetime.utcnow()
            self.page.reasonUpdate = True  # block page autoupdate
            self.page.modified = self.modified

        def before_delete(self):
            # backup la page pour after delete
            self.before_delete_position()

        def after_delete(self):
            try:
                page = self._positionbackup[0][self._positionbackup[1]]
            except ObjectNotFound:
                return  # should not fail if page aldready deleted
            self.after_delete_position()
            page.modified = datetime.utcnow()

    class ImageSection(Section):

        path = Required(str)

        def to_dict(self, **kwargs):
            dico = super().to_dict()
            dico["annotations"] = [annot.to_dict() for annot in self.annotations]
            return dico

    class TextSection(Section):
        text = Optional(str, default="<body></body>")

    class TableDataSection(Section):
        _datas = Required(str)
        rows = Required(int)
        columns = Required(int)

        @property
        def datas(self):
            return json.loads(self._datas)

        def to_dict(self, *args, **kwargs):
            dico = super().to_dict(*args, **kwargs)
            dico.pop("_datas")
            dico["datas"] = self.datas
            return dico

        def update_datas(self, index, value):
            datas = self.datas
            datas[index] = value
            self._datas = json.dumps(datas)

    class OperationSection(TableDataSection):

        size = Required(int)
        virgule = Required(int)

        def __init__(self, string, **kwargs):
            try:
                rows, columns, virgule, datas = create_operation(string)
            except TypeError:
                raise MyCartableOperationError(f"{string} est une entrée invalide")

            size = len(datas)
            super().__init__(
                rows=rows,
                columns=columns,
                _datas=json.dumps(datas),
                size=size,
                virgule=virgule,
                **kwargs,
            )

    class AdditionSection(OperationSection):
        def get_editables(self):
            first_line = {x for x in range(1, self.columns - 1)}
            last_line = {x for x in range(self.size - self.columns + 1, self.size)}
            res = first_line | last_line
            if self.virgule:
                virgule_ll = self.size - self.columns + self.virgule
                res = res - {self.virgule, virgule_ll}

            return res

    class SoustractionSection(OperationSection):
        @property
        def line_0(self):
            return self.datas[0 : self.columns]

        @property
        def line_1(self):
            return self.datas[self.columns : self.columns * 2]

        @property
        def line_2(self):
            return self.datas[self.columns * 2 :]

        def get_editables(self):
            res = set()

            def aide(res, debut, limite):
                i = debut
                while i < limite:
                    res.add(i)
                    i += 3

            if not self.virgule:
                if len(self.line_0) == len(self.line_1) == 4:
                    return {10}
                aide(res, self.columns * 2 + 2, self.size)  # troisieme ligne

            else:
                i = self.columns * 2 + 2
                flag = True
                while i < self.size:
                    if i >= self.virgule + (self.columns * 2) and flag:
                        i += 1
                        flag = False
                        continue
                    res.add(i)
                    i += 3
            return res

    class MultiplicationSection(OperationSection):
        @cached_property
        def n_chiffres(self):
            return int((self.rows - 4) / 2) or 1

        @property
        def line_0(self):
            start = self.n_chiffres * self.columns
            return self.datas[start : start + self.columns]

        @property
        def line_1(self):
            start = (1 + self.n_chiffres) * self.columns
            return self.datas[start : start + self.columns]

        @property
        def line_res_index(self):
            return self.size - self.columns, self.size

        @property
        def line_res(self):
            start, stop = self.line_res_index
            return self.datas[start:stop]

        def get_editables(self):
            res = set()
            if self.n_chiffres == 1:
                # pass
                start, stop = self.line_res_index
                res = set(range(start + 1, stop)) | set(range(1, self.columns - 1))
            else:
                # d'abord les retenues via les même index que ligne0 - le dernier
                indexes = [n for n, x in enumerate(self.line_0) if x.isdigit()][:-1]
                for i in range(self.n_chiffres):
                    k = self.columns * i
                    for j in indexes:
                        res.add(k + j)

                # ensuite on faite tout le reste
                reste = set(range(self.columns * (self.n_chiffres + 2), self.size))

                # on enleve la collone des signe
                colonne_signe = set(range(0, self.size, self.columns))
                reste = reste - colonne_signe

                res = res | reste

            return res

    class DivisionSection(OperationSection):
        dividende = Optional(str)
        # dividende = Optional(Decimal)
        diviseur = Optional(str)
        # diviseur = Optional(Decimal, scale=1, precision=8)
        quotient = Optional(str, default="")

        def __init__(self, string, **kwargs):
            super().__init__(string, **kwargs)
            datas = self.datas
            # pas optimal mais permet de conserver une cohérance avec les autres.
            # il faudrait shunter le dump pour ne pas recréer les Decimal
            # self.dividende = Decimal(datas["dividende"])
            self.dividende = datas["dividende"]
            self.diviseur = datas["diviseur"]
            self._datas = json.dumps(datas["datas"])
            self.size = self.columns * self.rows

        # @cached_property
        # def l_dividende(self):
        #     return len(self.dividende)

        def is_ligne_dividende(self, index):
            return 0 <= index < self.columns

        def is_ligne_last(self, index):
            return self.size - self.columns <= index < self.size

        def get_editables(self):
            # dividende = set(range(3, self.columns, 3)) # retenues du haut
            last = set(range(self.size - self.columns + 1, self.size, 3))
            milieu = set()
            for i in range(1, self.rows - 1):
                debut = i * self.columns
                impair = bool(i & 1)
                mini_index = 1
                # rangée des chiffres
                milieu.update(set(range(debut + mini_index, debut + self.columns, 3)))
                mini_index = 2 if impair else 3  # rien dans la premiere colone
                skip_end = 3 if impair else 0
                # # rangée des retenues
                # milieu.update(
                #     set(range(debut + mini_index, debut + self.columns - skip_end, 3))
                # )

            return milieu | last

        def _as_num(self, num):
            try:
                res = int(num)
            except ValueError:
                res = float(num)
            return res

        @cached_property
        def diviseur_as_num(self):
            return self._as_num(self.diviseur)

        @cached_property
        def dividende_as_num(self):
            return self._as_num(self.dividende)

    class EquationSection(Section):

        DEFAULT_CONTENT = ""
        DEFAULT_CURSEUR = 0

        content = Optional(str, default=DEFAULT_CONTENT, autostrip=False)
        curseur = Required(int, default=DEFAULT_CURSEUR)

        def set(self, *, content, curseur, **kwargs):
            super().set(**kwargs)
            if re.match(r"\s+", content):
                self.content = self.DEFAULT_CONTENT
                self.curseur = self.DEFAULT_CURSEUR
                return self.to_dict()
            else:
                self.content = content
                self.curseur = curseur
                return self.to_dict()

    class Annotation(db.Entity):
        id = PrimaryKey(UUID, auto=True, default=uuid4)
        x = Required(float)
        y = Required(float)
        section = Required(Section)
        # style = Optional("Style", default=lam, cascade_delete=True)
        style = Optional(db.Style, default=db.Style, cascade_delete=True)

        def __init__(self, **kwargs):
            if "style" in kwargs and isinstance(kwargs["style"], dict):
                kwargs["style"] = db.Style(**kwargs["style"])
            super().__init__(**kwargs)

        def as_type(self):
            return getattr(db, self.classtype)[self.id]

        def to_dict(self, **kwargs):
            dico = super().to_dict(**kwargs, related_objects=True)
            dico.update(dico.pop("style").to_dict())
            dico["id"] = str(self.id)
            return dico

        def set(self, **kwargs):
            if "style" in kwargs:
                style = kwargs.pop("style")
                self.style.set(**style)
            for k, v in kwargs.pop("attrs", {}).items():
                kwargs[k] = v

            super().set(**kwargs)

        def before_insert(self):
            self.section.before_update()

        def before_delete(self):
            if Section.exists(id=self.section.id):
                self.section.before_update()

    class AnnotationText(Annotation):
        text = Optional(str, autostrip=False)

    class AnnotationDessin(Annotation):
        width = Required(float)
        height = Required(float)
        tool = Required(str)
        startX = Required(float)
        startY = Required(float)
        endX = Required(float)
        endY = Required(float)
        points = Optional(str)
        """style : 
            fgColor: strokeStyle
            bgColor: fillStyle
            pointSize: lineWidth
            weight: opacity
        """

    class TableauSection(Section):
        lignes = Required(int, default=0)
        colonnes = Required(int, default=0)
        cells = Set("TableauCell")

        MODEL_COLOR_LINE0 = QColor("blue").lighter()
        MODEL_COLOR_COLONNE0 = QColor("grey").lighter()

        def __init__(self, *args, modele="", **kwargs):
            self.modele = modele
            super().__init__(*args, **kwargs)

        def after_insert(self):
            for r in range(self.lignes):
                for c in range(self.colonnes):
                    TableauCell(tableau=self, y=r, x=c)

            self.apply_model()

        def apply_model(self):
            if self.modele == "ligne0":
                for cel in self.get_cells_par_ligne(0):
                    cel.style.bgColor = self.MODEL_COLOR_LINE0
            elif self.modele == "colonne0":
                for y in range(self.lignes):
                    cel = TableauCell[self, y, 0]
                    cel.style.bgColor = self.MODEL_COLOR_COLONNE0
            elif self.modele == "ligne0-colonne0":
                for y in range(1, self.lignes):
                    cel = TableauCell[self, y, 0]
                    cel.style.bgColor = self.MODEL_COLOR_COLONNE0
                for cel in self.get_cells_par_ligne(0):
                    cel.style.bgColor = self.MODEL_COLOR_LINE0

        def get_cells(self):
            return self.cells.select().sort_by(TableauCell.y, TableauCell.x)

        def get_cells_par_ligne(self, row):
            return self.get_cells().page(
                row + 1, self.colonnes
            )  # page commence a 1 chez pony

        def insert_one_line(self, line):
            self.lignes = self.lignes + 1

            # Ajout de la ligne
            for c in range(self.colonnes):
                TableauCell(tableau=self, y=self.lignes - 1, x=c)

            if line < self.lignes:
                for l in range(self.lignes - 1, line, -1):
                    for c in range(self.colonnes):
                        TableauCell[self, l, c].set(
                            **TableauCell[self, l - 1, c].to_dict(exclude=["x", "y"])
                        )

            # on reset les nouvelles
            for c in range(self.colonnes):
                cel = TableauCell[self, line, c]
                cel.texte = ""
                cel.style = db.Style()

        def remove_one_line(self, line):
            self.lignes = self.lignes - 1

            if line < self.lignes:
                for i in range(line, self.lignes):
                    for c in range(self.colonnes):
                        TableauCell[self, i, c].set(
                            **TableauCell[self, i + 1, c].to_dict(exclude=["x", "y"])
                        )
            for c in range(self.colonnes):
                TableauCell[self, self.lignes, c].delete()

        def insert_one_column(self, col):
            self.colonnes = self.colonnes + 1

            # Ajout de la colonnes
            for c in range(self.lignes):
                TableauCell(tableau=self, y=c, x=self.colonnes - 1)

            if col < self.colonnes:
                for c in range(self.colonnes - 1, col, -1):
                    for l in range(self.lignes):
                        TableauCell[self, l, c].set(
                            **TableauCell[self, l, c - 1].to_dict(exclude=["x", "y"])
                        )

            # on reset les nouvelles
            for l in range(self.lignes):
                cel = TableauCell[self, l, col]
                cel.texte = ""
                cel.style = db.Style()

        def remove_one_column(self, col):
            self.colonnes = self.colonnes - 1

            if col < self.colonnes:
                for c in range(col, self.colonnes):
                    for l in range(self.lignes):
                        TableauCell[self, l, c].set(
                            **TableauCell[self, l, c + 1].to_dict(exclude=["x", "y"])
                        )
            for l in range(self.lignes):
                TableauCell[self, l, self.colonnes].delete()

        def append_one_line(self):
            self.insert_one_line(self.lignes)

        def append_one_column(self):
            self.insert_one_column(self.colonnes)

    class TableauCell(db.Entity, ColorMixin):
        """
        Cellule de Tableau
        """

        x = Required(int)
        y = Required(int)
        tableau = Required(TableauSection)
        PrimaryKey(tableau, y, x)
        texte = Optional(str)
        style = Optional(db.Style, default=db.Style, cascade_delete=True)

        def __init__(self, **kwargs):

            if "style" in kwargs and isinstance(kwargs["style"], dict):
                kwargs["style"] = db.Style(**kwargs["style"])
            super().__init__(**kwargs)

        def to_dict(self, *args, **kwargs):
            dico = super().to_dict(*args, **kwargs)
            if (
                "style" in dico
            ):  # pragma: no branch # ne pas l'ajouter sur a été exclude
                dico["style"] = self.style.to_dict()
            dico["tableau"] = str(self.tableau.id)
            return dico

        def set(self, **kwargs):
            if "style" in kwargs:
                style: dict = kwargs.pop("style")
                style.pop("styleId", None)
                self.style.set(**style)
            super().set(**kwargs)
            self.tableau.modified = datetime.utcnow()

    class FriseSection(Section):
        height = Required(int)
        zones = Set("ZoneFrise")
        titre = Optional(str)

        def to_dict(self, **kwargs):
            dico = super().to_dict(**kwargs)
            dico["zones"] = [
                x.to_dict() for x in self.zones.order_by(lambda x: x.position)
            ]
            return dico

    class ZoneFrise(db.Entity, PositionMixin):
        """
        ZoneFrise
        """

        referent_attribute_name = "frise"
        id = PrimaryKey(UUID, auto=True, default=uuid4)
        frise = Required(FriseSection)
        _position = Required(int)
        ratio = Required(float)
        texte = Optional(str)
        style = Optional(db.Style, default=db.Style, cascade_delete=True)
        # on utilise style.strikeout pour la position du separator True = "up", False = ""
        separatorText = Optional(str)
        legendes = Set("FriseLegende")

        def __init__(self, position=None, frise=None, **kwargs):

            if "style" in kwargs and isinstance(kwargs["style"], dict):
                kwargs["style"] = db.Style(**kwargs["style"])
            with self.init_position(position, frise) as _position:
                super().__init__(frise=frise, _position=_position, **kwargs)

        def before_delete(self):
            self.before_delete_position()

        def after_delete(self):
            self.after_delete_position()

        def to_dict(self, *args, **kwargs):
            dico = super().to_dict(*args, **kwargs)
            dico["position"] = dico.pop("_position")
            if (
                "style" in dico
            ):  # pragma: no branch # ne pas l'ajouter sur a été exclude
                dico["style"] = self.style.to_dict()
            dico["frise"] = str(self.frise.id)
            dico["id"] = str(self.id)
            dico["legendes"] = [p.to_dict() for p in self.legendes]
            return dico

        #
        def set(self, **kwargs):
            if "style" in kwargs:
                style: dict = kwargs.pop("style")
                style.pop("styleId", None)
                self.style.set(**style)
            if pos := kwargs.pop("position", None):
                self.position = pos
            super().set(**kwargs)
            self.frise.modified = datetime.utcnow()

    class FriseLegende(db.Entity):
        id = PrimaryKey(UUID, auto=True, default=uuid4)
        texte = Optional(str)
        relativeX = Required(float)
        side = Required(bool, sql_default=False)
        zone = Required(ZoneFrise)

        def to_dict(self, **kwargs):
            dico = super().to_dict(**kwargs)
            dico["zone"] = str(dico["zone"])
            dico["id"] = str(dico["id"])
            return dico

    return (
        Section,
        ImageSection,
        TextSection,
        TableDataSection,
        OperationSection,
        AdditionSection,
        SoustractionSection,
        MultiplicationSection,
        DivisionSection,
        EquationSection,
        Annotation,
        AnnotationText,
        AnnotationDessin,
        TableauSection,
        TableauCell,
        FriseSection,
        ZoneFrise,
        FriseLegende,
    )
