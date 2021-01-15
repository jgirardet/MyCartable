"""
Test LExique model
"""
import pytest
from PyQt5.QtCore import QModelIndex, Qt
from mycartable.lexique import LexiqueModel
from mycartable.lexique import LexiqueProxy, Lexique
from pony.orm import db_session


@pytest.fixture()
def set_locales(ddbr):
    with db_session:
        ddbr.Configuration.add("actives_locales", ["fr_FR", "en_GB"])


pytestmark = pytest.mark.usefixtures("set_locales")


def test_init(fk):
    fk.f_locale(id="fr_FR")
    fk.f_locale(id="en_GB")
    lexons = fk.bulk("f_lexon", 3, td=True)
    model = LexiqueModel()
    # reset
    assert model._data == [
        {"id": lexons[0]["id"], "traductions": [None, None]},
        {"id": lexons[1]["id"], "traductions": [None, None]},
        {"id": lexons[2]["id"], "traductions": [None, None]},
    ]
    assert model.activesLocales == ["en_GB", "fr_FR"]  # order respected
    assert model.availablesLocales == [
        {"active": False, "id": "de_DE", "nom": "🇩🇪 Deutsch"},
        {"active": True, "id": "en_GB", "nom": "🇬🇧 British English"},
        {"active": False, "id": "es_ES", "nom": "🇪🇸 español de España"},
        {"active": True, "id": "fr_FR", "nom": "🇫🇷 français"},
        {"active": False, "id": "it_IT", "nom": "🇮🇹 italiano"},
    ]

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
                {"content": "hello", "locale": "en_GB"},
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
                {"content": "two", "locale": "en_GB"},
            ]
        )
    return lex0, lex1, lex2


def test_data(lexons, fk):
    with db_session:
        fk.db.Configuration.add("actives_locales", ["fr_FR", "en_GB", "it_IT"])
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
    with db_session:
        fk.db.Configuration.add("actives_locales", ["fr_FR", "en_GB", "it_IT", "es_ES"])
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
    with db_session:
        fk.db.Configuration.add("actives_locales", ["fr_FR", "en_GB", "it_IT"])
    m = LexiqueModel()
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "ciao"
    with qtbot.waitSignal(m.dataChanged):
        assert m.setData(m.index(1, 2), "haha", Qt.EditRole)
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "haha"

    # empty case
    with qtbot.waitSignal(m.dataChanged):
        assert m.setData(m.index(1, 0), "haha", Qt.EditRole)
    assert m.data(m.index(1, 0), Qt.DisplayRole) == "haha"

    assert not m.setData(m.index(99, 99), "haha", Qt.EditRole)  # bad index
    assert not m.setData(m.index(1, 2), "haha", Qt.BackgroundRole)  # bad role
    assert not m.setData(m.index(1, 2), ["haha"], Qt.EditRole)  # base data format


def test_headerData(lexons, ddbr):
    with db_session:
        ddbr.Configuration.add("actives_locales", ["fr_FR", "en_GB", "it_IT"])
    m = LexiqueModel()
    assert "English" in m.headerData(0, Qt.Horizontal, Qt.DisplayRole)
    assert "français" in m.headerData(1, Qt.Horizontal, Qt.DisplayRole)
    assert "italiano" in m.headerData(2, Qt.Horizontal, Qt.DisplayRole)


"""
    TestLexique Proxy
"""


def test_map_from_source(lexons):
    l = Lexique()
    m = l._model
    p = l._proxy
    p.sort(0, Qt.AscendingOrder)
    assert p.mapFromSource(m.index(0, 0)) == p.index(1, 0)

    assert p.mapToSource(p.index(0, 0)) == m.index(1, 0)


def test_removeRow(lexons, ddbr, qtbot):
    l = Lexique()
    with qtbot.waitSignal(l._proxy.rowsAboutToBeRemoved):
        l._proxy.removeRow(1)
    assert l._model.rowCount(QModelIndex()) == 2
    assert l._model._data[0]["id"] == str(lexons[0].id)
    assert l._model._data[1]["id"] == str(lexons[2].id)
    with db_session:
        assert ddbr.Lexon.select().count() == 2
        assert not ddbr.Lexon.get(id=lexons[1].id)


"""
    Test Lexique Controlleur
"""


def test_lexique_init(qtbot):
    l = Lexique()
    assert isinstance(l._model, LexiqueModel)
    assert isinstance(l._proxy, LexiqueProxy)
    assert l._proxy.sourceModel() is l._model
    assert l.model is l._model
    assert l.proxy is l._proxy


def test_add_lexon(lexons):
    l = Lexique()
    assert l.model.rowCount(QModelIndex()) == 3
    assert l.addLexon(
        [
            {"content": "trois", "locale": "fr_FR"},
            {"content": "three", "locale": "en_GB"},
        ]
    )
    assert l.model.rowCount(QModelIndex()) == 4
    assert l.model._data[-1]["traductions"][0]["content"] == "three"
    assert l.model._data[-1]["traductions"][1]["content"] == "trois"


def test_doSort(lexons):
    l = Lexique()
    l.doSort(1)  # debut column 9, sortorder0
    # procy à jour
    assert l._proxy.data(l._proxy.index(0, 1), Qt.DisplayRole) == "au revoir"
    assert l._proxy.data(l._proxy.index(1, 1), Qt.DisplayRole) == "bonjour"
    assert l._proxy.data(l._proxy.index(2, 1), Qt.DisplayRole) == "deux"

    l.doSort(1)  # nouvelle colonne ascending
    # procy à jour
    assert l._proxy.data(l._proxy.index(0, 1), Qt.DisplayRole) == "deux"
    assert l._proxy.data(l._proxy.index(1, 1), Qt.DisplayRole) == "bonjour"
    assert l._proxy.data(l._proxy.index(2, 1), Qt.DisplayRole) == "au revoir"

    l.doSort(1)  # meme colonne toggle
    # proxy à jour
    assert l._proxy.data(l._proxy.index(0, 1), Qt.DisplayRole) == "au revoir"
    assert l._proxy.data(l._proxy.index(1, 1), Qt.DisplayRole) == "bonjour"
    assert l._proxy.data(l._proxy.index(2, 1), Qt.DisplayRole) == "deux"


def test_filter(lexons):
    l = Lexique()
    l.filter(1, "on")
    assert l._proxy.rowCount(QModelIndex()) == 1
    l.filter(1, "o")
    assert l._proxy.rowCount(QModelIndex()) == 2
    l.filter(1, "")
    assert l._proxy.rowCount(QModelIndex()) == 3
    assert l._proxy.sortOrder() == Qt.AscendingOrder


def test_updateActivesLocales(qtbot):
    l = Lexique()
    assert l._model.activesLocales == ["en_GB", "fr_FR"]
    with qtbot.waitSignal(l._model.activesLocalesChanged):
        l.updateActivesLocales("it_IT", True)
    assert l.model.activesLocales == ["en_GB", "fr_FR", "it_IT"]
