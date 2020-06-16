import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


from package.utils import (
    create_singleshot,
    get_new_filename,
    KeyW,
    KeyCross,
    WIN,
    KEYS,
    read_qrc,
)


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


@pytest.mark.parametrize("cle", [("KEY_1"), ("KEY_2"), ("KEY_3"), ("KEY_4"),])
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
    assert ressource.read_text().splitlines() == read_qrc(":/qml/main.qml").splitlines()

    with pytest.raises(FileNotFoundError):
        read_qrc(":/qml/blabdlzebflzef.qml")
