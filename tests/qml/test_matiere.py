from PySide2.QtCore import QObject
from package.database.factory import f_activite, f_matiere, f_page
from pony.orm import db_session, flush, select
from fixtures import compare, ss
from package.database import db


class TestComboSelector:
    def test_matiere_list_nom(self, rootObject, matieres_list, ddbn):
        """also test databaseobject.matierelitnom"""
        select_cb = rootObject.W._comboBoxSelectMatiere
        assert sorted(select_cb.model) == sorted(matieres_list)

    def test_changement_matiere(self, rootObject, matieres_list, ddbn):
        mat_id = 1
        select_cb = rootObject.W._comboBoxSelectMatiere

        # test ddb setcurrentmatierefromfindex
        select_cb.obj.activated.emit(1)
        assert select_cb.currentText == matieres_list[1]
        assert (
            rootObject.ddb.currentMatiere
            == matieres_list.index(select_cb.currentText) + 1
        )

        # test select reac to currentMatiere
        rootObject.ddb.currentMatiere = 3
        assert select_cb.currentText == matieres_list[2]

        # test changement dans lessons
        rootObject.ddb.currentMatiere = mat_id
        lvlessons = rootObject.W._listViewLessons
        with db_session:
            pages = ddbn.Activite.pages_by_matiere_and_famille(mat_id, 0)
            assert compare(lvlessons.model, pages)

        # test changement dans lessons
        rootObject.ddb.currentMatiere = mat_id
        lvexercices = rootObject.W._listViewExercices
        with db_session:
            pages = ddbn.Activite.pages_by_matiere_and_famille(mat_id, 1)
            assert compare(lvexercices.model, pages)


class TestDataBaseObject:
    def test_database_object_current_matierere_set(self, rootObject, matieres_list):
        # set via int
        rootObject.ddb.currentMatiere = 1
        assert rootObject.ddb.currentMatiere == 1
        # no change do nothing
        rootObject.ddb.currentMatiere = 1
        assert rootObject.ddb.currentMatiere == 1

        # not int not set
        rootObject.ddb.currentMatiere = matieres_list[3]
        assert rootObject.ddb.currentMatiere == 1
