import random
from typing import Optional, Any, Union, Dict

import flag
from PyQt5.QtCore import (
    QModelIndex,
    Qt,
    QSortFilterProxyModel,
    pyqtProperty,
    QObject,
    QLocale,
    pyqtSlot,
    QRegExp,
    pyqtSignal,
)
from PyQt5.QtQuick import QQuickItem
from mycartable.types.collections import DtbTableModel


def country_flag(locale: QLocale):
    return flag.flag(locale.name().split("_")[-1])


class LexiqueModel(DtbTableModel):
    activesLocalesChanged = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _reset(self):
        self._data = []
        data = self._dtb.execDB("Lexon", None, "all")
        self._actives_locales = sorted(self._dtb.getConfig("actives_locales"))
        self._availables_locales = sorted(self._dtb.getConfig("availables_locales"))
        for row in data:
            self._format_internal_data(row)
            self._data.append(row)

    def _after_reset(self):
        self.activesLocalesChanged.emit()

    def _format_internal_data(self, lexon: dict):
        # on crée les cases vides qui n'ont pas de traduction
        res = [None] * len(self._actives_locales)
        for t in lexon["traductions"]:
            if t["locale"] in self.activesLocales:
                res[self._actives_locales.index(t["locale"])] = t
        lexon["traductions"] = res

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._actives_locales)

    def data(self, index: QModelIndex, role: int) -> Optional[str]:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            if trad := self._data[index.row()]["traductions"][index.column()]:
                return trad["content"]
            else:
                return ""

    def setData(self, index: QModelIndex, value: Any, role: int) -> Union[bool, str]:
        if index.isValid():
            if role == Qt.EditRole:
                row = self._data[index.row()]
                if trad := row["traductions"][index.column()]:
                    res = self._dtb.setDB("Traduction", trad["id"], {"content": value})
                else:
                    res = self._dtb.addDB(
                        "Traduction",
                        {
                            "lexon": row["id"],
                            "content": value,
                            "locale": self.activesLocales[index.column()],
                        },
                    )
                if res:
                    self._data[index.row()]["traductions"][index.column()] = res
                    self.dataChanged.emit(index, index)
                    return True

        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if role == Qt.DisplayRole and 0 <= section < len(self._actives_locales):
            locale = QLocale(self._actives_locales[section])
            drapeau = self._country_flag(locale)
            # nom = locale.nativeLanguageName().split(" ")[-1].upper()
            return f"{drapeau} {locale.nativeLanguageName()} {drapeau}"

    def _country_flag(self, locale: QLocale):
        return flag.flag(locale.name().split("_")[-1])

    @pyqtProperty("QVariantList", notify=activesLocalesChanged)
    def activesLocales(self):
        return self._actives_locales

    @pyqtProperty("QVariantList", constant=True)
    def availablesLocales(self):
        res = []
        for l in self._availables_locales:
            loc = QLocale(l)
            res.append(
                {
                    "id": loc.name(),
                    "nom": f"{country_flag(loc)} {loc.nativeLanguageName()}",
                    "active": l in self._actives_locales,
                }
            )

        return res

    @property
    def model_data(self) -> list:
        return self._data

    def addLexon(self, trads: list) -> bool:
        if new_lexon := self._dtb.execDB("Lexon", None, "add", trads, td=True):
            self._format_internal_data(new_lexon)
            self._data.append(new_lexon)
            return True

        return False

    def _removeRows(self, row, count):
        for lex in self._data[row : row + 1 + count]:
            self._dtb.delDB("Lexon", lex["id"])
        self._data = self._data[:row] + self._data[row + count + 1 :]


class LexiqueProxy(QSortFilterProxyModel):
    def __init__(self, parent=None, source=None, **kwargs):
        super().__init__(parent=parent)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setSourceModel(source)

    def removeRow(self, row: int, parent=QModelIndex()) -> bool:
        model_index = self.mapToSource(self.index(row, 0))
        self.beginRemoveRows(QModelIndex(), row, row)
        self.sourceModel().removeRow(model_index.row())
        self.endRemoveRows()


