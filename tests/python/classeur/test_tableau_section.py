import pytest
from fixtures import compare_dict_list
from mycartable.classeur import TableauSection, Page
from pony.orm import db_session


def test_properties(fk, bridge):
    a = fk.f_tableauSection(lignes=2, colonnes=3)
    b = TableauSection.get(a.id, parent=bridge)
    assert b.colonnes == 3
    assert b.lignes == 2
    assert b.entity_name == "TableauSection"


def test_init_datas(fk, bridge):
    x = fk.f_tableauSection(3, 4)
    t = TableauSection.get(x.id, parent=bridge)
    with db_session:
        assert t.initTableauDatas() == fk.db.TableauSection[x.id].get_cells()


def test_update_cell(qtbot, fk, bridge):
    tab = fk.f_tableauSection(4, 4)
    page = Page.get(tab.page.id, parent=bridge)
    t: TableauSection = page.get_section(0)

    # set by app no emit first
    with qtbot.assertNotEmitted(t.cellUpdated):
        t.updateCell(3, 2, {"texte": "bla"}, 5, 12)
    with db_session:
        assert fk.db.TableauCell[tab.id, 3, 2].texte == "bla"

    with qtbot.waitSignal(t.cellUpdated) as blocker:
        t.undoStack.undo()
    assert blocker.args == [{"_cursor": 5, "_index": 14, "texte": ""}]

    with qtbot.waitSignal(t.cellUpdated) as blocker:
        t.undoStack.redo()
    assert blocker.args == [{"_cursor": 12, "_index": 14, "texte": "bla"}]

    with qtbot.waitSignal(t.cellUpdated) as blocker:
        t.undoStack.undo()
    assert blocker.args == [{"_cursor": 5, "_index": 14, "texte": ""}]  # test not crash


@pytest.mark.parametrize(
    "fn, lignes, colonnes, args",
    [
        ("insertRow", 3, 2, [1]),
        ("removeRow", 1, 2, [1]),
        ("appendRow", 3, 2, []),
    ],
)
def test_add_remove_row(fk, bridge, qtbot, fn, lignes, colonnes, args):
    x = fk.f_tableauSection(2, 2)
    p = Page.get(x.page.id, parent=bridge)
    t = p.get_section(0)
    with qtbot.waitSignal(t.lignesChanged):
        getattr(t, fn)(*args)
    with db_session:
        x = fk.db.TableauSection[x.id]
        assert t.lignes == x.lignes == lignes
        assert t.colonnes == x.colonnes == colonnes
        base_res = x.get_cells()

    with qtbot.waitSignal(t.lignesChanged):
        t.undoStack.undo()
    with db_session:
        x = fk.db.TableauSection[x.id]
        assert t.lignes == x.lignes == 2
        assert t.colonnes == x.colonnes == 2
        assert x.cells.count() == 4
        assert len(x.get_cells()) == 4

    with qtbot.waitSignal(t.lignesChanged):
        t.undoStack.redo()
        with db_session:
            x = fk.db.TableauSection[x.id]
            assert t.lignes == x.lignes == lignes
            assert t.colonnes == x.colonnes == colonnes
            res_apres_redo = x.get_cells()

    exclude = [("style", "styleId")] if fn != "removeRow" else []
    compare_dict_list(base_res, res_apres_redo, exclude=exclude)


@pytest.mark.parametrize(
    "fn, lignes, colonnes, args",
    [
        ("insertColumn", 2, 3, [1]),
        ("appendColumn", 2, 3, []),
        ("removeColumn", 2, 1, [1]),
        ("removeColumn", 2, 1, [0]),
    ],
)
def test_add_remove_column(fk, bridge, qtbot, fn, lignes, colonnes, args):
    x = fk.f_tableauSection(2, 2)
    p = Page.get(x.page.id, parent=bridge)
    t = p.get_section(0)
    with qtbot.waitSignal(t.colonnesChanged):
        getattr(t, fn)(*args)
    with db_session:
        x = fk.db.TableauSection[x.id]
        assert t.lignes == x.lignes == lignes
        assert t.colonnes == x.colonnes == colonnes
        base_res = x.get_cells()

    with qtbot.waitSignal(t.colonnesChanged):
        t.undoStack.undo()
    with db_session:
        x = fk.db.TableauSection[x.id]
        assert t.lignes == x.lignes == 2
        assert t.colonnes == x.colonnes == 2
        assert x.cells.count() == 4
        assert len(x.get_cells()) == 4

    with qtbot.waitSignal(t.colonnesChanged):
        t.undoStack.redo()
        with db_session:
            x = fk.db.TableauSection[x.id]
            assert t.lignes == x.lignes == lignes
            assert t.colonnes == x.colonnes == colonnes
            res_apres_redo = x.get_cells()

    exclude = [("style", "styleId")] if "remove" not in fn else []
    compare_dict_list(base_res, res_apres_redo, exclude=exclude)
