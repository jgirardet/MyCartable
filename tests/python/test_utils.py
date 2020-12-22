import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtCore import QUrl
from mycartable.package.utils import pathize

from package.utils import (
    create_singleshot,
    get_new_filename,
    KeyW,
    KeyCross,
    WIN,
    KEYS,
    read_qrc,
    WDict,
    shift_list,
    Version,
)
from packaging.version import InvalidVersion


def test_create_single_shot():
    def bla():
        pass

    a = create_singleshot(bla)
    assert a.isSingleShot()


@pytest.mark.freeze_time("2344-9-21 7:48:5")
def test_get_new_filename():
    with patch(
        "package.utils.uuid.uuid4",
        new=lambda: uuid.UUID("d9ca35e1-0b4b-4d42-9f0d-aa07f5dbf1a5"),
    ):
        assert get_new_filename(".jpg") == "2344-09-21-07-48-05-d9ca3.jpg"


@pytest.mark.parametrize(
    "cle",
    [
        ("KEY_1"),
        ("KEY_2"),
        ("KEY_3"),
        ("KEY_4"),
    ],
)
def test_KeyWizard(cle):
    if WIN:
        assert getattr(KeyW, cle) == KEYS[cle][1]
        assert getattr(KeyW, cle) == {"nativeScanCode": KEYS[cle][1]}
        assert getattr(KeyW, cle) != "bla"
    else:
        assert getattr(KeyW, cle) == KEYS[cle][0]
        assert getattr(KeyW, cle) == {"nativeScanCode": KEYS[cle][0]}
        assert getattr(KeyW, cle) != "bla"


def test_read_qrc():
    ressource = Path(__file__).parents[2] / "src" / "qml" / "main.qml"
    assert ressource.is_file()
    assert ressource.read_text() == read_qrc(":/qml/main.qml").replace("\r\n", "\n")

    with pytest.raises(FileNotFoundError):
        read_qrc(":/qml/blabdlzebflzef.qml")


def test_Wdict():
    a = WDict("aaa.bbb.ccc", 2)
    assert a == {"aaa": {"bbb": {"ccc": 2}}}
    a["aaa"]["bbb"]["ddd"] = 5
    a.update({"aaa": {"bbb": {"ccc": 6}}})
    assert a == {"aaa": {"bbb": {"ccc": 6, "ddd": 5}}}

    assert WDict({"aa": "bbb"}) == {"aa": "bbb"}


def test_shift_list():
    a = lambda: [0, 1, 2, 3, 4, 5]
    props = [
        # index 0 vers le bas
        ((0, 1, 0), (0, 1, 2, 3, 4, 5)),
        ((0, 1, 1), (0, 1, 2, 3, 4, 5)),
        ((0, 1, 2), (1, 0, 2, 3, 4, 5)),
        ((0, 1, 3), (1, 2, 0, 3, 4, 5)),
        ((0, 1, 4), (1, 2, 3, 0, 4, 5)),
        ((0, 1, 5), (1, 2, 3, 4, 0, 5)),
        ((0, 1, 6), (1, 2, 3, 4, 5, 0)),
        ((0, 1, 7), (1, 2, 3, 4, 5, 0)),
        # index 1 vers le bas
        ((1, 1, 2), (0, 1, 2, 3, 4, 5)),
        ((1, 1, 3), (0, 2, 1, 3, 4, 5)),
        ((1, 1, 4), (0, 2, 3, 1, 4, 5)),
        ((1, 1, 5), (0, 2, 3, 4, 1, 5)),
        ((1, 1, 6), (0, 2, 3, 4, 5, 1)),
        ((1, 1, 7), (0, 2, 3, 4, 5, 1)),
        # index 4 vers le bas
        ((4, 1, 5), (0, 1, 2, 3, 4, 5)),
        ((4, 1, 6), (0, 1, 2, 3, 5, 4)),
        ((4, 1, 7), (0, 1, 2, 3, 5, 4)),
        # index 0 vers le bas, 2 éléments
        ((0, 2, 1), (0, 1, 2, 3, 4, 5)),
        ((0, 2, 2), (0, 1, 2, 3, 4, 5)),
        ((0, 2, 3), (2, 0, 1, 3, 4, 5)),
        ((0, 2, 4), (2, 3, 0, 1, 4, 5)),
        ((0, 2, 5), (2, 3, 4, 0, 1, 5)),
        ((0, 2, 6), (2, 3, 4, 5, 0, 1)),
        ((0, 2, 7), (2, 3, 4, 5, 0, 1)),
        # index 1 vers le bas, 2 éléments
        ((1, 2, 2), (0, 1, 2, 3, 4, 5)),
        ((1, 2, 3), (0, 1, 2, 3, 4, 5)),
        ((1, 2, 4), (0, 3, 1, 2, 4, 5)),
        ((1, 2, 5), (0, 3, 4, 1, 2, 5)),
        ((1, 2, 6), (0, 3, 4, 5, 1, 2)),
        ((1, 2, 8), (0, 3, 4, 5, 1, 2)),
        # index 5 vers le haut
        ((5, 1, 0), (5, 0, 1, 2, 3, 4)),
        ((5, 1, 1), (0, 5, 1, 2, 3, 4)),
        ((5, 1, 2), (0, 1, 5, 2, 3, 4)),
        ((5, 1, 3), (0, 1, 2, 5, 3, 4)),
        ((5, 1, 4), (0, 1, 2, 3, 5, 4)),
        ((5, 1, 5), (0, 1, 2, 3, 4, 5)),
        # index 4 vers le haut, 2 élement
        ((4, 2, 0), (4, 5, 0, 1, 2, 3)),
        ((4, 2, 1), (0, 4, 5, 1, 2, 3)),
        ((4, 2, 2), (0, 1, 4, 5, 2, 3)),
        ((4, 2, 3), (0, 1, 2, 4, 5, 3)),
        ((4, 2, 4), (0, 1, 2, 3, 4, 5)),
        ((4, 2, 5), (0, 1, 2, 3, 4, 5)),
    ]

    for inp, out in props:
        res = shift_list(a(), *inp)
        assert list(res) == list(out)


versions_values = [
    (34543453, "0"),
    (0, "0"),
    (12342, "1.23.42"),
    (912342, "91.23.42"),
    (10302, "1.03.02"),
    (100302, "10.03.02"),
    (100300, "10.03.0"),
    (100001, "10.00.01"),
    (1, "0.0.1"),
    (12, "0.0.12"),
    (1232, "0.12.32"),
    (132, "0.1.32"),
    (1002, "0.10.2"),
    (30000, "3.0.0"),
    (30000, "3"),
    (30300, "3.3"),
]


class TestVersion:
    def test_init(self):
        assert Version("3") == Version("3.0.0")
        assert Version("30") == Version("30.0.0")
        assert Version("0") == Version("0.0.0")
        assert Version("3.2") == Version("3.2.0")
        assert Version("30.2") == Version("30.2.0")
        assert Version("30.20") == Version("30.20.0")

        for v in ["333", "1.333", "123.1", "123.23.23", "12.233.23", "12.23.323"]:
            with pytest.raises(InvalidVersion):
                Version(v)

    def test_parse_int(self):
        for v_int, v_str in versions_values:
            assert Version(v_int) == Version(v_str)

    def test_to_int(self):
        for v_int, v_str in versions_values[1:]:
            assert Version(v_str).to_int() == v_int


def test_pathize():
    name = Path(__file__).name
    res = Path(__file__).resolve()
    assert pathize(QUrl.fromLocalFile(name)) == res
    assert pathize(name) == res
    assert pathize(name) == res
    assert res.is_absolute()