class Quizz(QObject):
    bonneReponse = pyqtSignal()
    propositionChanged = pyqtSignal()
    questionChanged = pyqtSignal()
    questionFlagChanged = pyqtSignal()
    reponseChanged = pyqtSignal()
    reponseFlagChanged = pyqtSignal()
    scoreChanged = pyqtSignal()
    showErrorChanged = pyqtSignal()
    totalChanged = pyqtSignal()

    def __init__(self, parent, model):
        super().__init__(parent)
        self._model = model
        self.reset()

    def reset(self):
        self.score = 0
        self.total = 0
        self.question = ""
        self.reponse = ""
        self.questionFlag = ""
        self.reponseFlag = ""
        self.showError = False
        self.proposition = ""
        self._data = self._model.model_data

    def _new_question(self):
        self.showError = False
        self.proposition = ""
        content = None
        compteur = 0
        while not content and compteur < 100:
            # permet d'éviter le problème où il n'y a qu'un seul trad
            # le compteur évite la boucle infinie
            content = self._question_provider()
            compteur += 1
        if not content:
            return
        self.question = content["question"]
        self.questionFlag = country_flag(QLocale(content["question_locale"]))
        self.reponse = content["reponse"]
        self.reponseFlag = country_flag(QLocale(content["reponse_locale"]))

    def _question_provider(self) -> dict:
        res = {}
        trads = list(filter(lambda x: x, random.choice(self._data)["traductions"]))
        if len(trads) < 2:
            return
        q = trads.pop(random.randint(0, len(trads) - 1))
        res["question"] = q["content"]
        res["question_locale"] = q["locale"]
        r = trads.pop(random.randint(0, len(trads) - 1))
        res["reponse"] = r["content"]
        res["reponse_locale"] = r["locale"]
        return res

    """
    Qt Property
    """

    @pyqtProperty(bool, notify=showErrorChanged)
    def showError(self):
        return self._showError

    @showError.setter
    def showError(self, value: bool):
        self._showError = value
        self.showErrorChanged.emit()

    @pyqtProperty(str, notify=questionChanged)
    def question(self):
        return self._question

    @question.setter
    def question(self, value: str):
        self._question = value
        self.questionChanged.emit()

    @pyqtProperty(str, notify=questionFlagChanged)
    def questionFlag(self):
        return self._questionFlag

    @questionFlag.setter
    def questionFlag(self, value: str):
        self._questionFlag = value
        self.questionFlagChanged.emit()

    @pyqtProperty(str, notify=reponseChanged)
    def reponse(self):
        return self._reponse

    @reponse.setter
    def reponse(self, value: str):
        self._reponse = value
        self.reponseChanged.emit()

    @pyqtProperty(str, notify=propositionChanged)
    def proposition(self):
        return self._proposition

    @proposition.setter
    def proposition(self, value: str):
        self._proposition = value
        self.propositionChanged.emit()

    @pyqtProperty(str, notify=reponseFlagChanged)
    def reponseFlag(self):
        return self._reponseFlag

    @reponseFlag.setter
    def reponseFlag(self, value: str):
        self._reponseFlag = value
        self.reponseFlagChanged.emit()

    @pyqtProperty(int, notify=scoreChanged)
    def score(self):
        return self._score

    @score.setter
    def score(self, value: int):
        self._score = value
        self.scoreChanged.emit()

    @pyqtProperty(int, notify=totalChanged)
    def total(self):
        return self._total

    @total.setter
    def total(self, value: int):
        self._total = value
        self.totalChanged.emit()

    """
    Qt Slots
    """

    @pyqtSlot(result=bool)
    def checkReponse(self):
        if self._reponse == self.proposition:
            self.total += 1
            if not self.showError:
                self.score += 1
                self.bonneReponse.emit()
            self._new_question()
            return True
        else:
            self.showError = True
        return False

    @pyqtSlot()
    def start(self):
        self.reset()
        self._new_question()


class Lexique(QQuickItem):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)
        self._model = LexiqueModel(parent=self)
        self._proxy = LexiqueProxy(parent=self, source=self._model)
        self._quizz = Quizz(parent=self, model=self._model)

    """ "
    Qt Properties
    """

    @pyqtProperty(QObject, constant=True)
    def model(self) -> LexiqueModel:
        return self._model

    @pyqtProperty(QObject, constant=True)
    def proxy(self) -> LexiqueProxy:
        return self._proxy

    @pyqtProperty(QObject, constant=True)
    def quizz(self) -> Quizz:
        return self._quizz

    """"
    Qt SLot
    """

    @pyqtSlot("QVariantList", result=bool)
    def addLexon(self, trads: list) -> bool:
        if self.model.addLexon(trads):
            self._proxy.beginResetModel()
            self.model.insertRow(0)
            self._proxy.endResetModel()
            self._proxy.sort(0, Qt.AscendingOrder)
            return True
        self._proxy.sort(0, Qt.AscendingOrder)
        return False

    @pyqtSlot(int, str)
    def filter(self, index: int, value: str):
        self.proxy.setFilterKeyColumn(index)
        self.proxy.setFilterRegExp(
            QRegExp(value, Qt.CaseInsensitive, QRegExp.FixedString)
        )
        self._proxy.sort(index, Qt.AscendingOrder)

    @pyqtSlot(int)
    def doSort(self, col: int):
        if col == self._proxy.sortColumn():
            self._proxy.sort(col, int(not self._proxy.sortOrder()))
        else:
            self._proxy.sort(col, Qt.AscendingOrder)

    @pyqtSlot(str, bool)
    def updateActivesLocales(self, locale_id: str, checked: bool):
        if checked and locale_id not in self._model.activesLocales:
            locales = self._model.activesLocales + [locale_id]
        elif not checked and locale_id in self.model.activesLocales:
            locales = list(self._model.activesLocales)
            locales.pop(locales.index(locale_id))
        else:
            return
        self._model._dtb.setConfig("actives_locales", locales)
        self._proxy.beginResetModel()
        self._model.reset()
        self._proxy.endResetModel()
        self._proxy.sort(0, Qt.AscendingOrder)

    @pyqtSlot(int)
    def removeRow(self, row: int):
        self._proxy.removeRow(row)
