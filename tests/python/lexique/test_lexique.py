"""
Test LExique model
"""
import pytest
from PyQt5.QtCore import QModelIndex, Qt
from mycartable.lexique import LexiqueModel
from mycartable.lexique import LexiqueProxy, Lexique
from pony.orm import db_session


def test_init(fk):
    fk.f_locale(id="fr_FR")
    fk.f_locale(id="en_US")
    lexons = fk.bulk("f_lexon", 3, td=True)
    model = LexiqueModel()
    # reset
    assert model._data == [
        {"id": lexons[0]["id"], "traductions": [None, None]},
        {"id": lexons[1]["id"], "traductions": [None, None]},
        {"id": lexons[2]["id"], "traductions": [None, None]},
    ]
    assert model._locales == ["en_US", "fr_FR"]  # order respected
    # Rowcount
    assert model.rowCount(QModelIndex()) == 3
    # columnCount
    assert model.columnCount(QModelIndex()) == 2


@pytest.fixture()
def lexons(fk):
    with db_session:
        lex0 = lex = fk.db.Lexon.add(
            [
                {"content": "bonjour", "locale": "fr_FR"},
                {"content": "hello", "locale": "en_US"},
            ]
        )
        lex1 = lex = fk.db.Lexon.add(
            [
                {"content": "au revoir", "locale": "fr_FR"},
                {"content": "ciao", "locale": "it_IT"},
            ]
        )
        lex2 = lex = fk.db.Lexon.add(
            [
                {"content": "deux", "locale": "fr_FR"},
                {"content": "due", "locale": "it_IT"},
                {"content": "two", "locale": "en_US"},
            ]
        )
    return lex0, lex1, lex2


def test_data(lexons, fk):
    m = LexiqueModel()
    # ordre de local : en fr it
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "hello"
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "bonjour"
    assert m.data(m.index(0, 2), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 0), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 1), Qt.DisplayRole) == "au revoir"
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "ciao"
    assert m.data(m.index(2, 0), Qt.DisplayRole) == "two"
    assert m.data(m.index(2, 1), Qt.DisplayRole) == "deux"
    assert m.data(m.index(2, 2), Qt.DisplayRole) == "due"

    # ajout d'un lococale donc changement d'ordre
    fk.f_traduction(content="dos", locale="es_ES", lexon=lexons[2])

    m = LexiqueModel()
    # ordre de local :  en, ses,  frn it
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "hello"
    assert m.data(m.index(0, 1), Qt.DisplayRole) == ""
    assert m.data(m.index(0, 2), Qt.DisplayRole) == "bonjour"
    assert m.data(m.index(0, 3), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 0), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 1), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "au revoir"
    assert m.data(m.index(1, 3), Qt.DisplayRole) == "ciao"
    assert m.data(m.index(2, 0), Qt.DisplayRole) == "two"
    assert m.data(m.index(2, 1), Qt.DisplayRole) == "dos"
    assert m.data(m.index(2, 2), Qt.DisplayRole) == "deux"
    assert m.data(m.index(2, 3), Qt.DisplayRole) == "due"


def test_setdata(lexons, fk, qtbot):
    m = LexiqueModel()
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "ciao"
    with qtbot.waitSignal(m.dataChanged):
        assert m.setData(m.index(1, 2), "haha", Qt.EditRole)
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "haha"
    assert not m.setData(m.index(99, 99), "haha", Qt.EditRole)  # bad index
    assert not m.setData(m.index(1, 2), "haha", Qt.BackgroundRole)  # bad role
    assert not m.setData(m.index(1, 2), ["haha"], Qt.EditRole)  # base data format


"""
    TestLexique Proxy
"""


def test_sort(lexons):
    m = LexiqueModel()
    p = LexiqueProxy(parent=m, source=m)
    p.sort(1, Qt.AscendingOrder)
    # model inchangé
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "bonjour"
    assert m.data(m.index(1, 1), Qt.DisplayRole) == "au revoir"
    assert m.data(m.index(2, 1), Qt.DisplayRole) == "deux"
    # procy à jour
    assert p.data(p.index(0, 1), Qt.DisplayRole) == "au revoir"
    assert p.data(p.index(1, 1), Qt.DisplayRole) == "bonjour"
    assert p.data(p.index(2, 1), Qt.DisplayRole) == "deux"


"""
    Test Lexique Controlleur
"""


def test_lexique_init():
    l = Lexique()
    assert isinstance(l._model, LexiqueModel)
    assert isinstance(l._proxy, LexiqueProxy)
    assert l._proxy.sourceModel() is l._model
    assert l.model is l._model
    assert l.proxy is l._proxy
