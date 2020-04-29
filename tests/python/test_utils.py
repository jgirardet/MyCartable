import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


from package.utils import create_singleshot, get_new_filename


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
