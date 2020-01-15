from PySide2.QtCore import QObject
from package.database.factory import f_activite, f_matiere, f_page
from pony.orm import db_session
from fixtures import compare, ss


# class TestMatiere:

    # def testSignalArguments(self, root):
    #     a = f_matiere(nom="bla")
    #     f_matiere(nom="lot")
    #     ac = f_activite(matiere=a.id, famille=0)
    #     with db_session:
    #         pages = [f_page(activite=ac.id).to_dict() for i in range(4)]
    #     root.ddb.matieresListRefresh()
    #     select = root.W._comboBoxSelectMatiere
    #     assert select.model == ['bla', 'lot']
    #     recent_header =  root.W.recentsHeader
    #     assert recent_header.text == -1
    #
    #     select.obj.activated.emit(1)
    #     assert select.currentText == "lot"
    #     assert recent_header.text == 2
    #     select.obj.activated.emit(0)
    #     assert select.currentText == "bla"
    #     assert recent_header.text == 1
    #
    #     root.ddb.currentMatiere = 2
    #     assert select.currentText == "lot"
    #     assert recent_header.text == 2
    #
    #     root.ddb.currentMatiere = 1
    #     lvlessons = root.W._listViewLessons
    #     assert compare(lvlessons.model, pages)

def test_recents(root, ddbn):
    import time
    time.sleep(1)
    recents_lv = root.W.recentsListView
    print(root.W._buttonDelegateRecents.obj)
    print(root.findChildren(QObject, "_buttonDelegateRecents"))
    # recents_db = ss(ddbn.Page.recents)
    # assert recents_lv.count == len(recents_db)
    print("fin test")

