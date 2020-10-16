import pytest

from PySide2.QtCore import Qt, QModelIndex
from fixtures import check_super_init, check_begin_end, check_args
from package.page.page_model import PageModel
from pony.orm import db_session, make_proxy


@pytest.fixture
def pm(fk, qappdao):
    # return a
    def factory(nb):
        p = fk.f_page()
        a = PageModel(fk.db)
        x = fk.b_section(nb, page=p.id)
        a.secids = [str(z.id) for z in x]
        a.pageid = p.id
        print(a.secids, a.pageid)
        a.slotReset(p.id)
        return a

    return factory


class TestPAgeModel:
    def test_check_args(self, pm):
        a = pm(1)
        check_args(a.move, [int, int], bool)
        check_args(a.removeSection, [int], bool)

    def test_base_init(self, ddbr, qtbot, qtmodeltester):
        b = PageModel(ddbr)
        assert b.row_count == 0

        a = PageModel(ddbr)
        # a._datas = [1, 2, 4]
        qtmodeltester.check(a)

    #
    def test_data_role(self, pm):
        a = pm(2)
        # valid index
        assert a.data(a.index(1, 0), a.PageRole)["id"] == a.secids[1]
        # invalid index
        assert a.data(a.index(99, 99), a.PageRole) is None
        # no good role
        assert a.data(a.index(1, 0), 99999) is None

    def test_flags(self, pm):
        x = pm(1)
        assert int(x.flags(x.index(0, 0))) == 128 + 35
        assert x.flags(x.index(99, 99)) is None

    def test_insertRows(self, fk, pm, qtbot):
        x = pm(2)

        def util(x, y, z):
            assert x == QModelIndex()
            assert y == 2
            assert z == 4
            return True

        assert x.count == 2

        with db_session:
            d = fk.b_section(3, page=x.page.id)
        with qtbot.waitSignal(
            x.rowsInserted,
            check_params_cb=util,
        ):
            assert x.insertRows(d[0].position, len(d))
        assert x.count == 5
        assert x.lastPosition == 2

    def test_insertRow(self, pm, fk):
        """cela test aussi insertion en dernière place
        et les defautls arguments.
        """
        x = pm(1)

        assert x.row_count == 1

        with db_session:
            d = fk.f_section(page=x.page.id)
        assert x.insertRow(1)
        assert x.row_count == 2
        assert x.lastPosition == 1

    def test_insertRows_begin_end(self, pm):
        a = pm(1)
        with check_begin_end(a, "InsertRows"):
            a.insertRows(0, 1, QModelIndex())

    def test_roles(self, ddbr):
        pm = PageModel(ddbr)
        assert Qt.DisplayRole in pm.roleNames()
        assert PageModel.PageRole in pm.roleNames()
        assert pm.roleNames()[PageModel.PageRole] == b"page"

    def test_row_count(self, pm):
        a = pm(5)
        assert a.rowCount() == 5

    def test_sloot_reset(self, pm, ddbr):
        a = pm(1)
        with db_session:
            pid = a.page.id
            modidied = ddbr.Page[pid].modified

        a.slotReset(pid)
        # update automagicaly called
        with db_session:
            item = ddbr.Page[pid]
            assert a.lastPosition == item.lastPosition
            assert item.modified == modidied  # reset do not change modified

    def test_slot_reset_pageId_is_zero(self, pm):
        a = pm(0)
        a.slotReset(1)
        assert a.page is not None
        a.slotReset(0)
        assert a.page is None

    def test_ResetModel_begin_end(self, pm):
        a = pm(0)
        with check_begin_end(a, "ResetModel"):
            a.slotReset(0)

    def test_property_last_position(self, pm):
        a = pm(3)
        assert a.lastPosition == None
        a.lastPosition = 2
        with db_session:
            assert a.page.lastPosition == 2

    def test_property_last_position_set_ddb(self, pm, fk, qtbot):
        a = pm(0)
        # section do not exists
        with qtbot.waitSignal(a.lastPositionChanged):
            a.lastPosition = 999

        # cas ou ça va
        p = fk.f_page(lastPosition=2)
        fk.b_section(3, page=p.id)
        a.page_id = p.id
        with db_session:
            a._page = make_proxy(fk.db.Page[p.id])
        with qtbot.waitSignal(a.lastPositionChanged):
            a.lastPosition = 1
        with db_session:
            assert fk.db.Page[str(a.pageid)].lastPosition == 1

    @pytest.mark.parametrize(
        "source, target, res_fn, res_source, res_target",
        [
            (0, 2, True, 2, 1),
            (0, 1, True, 1, 0),
            (2, 0, True, 0, 1),
            (2, 1, True, 1, 2),
            (-1, 3, False, 1, 2),
            (-1, 1, False, 1, 2),
            (1, 1, False, 1, 1),
        ],
    )
    def test_move(self, source, target, res_fn, res_source, res_target, pm, ddbr):
        a = pm(3)
        assert a.move(source, target) == res_fn
        if res_fn:
            with db_session:
                assert ddbr.Section[a.secids[source]].position == res_source
                assert ddbr.Section[a.secids[target]].position == res_target

    def test_move_last_position(self, pm, qtbot, ddbr):
        a = pm(3)
        with qtbot.waitSignal(a.lastPositionChanged):
            assert a.move(0, 2)

        with db_session:
            assert a.page.lastPosition == 2

    def test_removeRows_at_0(self, pm, ddbr, qtbot):
        a = pm(3)

        assert a.removeRows(0, 0, QModelIndex())
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.PageRole)["id"] == a.secids[1]
        assert a.data(a.index(1, 0), a.PageRole)["id"] == a.secids[2]

    def test_removeRows_at_1(self, pm, ddbr, qtbot):
        a = pm(3)

        assert a.removeRows(1, 0, QModelIndex())
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.PageRole)["id"] == a.secids[0]
        assert a.data(a.index(1, 0), a.PageRole)["id"] == a.secids[2]

    def test_removeRows_at_end(self, pm, ddbr, qtbot):
        a = pm(3)

        assert a.removeRows(2, 0, QModelIndex())
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.PageRole)["id"] == a.secids[0]
        assert a.data(a.index(1, 0), a.PageRole)["id"] == a.secids[1]

    def test_removeSection(self, pm, ddbr, qtbot):
        a = pm(3)

        assert a.removeSection(0)
        assert a.rowCount() == 2
        assert a.data(a.index(0, 0), a.PageRole)["id"] == a.secids[1]
        assert a.data(a.index(1, 0), a.PageRole)["id"] == a.secids[2]

    def test_count(self, pm, fk, qtbot):
        a = pm(0)
        assert a.count == 0
        b = pm(3)
        assert b.count == 3
        x = fk.f_page()
        fk.b_section(2, page=x.id)
        with qtbot.waitSignal(b.countChanged):
            b.slotReset(x.id)
        assert b.count == 2

    def test_modif_update_recents_and_activites(self, qtbot, pm, qapp):
        a = pm(3)

        with qtbot.waitSignal(qapp.dao.updateRecentsAndActivites):
            a.move(0, 2)

        with qtbot.waitSignal(qapp.dao.updateRecentsAndActivites):
            a.removeSection(0)

        with qtbot.waitSignal(qapp.dao.updateRecentsAndActivites):
            a.insertRow(0)
