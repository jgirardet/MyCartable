import pytest

from PySide2.QtCore import Qt, QModelIndex
from fixtures import check_super_init, check_begin_end
from package.database.factory import (
    f_page,
    b_section,
    f_section,
    f_annotationText,
    f_annotationDessin,
    f_imageSection,
)
from package.page.annotation_model import AnnotationModel
from pony.orm import db_session, make_proxy
from pony.orm.core import EntityProxy


@pytest.fixture
def am(ddbr):
    def factory(nb, genre=None):
        p = f_imageSection()
        a = AnnotationModel()
        if isinstance(genre, tuple):
            for i in genre:
                if i == "t":
                    f_annotationText(section=p.id)
                elif i == "d":
                    f_annotationDessin(section=p.id)
        else:
            for i in range(nb):
                f_annotationText(section=p.id)
        a.sectionId = p.id
        return a

    return factory


class TestAnnotationModel:
    def test_base_init(self, qtbot, qtmodeltester):
        assert check_super_init(
            "package.page.page_model.QAbstractListModel", AnnotationModel
        )
        b = AnnotationModel()
        assert b.row_count == 0

        a = AnnotationModel()
        # a._datas = [1, 2, 4]
        qtmodeltester.check(a)

    #
    def test_data_role(self, am):
        a = am(2)
        # valid index
        assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == 2
        # invalid index
        assert a.data(a.index(99, 99), a.AnnotationRole) is None
        # no good role
        assert a.data(a.index(1, 0), 99999) is None

    def test_flags(self, am):
        x = am(1)
        assert int(x.flags(x.index(0, 0))) == 128 + 35
        assert x.flags(x.index(99, 99)) is None

    def test_insertRows_and_row(self, am, qtbot):
        x = am(2)
        assert x.rowCount() == 2

        f_annotationText(section=x.sectionId)
        assert x.insertRows(1, 0)
        assert x.rowCount() == 3

        f_annotationText(section=x.sectionId)
        assert x.insertRow(1)
        assert x.rowCount() == 4

    def test_roles(self):
        am = AnnotationModel()
        assert Qt.DisplayRole in am.roleNames()
        assert AnnotationModel.AnnotationRole in am.roleNames()
        assert am.roleNames()[AnnotationModel.AnnotationRole] == b"annot"

    def test_row_count(self, am):
        a = am(2)
        assert a.rowCount() == a.row_count == a.count == 2

    def test_count(self, am, qtbot):
        a = am(1)
        with qtbot.waitSignal(a.countChanged):
            a.count = 3
        assert a.rowCount() == a.row_count == a.count == 3

    def test_sloot_reset(self, ddbr, qtbot):
        a = AnnotationModel()

        # section does not exists
        with qtbot.waitSignal(a.modelReset):
            assert a.slotReset(99) is None
            assert a.section is None
            assert a.sectionId == 0

        f = f_imageSection()
        f_annotationDessin(section=f.id)
        with qtbot.waitSignal(a.modelReset):
            assert a.slotReset(f.id)

        with db_session:
            assert a.section.id == f.id
            assert isinstance(a.section, EntityProxy)
            assert a.sectionId == f.id
            assert a.count == 1

        # a.slotReset(f.id)
        #
        # with db_session:
        #     pid = a.page.id
        #     modidied = ddbr.Page[pid].modified
        #
        # a.slotReset(pid)
        # # update automagicaly called
        # with db_session:
        #     item = ddbr.Page[pid]
        #     assert a.lastPosition == item.lastPosition
        #     assert item.modified == modidied  # reset do not change modified

    #
    # def test_slot_reset_pageId_is_zero(self, am):
    #     a = am(0)
    #     a.slotReset(1)
    #     assert a.page is not None
    #     a.slotReset(0)
    #     assert a.page is None
    #
    # def test_ResetModel_begin_end(self, am):
    #     a = am(0)
    #     with check_begin_end(a, "ResetModel"):
    #         a.slotReset(0)
    #
    # def test_property_last_position(self, am):
    #     a = am(3)
    #     assert a.lastPosition == None
    #     a.lastPosition = 2
    #     with db_session:
    #         assert a.page.lastPosition == 2
    #
    # def test_property_last_position_set_ddb(self, am, ddbr, qtbot):
    #     a = am(0)
    #     # section do not exists
    #     with qtbot.waitSignal(a.lastPositionChanged):
    #         a.lastPosition = 999
    #
    #     # cas ou ça va
    #     p = f_page(lastPosition=2)
    #     b_section(3, page=p.id)
    #     a.page_id = p.id
    #     with db_session:
    #         a._page = make_proxy(ddbr.Page[p.id])
    #     with qtbot.waitSignal(a.lastPositionChanged):
    #         a.lastPosition = 1
    #     with db_session:
    #         assert ddbr.Page[1].lastPosition == 1
    #
    # @pytest.mark.parametrize(
    #     "source, target, res_fn, res_source, res_target",
    #     [
    #         (0, 2, True, 2, 1),
    #         (0, 1, True, 1, 0),
    #         (2, 0, True, 0, 1),
    #         (2, 1, True, 1, 2),
    #         (-1, 3, False, 1, 2),
    #         (-1, 1, False, 1, 2),
    #         (1, 1, False, 1, 1),
    #     ],
    # )
    # def test_move(self, source, target, res_fn, res_source, res_target, am, ddbr):
    #     a = am(3)
    #     assert a.move(source, target) == res_fn
    #     if res_fn:
    #         with db_session:
    #             assert ddbr.Section[source + 1].position == res_source
    #             assert ddbr.Section[target + 1].position == res_target
    #
    # def test_move_last_position(self, am, qtbot, ddbr):
    #     a = am(3)
    #     with qtbot.waitSignal(a.lastPositionChanged):
    #         assert a.move(0, 2)
    #
    #     with db_session:
    #         assert a.page.lastPosition == 2
    #
    # def test_removeRows_at_0(self, am, ddbr, qtbot):
    #     a = am(3)
    #
    #     assert a.removeRows(0, 0, QModelIndex())
    #     assert a.rowCount() == 2
    #     assert a.data(a.index(0, 0), a.AnnotationRole)["id"] == 2
    #     assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == 3
    #
    # def test_removeRows_at_1(self, am, ddbr, qtbot):
    #     a = am(3)
    #
    #     assert a.removeRows(1, 0, QModelIndex())
    #     assert a.rowCount() == 2
    #     assert a.data(a.index(0, 0), a.AnnotationRole)["id"] == 1
    #     assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == 3
    #
    # def test_removeRows_at_end(self, am, ddbr, qtbot):
    #     a = am(3)
    #
    #     assert a.removeRows(2, 0, QModelIndex())
    #     assert a.rowCount() == 2
    #     assert a.data(a.index(0, 0), a.AnnotationRole)["id"] == 1
    #     assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == 2
    #
    # def test_removeSection(self, am, ddbr, qtbot):
    #     a = am(3)
    #
    #     assert a.removeSection(0)
    #     assert a.rowCount() == 2
    #     assert a.data(a.index(0, 0), a.AnnotationRole)["id"] == 2
    #     assert a.data(a.index(1, 0), a.AnnotationRole)["id"] == 3
    #
    # def test_count(self, am, ddbr, qtbot):
    #     a = am(0)
    #     assert a.count == 0
    #     b = am(3)
    #     assert b.count == 3
    #     x = f_page()
    #     b_section(2, page=x.id)
    #     with qtbot.waitSignal(b.countChanged):
    #         b.slotReset(x.id)
    #     assert b.count == 2
    #
    # def test_modif_update_recents_and_activites(self, qtbot, am, qapp):
    #     a = am(3)
    #
    #     with qtbot.waitSignal(qapp.dao.updateRecentsAndActivites):
    #         a.move(0, 2)
    #
    #     with qtbot.waitSignal(qapp.dao.updateRecentsAndActivites):
    #         a.removeSection(0)
    #
    #     with qtbot.waitSignal(qapp.dao.updateRecentsAndActivites):
    #         a.insertRow(0)
