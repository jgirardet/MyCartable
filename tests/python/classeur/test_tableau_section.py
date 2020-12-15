import pytest
from fixtures import check_args
from mycartable.classeur import TableauSection
from pony.orm import db_session


def test_properties(fk):
    a = fk.f_tableauSection(lignes=2, colonnes=3)
    b = TableauSection.get(a.id)
    assert b.colonnes == 3
    assert b.lignes == 2
    assert b.entity_name == "TableauSection"


def test_check_args():
    check_args(TableauSection.initTableauDatas, None, list)
    check_args(TableauSection.updateCell, [int, int, dict])
    check_args(TableauSection.insertRow, [int])
    check_args(TableauSection.appendRow)
    check_args(TableauSection.removeRow, [int])
    check_args(TableauSection.insertColumn, [int])
    check_args(TableauSection.appendColumn)
    check_args(TableauSection.removeColumn, [int])


def test_init_datas(fk):
    x = fk.f_tableauSection(3, 4)
    t = TableauSection.get(x.id)
    with db_session:
        assert t.initTableauDatas() == fk.db.TableauSection[x.id].get_cells()


def test_update_cell(qtbot, fk):
    x = fk.f_tableauCell(x=2, y=3, texte="zer")
    t = TableauSection.get(x.tableau.id)
    with qtbot.waitSignal(t.tableauChanged):
        t.updateCell(3, 2, {"texte": "bla"})
    with db_session:
        assert fk.db.TableauCell[x.tableau.id, 3, 2].texte == "bla"


@pytest.mark.parametrize(
    "fn, lignes, colonnes, args",
    [
        ("insertRow", 3, 2, [1]),
        ("removeRow", 1, 2, [1]),
        ("appendRow", 3, 2, []),
    ],
)
def test_add_remove_row(fk, qtbot, fn, lignes, colonnes, args):
    x = fk.f_tableauSection(2, 2)
    t = TableauSection.get(x.id)
    with qtbot.waitSignal(t.lignesChanged):
        getattr(t, fn)(*args)
    with db_session:
        x = fk.db.TableauSection[x.id]
        assert t.lignes == x.lignes == lignes
        assert t.colonnes == x.colonnes == colonnes


@pytest.mark.parametrize(
    "fn, lignes, colonnes, args",
    [
        ("insertColumn", 2, 3, [1]),
        ("appendColumn", 2, 3, []),
        ("removeColumn", 2, 1, [1]),
    ],
)
def test_add_remove_column(fk, qtbot, fn, lignes, colonnes, args):
    x = fk.f_tableauSection(2, 2)
    t = TableauSection.get(x.id)
    with qtbot.waitSignal(t.colonnesChanged):
        getattr(t, fn)(*args)
    with db_session:
        x = fk.db.TableauSection[x.id]
        assert t.lignes == x.lignes == lignes
        assert t.colonnes == x.colonnes == colonnes
