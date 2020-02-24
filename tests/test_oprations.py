import pytest
from package.operations.api import match, convert_addition, create_operation


class TestAddition:
    @pytest.mark.parametrize(
        "string, res",
        [
            ("1+2", ("+", ["1", "2"])),
            ("1+2+3", ("+", ["1", "2", "3"])),
            ("111+2222+33333", ("+", ["111", "2222", "33333"])),
            ("111-2222-33333", ("-", ["111", "2222", "33333"])),
            ("111*2222*33333", ("*", ["111", "2222", "33333"])),
            ("111/2222/33333", ("/", ["111", "2222", "33333"])),
        ],
    )
    def test_match(self, string, res):
        assert match(string) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            (["1", "2"], [["", ""], ["", "1"], ["+", "2"], ["", ""]]),
            (["9", "8"], [["", "", ""], ["", "", "9"], ["+", "", "8"], ["", "", ""],],),
            (
                ["1", "2", "3"],
                [["", ""], ["", "1"], ["+", "2"], ["+", "3"], ["", ""],],
            ),
            (
                ["1", "25", "348", "4789"],
                [
                    ["", "", "", "", ""],
                    ["", "", "", "", "1"],
                    ["+", "", "", "2", "5"],
                    ["+", "", "3", "4", "8"],
                    ["+", "4", "7", "8", "9"],
                    ["", "", "", "", ""],
                ],
            ),
        ],
    )
    def test_convert_addition(self, string, res):
        assert convert_addition(string) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            ("1+2", [["", ""], ["", "1"], ["+", "2"], ["", ""]]),  # normal
            (" 1 + 2 ", [["", ""], ["", "1"], ["+", "2"], ["", ""]]),  # space
            ("1A2", None)  # no match
            # (["9", "8"], [["", "", ""], ["", "", "9"], ["+", "", "8"], ["", "", ""] ])
        ],
    )
    def test_create_operations(self, string, res):
        assert create_operation(string) == res
