import json
from datetime import datetime
from typing import Tuple
from uuid import UUID, uuid4

from PyQt5.QtGui import QColor
from pony.orm import (
    Required,
    PrimaryKey,
    Optional,
    Set,
    Database,
    ObjectNotFound,
)

from mycartable.classeur.sections.operations.api import create_operation
from mycartable.exceptions import MyCartableOperationError
from .mixins import ColorMixin, PositionMixin, BackupAble


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
    class Section(db.Entity, PositionMixin, BackupAble):
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

        # def backup(self) -> dict:
        #     """
        #     Backup les data afin de pouvoir  restaurer le state de l'entity
        #     :return: dict
        #     """
        #     return self.to_dict()

        @classmethod
        def restore(cls, **data):
            """
            Restore le state d'une entity supprimée
            :param data:
            :return: None
            """
            annotations = data.pop("annotations", [])
            new_sec = super().restore(**data)
            for an in annotations:
                Annotation(**an)
            return new_sec

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
            dico["annotations"] = [a.to_dict() for a in self.annotations]

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

        @datas.setter
        def datas(self, value):
            self._datas = json.dumps(value)

        def to_dict(self, *args, **kwargs):
            dico = super().to_dict(*args, **kwargs)
            dico.pop("_datas")
            dico["datas"] = self.datas
            return dico

        def set(self, **kwargs):
            if datas := kwargs.pop("datas", None):
                self.datas = datas
            super().set(**kwargs)

    class OperationSection(TableDataSection):

        size = Required(int)
        virgule = Required(int)

        def __init__(self, string="", **kwargs):
            if string:
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
            else:
                _datas = kwargs.pop("datas")
                kwargs["_datas"] = json.dumps(_datas)
                super().__init__(**kwargs)

    class AdditionSection(OperationSection):
        pass

    class SoustractionSection(OperationSection):
        pass

    class MultiplicationSection(OperationSection):
        pass

    class DivisionSection(OperationSection):
        dividende = Optional(str)
        diviseur = Optional(str)
        quotient = Optional(str, default="")

        def __init__(self, string="", **kwargs):
            super().__init__(string=string, **kwargs)
            if string:
                datas = self.datas
                # pas optimal mais permet de conserver une cohérance avec les autres.
                # il faudrait shunter le dump pour ne pas recréer les Decimal
                # self.dividende = Decimal(datas["dividende"])
                self.dividende = datas["dividende"]
                self.diviseur = datas["diviseur"]
                self._datas = json.dumps(datas["datas"])
                self.size = self.columns * self.rows

    class EquationSection(Section):

        DEFAULT_CONTENT = ""
        DEFAULT_CURSEUR = 0

        content = Optional(str, default=DEFAULT_CONTENT, autostrip=False)
        curseur = Required(int, default=DEFAULT_CURSEUR)

    class Annotation(db.Entity, BackupAble):
        id = PrimaryKey(UUID, auto=True, default=uuid4)
        x = Required(float)
        y = Required(float)
        section = Required(Section)
        style = Optional(db.Style, default=db.Style, cascade_delete=True)

        def __new__(cls, *args, **kwargs):
            if classtype := kwargs.pop("classtype", None):
                cls = getattr(db, classtype)
            return super().__new__(cls)

        def __init__(self, **kwargs):
            if "style" in kwargs and isinstance(kwargs["style"], dict):
                kwargs["style"] = db.Style(**kwargs["style"])
            super().__init__(**kwargs)

        def as_type(self):
            return getattr(db, self.classtype)[self.id]

        def to_dict(self, **kwargs):
            dico = super().to_dict(**kwargs, related_objects=True)
            # dico.update(dico.pop("style").to_dict())
            dico["style"] = self.style.to_dict()
            dico["id"] = str(self.id)
            dico["section"] = str(self.section.id)
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

        def __init__(self, *args, modele="", create_cells=True, **kwargs):
            self._create_cells = create_cells
            self.modele = modele
            super().__init__(*args, **kwargs)

        def after_insert(self):
            if self._create_cells:
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

        """
        backup restore methods
        """

        def backup(self):
            dico = self.to_dict()
            dico["cells"] = self.get_cells()
            return dico

        @classmethod
        def restore(cls, **kwargs):
            cells = kwargs.pop("cells")
            new_t = cls(create_cells=False, **kwargs)
            for c in cells:
                TableauCell(**c)
            return new_t

        def restore_column(self, col, cells: list):
            """col est indicatif, x et y doivent être contenues dans cells"""
            self._insert_one_column(col)
            self._restore_cells(cells)

        def restore_line(self, col, cells: list):
            """col est indicatif, x et y doivent être contenues dans cells"""
            self._insert_one_line(col)
            self._restore_cells(cells)

        """
        Query cells method
        """

        def _get_cells(self):
            return self.cells.select().sort_by(TableauCell.y, TableauCell.x)

        def get_cells(self):
            return [x.to_dict() for x in self._get_cells()]

        def get_cells_par_ligne(self, row):
            return self._get_cells().page(
                row + 1, self.colonnes
            )  # page commence a 1 chez pony

        """"
        modify tableau line/column
        """

        def append_one_line(self) -> bool:
            return self.insert_one_line(self.lignes)

        def append_one_column(self) -> bool:
            return self.insert_one_column(self.colonnes)

        def insert_one_column(self, col: int) -> bool:
            self._insert_one_column(col)
            self._fill_new_column(col)
            return True

        def insert_one_line(self, line: int) -> bool:
            self._insert_one_line(line)
            self._fill_new_row(line)
            return True

        def remove_one_column(self, col) -> bool:
            self.colonnes = self.colonnes - 1

            if col < self.colonnes:
                for c in range(col, self.colonnes):
                    for l in range(self.lignes):
                        _agauche = TableauCell[self, l, c]
                        _adroite = TableauCell[self, l, c + 1]
                        _agauche.style = _adroite.style
                        _agauche.texte = _adroite.texte
            for l in range(self.lignes):
                TableauCell[self, l, self.colonnes].delete()
            return True

        def remove_one_line(self, line) -> bool:
            self.lignes = self.lignes - 1

            if line < self.lignes:
                for l in range(line, self.lignes):
                    for c in range(self.colonnes):

                        _avant = TableauCell[self, l, c]
                        _apres = TableauCell[self, l + 1, c]
                        _avant.style = _apres.style
                        _avant.texte = _apres.texte
            for c in range(self.colonnes):
                TableauCell[self, self.lignes, c].delete()

            return True

        """
        Private methods
        """

        def _fill_new_column(self, col: int):
            # on reset les nouvelles
            for l in range(self.lignes):
                cel = TableauCell[self, l, col]
                cel.texte = ""
                cel.style = db.Style()

        def _fill_new_row(self, line: int):
            # on reset les nouvelles
            for c in range(self.colonnes):
                cel = TableauCell[self, line, c]
                cel.texte = ""
                cel.style = db.Style()
            return True

        def _insert_one_column(self, col) -> bool:
            self.colonnes = self.colonnes + 1  # ne pas placer apres les fonctions

            # Ajout de la colonnes
            for c in range(self.lignes):
                TableauCell(tableau=self, y=c, x=self.colonnes - 1)
            # on décale les indexes
            if col < self.colonnes:
                for c in range(self.colonnes - 1, col, -1):
                    for l in range(self.lignes):
                        _agauche = TableauCell[self, l, c - 1]
                        _adroite = TableauCell[self, l, c]
                        _adroite.style = _agauche.style
                        _adroite.texte = _agauche.texte

        def _insert_one_line(self, line) -> bool:
            self.lignes = self.lignes + 1

            # Ajout de la ligne
            for c in range(self.colonnes):
                TableauCell(tableau=self, y=self.lignes - 1, x=c)

            if line < self.lignes:
                for l in range(self.lignes - 1, line, -1):
                    for c in range(self.colonnes):

                        _avant = TableauCell[self, l - 1, c]
                        _apres = TableauCell[self, l, c]
                        _apres.style = _avant.style
                        _apres.texte = _avant.texte

        def _restore_cells(self, cells: list):
            for cel in cells:
                base_cel = TableauCell[self, cel["y"], cel["x"]]
                base_cel.texte = cel["texte"]
                base_cel.style = db.Style(**cel["style"])

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

        @classmethod
        def restore(cls, **kwargs):
            zones = kwargs.pop("zones", [])
            new_f = cls(**kwargs)
            for z in zones:
                ZoneFrise.restore(**z)
            return new_f

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
        style = Optional(
            db.Style, default=db.Style, cascade_delete=True, column="style"
        )
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

        @classmethod
        def restore(cls, **kwargs):
            legendes = kwargs.pop("legendes", [])
            new_z = cls(**kwargs)
            for l in legendes:
                FriseLegende(**l)
            return new_z

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
