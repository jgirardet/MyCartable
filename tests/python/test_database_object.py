from datetime import datetime


from package.database_object import DatabaseObject


from mycartable.files_path import FILES
from pony.orm import db_session


class TestDatabaseObject:
    def test_image_update_update_recents_and_activite(self, dao, qtbot):
        with qtbot.waitSignal(dao.updateRecentsAndActivites):
            dao.imageChanged.emit()

    def test_equation_update_update_recents_and_activite(self, dao, qtbot):
        with qtbot.waitSignal(dao.updateRecentsAndActivites):
            dao.equationChanged.emit()

    def test_page_activite_changed_update_pagesParsection(self, dao, qtbot):
        with qtbot.waitSignal(dao.pagesParActiviteChanged):
            dao.pageActiviteChanged.emit()

    def test_section_added_disable_busyindicator(self, fk, dao, qtbot):
        f = fk.f_page()
        dao.pageModel.slotReset(f.id)
        dao.ui.buzyIndicator = True
        dao.sectionAdded.emit(0, 0)
        assert not dao.ui.buzyIndicator
