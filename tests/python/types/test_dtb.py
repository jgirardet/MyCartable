import pytest
from fixtures import check_args
from mycartable.types.dtb import DTB
from loguru_caplog import loguru_caplog as caplog
from pony.orm import db_session


@pytest.fixture()
def dtb(reset_db):
    return DTB()


def test_addDB(dtb):
    res = dtb.addDB("Utilisateur", {"nom": "aaa", "prenom": "bbb"})
    assert res == {
        "id": str(res["id"]),
        "last_used": 0,
        "nom": "aaa",
        "prenom": "bbb",
    }


def test_addDB_bad_entity(dtb):
    assert dtb.addDB("AAA", {}) == {}


def test_addDB_bas_params(dtb, caplog):
    assert dtb.addDB("Utilisateur", {"ezfzef": "aaa"}) == {}
    assert "Unknown attribute 'ezfzef'" == caplog.records[0].exc_info[1].args[0]


def test_setDB_id_is_int(fk, dtb):
    f = fk.f_annee(id=2020, niveau="aaa", td=True)
    res = dtb.setDB("Annee", 2020, {"niveau": "bbb"})
    f["niveau"] = "bbb"
    assert res == f


def test_delDB(dtb, fk):
    f = fk.f_annee(id=2020)
    assert dtb.delDB("Annee", str(f.id))
    with db_session:
        assert not fk.db.Annee.get(id=f.id)


def test_delDB_bad_enitity(dtb, fk, caplog):
    assert not dtb.delDB("Azert", "kkk")
    assert (
        "Absence de table Azert dans la base de donnée"
        == caplog.records[0].getMessage()
    )


def test_delDB_bad_id(dtb, fk, caplog):
    assert not dtb.delDB("Annee", 2020)
    f = fk.f_annee(id=2020)
    assert "Absence d'item 2020 dans la table Annee" == caplog.records[0].getMessage()


### Test Get db


def test_check_args():
    check_args(DTB.getDB, [str, int], dict)
    check_args(DTB.getDB, [str, str], dict, slot_order=1)
    # check_args(DTB.getDB, [str, str, str], dict, slot_order=2)
    # check_args(DTB.getDB, [str, int, str], dict, slot_order=3)


def test_getDB(dtb, fk):
    f = fk.f_annee(id=2020, td=True)
    assert dtb.getDB("Annee", f["id"]) == f


# def test_getDB_function(dtb, fk):
#     f = fk.f_annee(id=2020, td=True)
#     assert dtb.getDB("Annee", f["id"], "to_dict") == f
#


def test_getDB_bad_enitity(dtb, fk, caplog):
    assert not dtb.getDB("Azert", "kkk")
    assert (
        "Absence de table Azert dans la base de donnée"
        == caplog.records[0].getMessage()
    )


def test_getDB_bad_id(dtb, fk, caplog):
    assert not dtb.getDB("Annee", 2020)
    f = fk.f_annee(id=2020)
    assert "Absence d'item 2020 dans la table Annee" == caplog.records[0].getMessage()


### tests setDB


def test_setDB_id_is_str(fk, dtb):
    f = fk.f_user(nom="aaa", td=True)
    res = dtb.setDB("Utilisateur", str(f["id"]), {"nom": "bbb"})
    f["nom"] = "bbb"
    assert res == f


def test_setDB_bad_entity(dtb):
    assert dtb.setDB("AZEAZE", "", {}) == {}


def test_setDB_bad_id(dtb):
    assert dtb.setDB("Annee", 123, {}) == {}


def test_setDB_bad_param(dtb, fk, caplog):
    f = fk.f_annee(id=2020)
    assert dtb.setDB("Annee", 2020, {"azda": "dzef"}) == {}
    assert "Unknown attribute 'azda'" == caplog.records[0].exc_info[1].args[0]
