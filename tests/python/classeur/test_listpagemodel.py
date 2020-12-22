from PySide2.QtCore import QObject
from mycartable.classeur import (
    ListOfPageModel,
    Page,
    RecentsModel,
    Classeur,
    ActiviteModel,
)
from pony.orm import db_session


class TestListOfPageModel:
    def test_base(self):
        a = QObject()
        l = ListOfPageModel(parent=a)
        l._data = [{"titre": "aaa", "id": "111", "matiereBgColor": "#111111"}]

        assert l.parent() == a
        assert l.rowCount() == 1

    def test_data(self):
        l = ListOfPageModel()
        l._data = [{"titre": "aaa", "id": "111", "matiereBgColor": "#111111"}]
        assert l.data(l.index(0, 0), l.TitreRole) == "aaa"
        assert l.data(l.index(0, 0), l.PageIdRole) == "111"
        assert l.data(l.index(0, 0), l.BgColorRole) == "#111111"

    def test_update_titre(self, fk):
        l = ListOfPageModel()
        p = fk.f_page()
        l._data = [{"titre": "aaa", "id": str(p.id), "matiereBgColor": "#111111"}]
        p_obj = Page.get(p.id)
        p_obj.titre = "bbb"
        assert l.update_titre(p_obj)
        assert l._data == [
            {"titre": "bbb", "id": str(p.id), "matiereBgColor": "#111111"}
        ]

    def test_remove_by_id(self, fk):
        l = ListOfPageModel()
        p = fk.f_page()
        l._data = [{"titre": "aaa", "id": str(p.id), "matiereBgColor": "#111111"}]
        l._reset = lambda: setattr(l, "_data", [])
        assert l.remove_by_Id(str(p.id))
        assert l._data == []


class TestRecentsModel:
    def test_base(self, fk):
        with db_session:
            p = fk.f_page(titre="hello")
            lannee = p.activite.matiere.groupe.annee
            p = p.to_dict()

        class AA(QObject):
            annee = lannee.id

        a = AA()
        r = RecentsModel(lannee.id, parent=a)
        assert r.classeur == a
        assert r.data(r.index(0, 0), r.TitreRole) == "hello"


class TestACtiviteModel:
    def test_base(self, fk):
        p = fk.f_page(titre="hello", td=True)
        r = ActiviteModel(p["activite"])
        assert r.data(r.index(0, 0), r.TitreRole) == "hello"
