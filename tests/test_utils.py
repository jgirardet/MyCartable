from unittest.mock import MagicMock

import pytest


from package.utils import create_singleshot


def test_create_single_shot():
    def bla():
        pass

    a = create_singleshot(bla)
    assert a.isSingleShot()
