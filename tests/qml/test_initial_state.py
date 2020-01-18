from PySide2.QtCore import QObject
from package.database.factory import f_activite, f_matiere, f_page
from pony.orm import db_session, flush, select
from fixtures import compare, ss
from package.database import db

class TestMatiere:
    def test_au_demarrage(self, rootObject, matieres_list, ddbn):

        select_cb = rootObject.W._comboBoxSelectMatiere
        assert sorted(select_cb.model) == sorted(matieres_list)

    def test_changement_matiere(self, rootObject, matieres_list, ddbn):
        mat_id = 1
        select_cb = rootObject.W._comboBoxSelectMatiere
        select_cb.obj.activated.emit(1)
        print("current", select_cb.currentText)
        assert select_cb.currentText == matieres_list[1]
        select_cb.obj.activated.emit(0)
        assert select_cb.currentText == matieres_list[0]
        rootObject.ddb.currentMatiere = 3
        assert select_cb.currentText == matieres_list[2]
        rootObject.ddb.currentMatiere = mat_id
        lvlessons = rootObject.W._listViewLessons
        with db_session:
            ac = ddbn.Matiere.get(id=1).activites.select()[:][0]
            pages = select(p for p in ddbn.Page if p.activite ==ac)[:]
            assert compare(lvlessons.model, [p.to_dict() for p in pages])



