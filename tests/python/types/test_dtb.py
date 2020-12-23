from datetime import datetime

import pytest
from PySide2.QtQml import QJSEngine
from tests.python.fixtures import check_args, disable_log
from mycartable.types.dtb import DTB
from loguru_caplog import loguru_caplog as caplog
from pony.orm import db_session


@pytest.fixture()
def dtb(reset_db):
    return DTB()


def test_addDB(dtb):
    res = dtb.addDB("Annee", {"id": 1234, "niveau": "bbb"})
    assert res == {
        "id": 1234,
        "niveau": "bbb",
    }


def test_addDB_bad_entity(dtb):
    assert dtb.addDB("AAA", {}) == {}


def test_DTB_no_db(dtb):
    class AAA(DTB):
        pass

    AAA.db = None

    with pytest.raises(NotImplementedError):
        AAA()


def test_addDB_bas_params(dtb, caplog):
    assert dtb.addDB("Annee", {"ezfzef": "aaa"}) == {}
    assert "Unknown attribute 'ezfzef'" == caplog.records[0].message


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
    f = fk.f_groupeMatiere(td=True)
    res = dtb.setDB("GroupeMatiere", str(f["id"]), {"nom": "bbb"})
    f["nom"] = "bbb"
    assert res == f


def test_setDB_id_is_int(fk, dtb):
    f = fk.f_annee(td=True)
    res = dtb.setDB("Annee", f["id"], {"niveau": "bbb"})
    f["niveau"] = "bbb"
    assert res == f


def test_setDB_name_id_filed_is_not_id(fk, dtb):
    f = fk.f_style(td=True, underline=True)
    res = dtb.setDB("Style", f["styleId"], {"underline": False})
    f["underline"] = False
    assert res == f


def test_setDB_bad_entity(dtb):
    assert dtb.setDB("AZEAZE", "", {}) == {}


def test_setDB_bad_id(dtb):
    assert dtb.setDB("Annee", 123, {}) == {}


def test_setDB_bad_param(dtb, fk, caplog):
    f = fk.f_annee(id=2020)
    assert dtb.setDB("Annee", 2020, {"azda": "dzef"}) == {}
    assert "Unknown attribute 'azda'" == caplog.records[0].message


# test configuration


def test_config_get_set(dtb, fk):
    with db_session:
        fk.db.Configuration.add("bla", "ha")

    assert dtb.getConfig("bla") == "ha"
    assert dtb.getConfig("nothing") is None
    dtb.setConfig("bla", "rouge")
    assert dtb.getConfig("bla") == "rouge"


def test_setConfig_jsvalue(dtb, fk, qapp):
    q = QJSEngine()
    val = {"nom": "aa", "prenom": "bb"}
    arr = q.toScriptValue(val)
    dtb.setConfig("bla", arr)
    assert dtb.getConfig("bla") == val


def test_exec(dtb, fk):
    a = fk.f_annee(id=2019)
    # no arg
    res = dtb.execDB("Annee", a.id, "get_pk")
    assert res == a.id

    # pos args
    # pas d'exemple à tester ...

    # kwargs
    res = dtb.execDB("Annee", 2019, "to_dict", only=["niveau"])
    assert res == {"niveau": "cm2019"}


def test_exec_class_method(dtb, fk):
    x = fk.f_page(activite=2019, titre="pageun", created=datetime(1111, 10, 1), td=True)
    y = fk.f_page(activite=2019, titre="pageun", created=datetime(1111, 12, 1), td=True)
    z = fk.f_page(activite=2019, titre="pageun", created=datetime(1111, 11, 1), td=True)

    a = fk.f_annee(id=2019)
    res = dtb.execDB("Page", None, "recents", 2019)
    assert res == [y, z, x]
