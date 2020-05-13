import json
from datetime import datetime
import re
from PySide2.QtGui import QColor
from descriptors import cachedproperty
from package.exceptions import MyCartableOperationError
from package.operations.api import create_operation
from pony.orm import Required, PrimaryKey, Optional, Set, select, count
from .root_db import db
from .mixins import ColorMixin


class Section(db.Entity):
    id = PrimaryKey(int, auto=True)
    created = Required(datetime, default=datetime.utcnow)
    modified = Optional(datetime)
    page = Required("Page")
    _position = Required(int)

    def __init__(self, *args, _position=None, page=None, position=None, **kwargs):
        # breakpoint()
        if _position is not None:  # doit être juste sinon erreur:
            pass
        else:
            if isinstance(page, db.Page):
                page = page.id
            query = select(s for s in db.Section if s.page.id == page)
            _position = query.count()

            if position is not None:
                _position = self.recalcule_position(_position, position, query=query)
        self.updating_position = False
        super().__init__(*args, _position=_position, page=page, **kwargs)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new):
        self._position = self.recalcule_position(self._position, new)

    def recalcule_position(self, old, new, query=None):
        query = query if query is not None else self.page.sections
        if new >= query.count():
            return query.count()
        if old == new:
            return
        elif old < new:
            for sec in query:
                if old < sec.position <= new and sec != self:
                    sec._position -= 1
        elif old > new:
            for sec in query:
                if new <= sec.position < old:
                    sec._position += 1
        return new

    def to_dict(self, *args, **kwargs):
        dico = super().to_dict(*args, **kwargs)
        dico["created"] = self.created.isoformat()
        dico["modified"] = self.modified.isoformat()
        dico["position"] = dico.pop("_position")
        return dico

    def before_insert(self):
        self.modified = self.created
        self.page.modified = self.modified

    def before_update(self):
        if getattr(self, "updating_position", None):
            self.updating_position = False
        else:
            self.modified = datetime.utcnow()
            self.page.modified = self.modified

    def before_delete(self):
        # backup la page pour after delete
        self._page = self.page.id

    def after_delete(self):
        page = db.Page.get(id=self._page)
        if page:
            n = 1
            for s in page.content:
                s.updating_position = True  # do not update modified on position
                s.position = n
                n += 1
            page.modified = datetime.utcnow()

    #
    # def _update_position(self):
    #     n = 1
    #     for x in self.page.content:
    #         if n == self._position:
    #             n += 1
    #         x.updating_position = True  # do not update modified on position
    #         x.position = n
    #         n += 1

    # def_update_position_new_remonte(self)


class ImageSection(Section):
    path = Required(str)
    annotations = Set("Annotation")

    def to_dict(self, **kwargs):
        return super().to_dict(with_collections=True)


class TextSection(Section):
    text = Optional(str, default="")


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
    @cachedproperty
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
        if self.virgule:
            return self.size - self.columns * 2, self.size - self.columns
        else:
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

    @cachedproperty
    def l_dividende(self):
        return len(self.dividende)

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

    @cachedproperty
    def diviseur_as_num(self):
        return self._as_num(self.diviseur)

    @cachedproperty
    def dividende_as_num(self):
        return self._as_num(self.dividende)


class EquationSection(Section):

    DEFAULT_CONTENT = ""
    DEFAULT_CURSEUR = 0

    content = Optional(str, default=DEFAULT_CONTENT, autostrip=False)
    curseur = Required(int, default=DEFAULT_CURSEUR)

    def set(self, *, content, curseur, **kwargs):
        super().set(**kwargs)
        if re.match("\s+", content):
            self.content = self.DEFAULT_CONTENT
            self.curseur = self.DEFAULT_CURSEUR
            return self.to_dict()
        else:
            self.content = content
            self.curseur = curseur
            return self.to_dict()


class Annotation(db.Entity):
    id = PrimaryKey(int, auto=True)
    relativeX = Required(float)
    relativeY = Required(float)
    section = Required(ImageSection)
    style = Optional(db.Style, default=db.Style, cascade_delete=True)

    def __init__(self, **kwargs):
        if "style" in kwargs and isinstance(kwargs["style"], dict):
            kwargs["style"] = db.Style(**kwargs["style"])
        super().__init__(**kwargs)

    def to_dict(self, *args, **kwargs):
        dico = super().to_dict(*args, **kwargs)
        if "style" in dico:  # ne pas l'ajouter sur a été exclude
            dico["style"] = self.style.to_dict()
        return dico

    def before_insert(self):
        self.section.before_update()

    def before_delete(self):
        if Section.exists(id=self.section.id):
            self.section.before_update()


class Stabylo(Annotation):
    relativeWidth = Required(float)
    relativeHeight = Required(float)


class AnnotationText(Annotation):
    text = Optional(str)


class TableauSection(Section):
    lignes = Required(int, default=0)
    colonnes = Required(int, default=0)
    cells = Set("TableauCell")

    def after_insert(self):
        for r in range(self.lignes):
            for c in range(self.colonnes):
                TableauCell(tableau=self, x=r, y=c)

    def to_dict(self, **kwargs):
        dico = super().to_dict(with_collections=True, **kwargs)
        return dico


class TableauCell(db.Entity, ColorMixin):

    x = Required(int)
    y = Required(int)
    texte = Optional(str)
    tableau = Required(TableauSection)
    PrimaryKey(tableau, x, y)
    style = Optional(db.Style, default=db.Style, cascade_delete=True)

    def __init__(self, **kwargs):

        if "style" in kwargs and isinstance(kwargs["style"], dict):
            kwargs["style"] = db.Style(**kwargs["style"])
        super().__init__(**kwargs)

    def to_dict(self, *args, **kwargs):
        dico = super().to_dict(*args, **kwargs)
        if "style" in dico:  # ne pas l'ajouter sur a été exclude
            dico["style"] = self.style.to_dict()
        return dico
