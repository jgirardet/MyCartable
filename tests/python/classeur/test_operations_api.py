from decimal import Decimal

import pytest
from mycartable.classeur import (
    DecimalLitteral,
    match,
    convert_addition,
    convert_multiplication,
    convert_division,
    convert_soustraction,
    create_operation,
)


class TestDecimal:
    @pytest.mark.parametrize(
        "inp, value, v_int, v_dec, l_int, l_dec",
        [
            ("1", "1", Decimal(1), Decimal(0), 1, 0),
            ("12", "12", Decimal(12), Decimal(0), 2, 0),
            ("0.3", "0.3", Decimal(0), Decimal("0.3"), 1, 1),
            ("0,3", "0.3", Decimal(0), Decimal("0.3"), 1, 1),
            ("12,311", "12.311", Decimal(12), Decimal("0.311"), 2, 3),
            ("0.10", "0.10", Decimal(0), Decimal("0.10"), 1, 2),
        ],
    )
    def test_init(self, inp, value, v_int, v_dec, l_int, l_dec):
        a = DecimalLitteral(inp)
        assert a == Decimal(value)
        assert a.int == v_int
        assert a.dec == v_dec
        assert a.l_int == l_int
        assert a.l_dec == l_dec

    @pytest.mark.parametrize("value, res", [("1", True), ("1.1", False)])
    def test_is_int(self, value, res):
        a = DecimalLitteral(value)
        assert a.is_int() == res

    @pytest.mark.parametrize(
        "value, size, apres, res",
        [
            ("1", 3, 0, ["", "", "1"]),
            ("1", 4, 0, ["", "", "", "1"]),
            ("1", 4, 1, ["", "1", "", ""]),
            (
                "1",
                8,
                3,
                [
                    "",
                    "",
                    "",
                    "1",
                    "",
                    "",
                    "",
                    "",
                ],
            ),
            ("12", 3, 0, ["", "1", "2"]),
            ("1.1", 3, 0, ["1", ",", "1"]),
            ("1,1", 3, 0, ["1", ",", "1"]),
            ("211,2", 10, 4, ["", "", "2", "1", "1", ",", "2", "", "", ""]),
            ("11,20", 10, 4, ["", "", "", "1", "1", ",", "2", "0", "", ""]),
            ("0,20", 6, 3, ["", "0", ",", "2", "0", ""]),
        ],
    )
    def test_to_string_list_addition(self, value, size, apres, res):
        a = DecimalLitteral(value)
        assert a.to_string_list_addition(size, apres_virgule=apres) == res

    @pytest.mark.parametrize(
        "value, size, ligne,  apres, res",
        [
            ("1", 2, 0, 0, ["", "", "1", ""]),
            (
                "11",
                3,
                0,
                0,
                [
                    "",
                    "",
                    "1",
                    "",
                    "",
                    "1",
                    "",
                ],
            ),
            (
                "111",
                3,
                0,
                0,
                [
                    "",
                    "",
                    "1",
                    "",
                    "",
                    "1",
                    "",
                    "",
                    "1",
                    "",
                ],
            ),
            (
                "1",
                2,
                1,
                0,
                [
                    "-",
                    "",
                    "1",
                    "",
                ],
            ),
            ("11", 3, 1, 0, ["-", "", "1", "", "", "1", ""]),
            ("111", 3, 1, 0, ["-", "", "1", "", "", "1", "", "", "1", ""]),
            ("3", 6, 1, 0, ["-", "", "", "", "3", ""]),
            ("1", 8, 0, 1, ["", "", "1", "", ",", "", "0", ""]),
            ("1,1", 3, 0, 1, ["", "", "1", "", ",", "", "1", ""]),
            (
                "11,11",
                3,
                0,
                1,
                ["", "", "1", "", "", "1", "", ",", "", "1", "", "", "1", ""],
            ),
            ("1,1", 8, 1, 1, ["-", "", "1", "", ",", "", "1", ""]),
            ("1,1", 11, 1, 2, ["-", "", "1", "", ",", "", "1", "", "", "0", ""]),
            ("1,1", 12, 1, 2, ["-", "", "", "1", "", ",", "", "1", "", "", "0", ""]),
            (
                "11,11",
                14,
                1,
                2,
                ["-", "", "1", "", "", "1", "", ",", "", "1", "", "", "1", ""],
            ),
            (
                "11,11",
                17,
                1,
                2,
                [
                    "-",
                    "",
                    "",
                    "",
                    "",
                    "1",
                    "",
                    "",
                    "1",
                ]
                + [
                    "",
                    ",",
                    "",
                    "1",
                    "",
                    "",
                    "1",
                    "",
                ],
            ),
            (
                "11,11",
                17,
                1,
                3,
                [
                    "-",
                    "",
                    "1",
                    "",
                    "",
                    "1",
                    "",
                    ",",
                    "",
                ]
                + [
                    "1",
                    "",
                    "",
                    "1",
                    "",
                    "",
                    "0",
                    "",
                ],
            ),
            ("0,20", 10, 0, 2, ["", "", "0", "", ",", "", "2", "", "", "0", ""]),
            ("0,20", 10, 1, 2, ["-", "", "0", "", ",", "", "2", "", "", "0", ""]),
            (
                "0,20",
                14,
                1,
                3,
                ["-", "", "0", "", ",", "", "2", "", "", "0", "", "", "0", ""],
            ),
            ("0,2", 10, 0, 2, ["", "", "0", "", ",", "", "2", "", "", "0", ""]),
            (
                "0,20",
                14,
                0,
                3,
                ["", "", "0", "", ",", "", "2", "", "", "0", "", "", "0", ""],
            ),
            ("20", 11, 0, 1, ["", "", "2", "", "", "0", "", ",", "", "0", ""]),
            ("20", 11, 1, 1, ["-", "", "2", "", "", "0", "", ",", "", "0", ""]),
        ],
    )
    def test_to_string_list_soustraction(self, value, size, ligne, apres, res):
        a = DecimalLitteral(value)
        assert a.to_string_list_soustraction(size, ligne, apres_virgule=apres) == res

    @pytest.mark.parametrize(
        "value, size, res",
        [
            ("1", 3, ["", "", "1"]),
            ("1", 4, ["", "", "", "1"]),
            ("1", 4, ["", "", "", "1"]),
            (
                "1",
                8,
                [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "1",
                ],
            ),
            ("12", 3, ["", "1", "2"]),
            ("1.1", 3, ["1", ",", "1"]),
            ("1,1", 3, ["1", ",", "1"]),
            ("211,2", 10, ["", "", "", "", "", "2", "1", "1", ",", "2"]),
            ("11,20", 10, ["", "", "", "", "", "1", "1", ",", "2", "0"]),
            ("0,20", 6, ["", "", "0", ",", "2", "0"]),
        ],
    )
    def test_to_string_list_multiplication(self, value, size, res):
        a = DecimalLitteral(value)
        assert a.to_string_list_multiplication(size) == res

    @pytest.mark.parametrize(
        "value, size, res",
        [
            ("1", 3, ["", "1", ""]),
            ("1", 9, ["", "1", ""] + [""] * 6),
            ("12", 9, ["", "1", "", "", "2", ""] + [""] * 3),
            ("1,2", 9, ["", "1,", "", "", "2", ""] + [""] * 3),
            (
                "211,2",
                20,
                ["", "2", "", "", "1", "", "", "1,", "", "", "2", ""] + [""] * 8,
            ),
        ],
    )
    def test_to_string_list_division(self, value, size, res):
        a = DecimalLitteral(value)
        assert a.to_string_list_division(size) == res


class TestOperation:
    @pytest.mark.parametrize(
        "string, res",
        [
            ("1+2", ("+", ["1", "2"])),
            ("1.2+2.3", ("+", ["1.2", "2.3"])),
            ("1,2+2,3", ("+", ["1,2", "2,3"])),
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
            (["1", "2"], (4, 2, 0, ["", "", "", "1", "+", "2", "", ""])),
            (
                ["1,2", "2,3"],
                (
                    4,
                    4,
                    2,
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "1",
                        ",",
                        "2",
                    ]
                    + [
                        "+",
                        "2",
                        ",",
                        "3",
                        "",
                        "",
                        ",",
                        "",
                    ],
                ),
            ),
            (
                ["1,2", "33,33", "444,444"],
                (
                    5,
                    8,
                    4,
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                    + [
                        "",
                        "",
                        "",
                        "1",
                        ",",
                        "2",
                        "",
                        "",
                    ]
                    + [
                        "+",
                        "",
                        "3",
                        "3",
                        ",",
                        "3",
                        "3",
                        "",
                    ]
                    + [
                        "+",
                        "4",
                        "4",
                        "4",
                        ",",
                        "4",
                        "4",
                        "4",
                    ]
                    + [
                        "",
                        "",
                        "",
                        "",
                        ",",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
            (
                ["1.2", "2.3"],
                (
                    4,
                    4,
                    2,
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "1",
                        ",",
                        "2",
                    ]
                    + [
                        "+",
                        "2",
                        ",",
                        "3",
                        "",
                        "",
                        ",",
                        "",
                    ],
                ),
            ),
            (
                ["9", "8"],
                (4, 3, 0, ["", "", "", "", "", "9", "+", "", "8", "", "", ""]),
            ),
            (["1", "2", "3"], (5, 2, 0, ["", "", "", "1", "+", "2", "+", "3", "", ""])),
            (
                ["1", "2,1"],
                (
                    4,
                    4,
                    2,
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "1",
                        "",
                        "",
                    ]
                    + [
                        "+",
                        "2",
                        ",",
                        "1",
                        "",
                        "",
                        ",",
                        "",
                    ],
                ),
            ),
            (
                ["1", "25", "348", "4789"],
                (
                    6,
                    5,
                    0,
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "1",
                    ]
                    + [
                        "+",
                        "",
                        "",
                        "2",
                        "5",
                    ]
                    + [
                        "+",
                        "",
                        "3",
                        "4",
                        "8",
                    ]
                    + [
                        "+",
                        "4",
                        "7",
                        "8",
                        "9",
                    ]
                    + [
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
        ],
    )
    def test_convert_addition(self, string, res):
        assert convert_addition(string) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            (
                ["2", "1"],
                (3, 4, 0, ["", "", "2", "", "-", "", "1", "", "", "", "", ""]),
            ),
            (
                ["22", "11"],
                (
                    3,
                    7,
                    0,
                    [
                        "",
                        "",
                        "2",
                        "",
                        "",
                        "2",
                        "",
                        "-",
                        "",
                        "1",
                        "",
                        "",
                        "1",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
            (
                ["222", "111"],
                (
                    3,
                    10,
                    0,
                    [
                        "",
                        "",
                        "2",
                        "",
                        "",
                        "2",
                        "",
                        "",
                        "2",
                        "",
                    ]
                    + [
                        "-",
                        "",
                        "1",
                        "",
                        "",
                        "1",
                        "",
                        "",
                        "1",
                    ]
                    + [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
            (
                ["15", "3"],
                (
                    3,
                    7,
                    0,
                    [
                        "",
                        "",
                        "1",
                        "",
                        "",
                        "5",
                        "",
                        "-",
                    ]
                    + [
                        "",
                        "",
                        "",
                        "",
                        "3",
                    ]
                    + [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
            (
                ["20", "0,2"],
                (
                    3,
                    11,
                    7,
                    [
                        "",
                        "",
                        "2",
                        "",
                        "",
                        "0",
                        "",
                        ",",
                        "",
                        "0",
                        "",
                    ]
                    + [
                        "-",
                        "",
                        "",
                        "",
                        "",
                        "0",
                        "",
                        ",",
                        "",
                        "2",
                        "",
                    ]
                    + [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ",",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
            (
                ["2,2", "1,1"],
                (
                    3,
                    8,
                    4,
                    [
                        "",
                        "",
                        "2",
                        "",
                        ",",
                        "",
                        "2",
                        "",
                    ]
                    + [
                        "-",
                        "",
                        "1",
                        "",
                        ",",
                        "",
                        "1",
                        "",
                    ]
                    + [
                        "",
                        "",
                        "",
                        "",
                        ",",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
        ],
    )
    def test_convert_soustraction(self, string, res):
        assert convert_soustraction(string) == res

    @pytest.mark.parametrize(
        "numbers, res",
        [
            (["2", "1"], (4, 2, 0, ["", "", "", "2", "x", "1", "", ""])),
            (
                ["6", "2"],
                (4, 3, 0, ["", "", "", "", "", "6", "x", "", "2", "", "", ""]),
            ),
            (
                ["6", "21"],
                (4, 4, 0, [""] * 4 + ["", "", "2", "1", "x", "", "", "6"] + [""] * 4),
            ),
            (
                ["21", "6"],
                (4, 4, 0, [""] * 4 + ["", "", "2", "1", "x", "", "", "6"] + [""] * 4),
            ),
            (
                ["331", "254"],  # res = 84074
                (
                    10,
                    6,
                    0,
                    [""] * 3 * 6
                    + ["", "", "", "3", "3", "1", "x", "", "", "2", "5", "4"]
                    + [""] * 1 * 6
                    + (["+"] + ([""] * 5)) * 3
                    + [""] * 1 * 6,
                ),
            ),
            (
                ["1,1", "5"],  #
                (
                    4,
                    4,
                    1,
                    [""] * 4
                    + ["", "1", ",", "1", "x", "", "", "5"]
                    + [
                        "",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
            (
                ["5", "1,1"],  #
                (
                    4,
                    4,
                    1,
                    [""] * 4
                    + ["", "1", ",", "1", "x", "", "", "5"]
                    + [
                        "",
                        "",
                        "",
                        "",
                    ],
                ),
            ),
            (
                ["23,3", "5,1234"],  # 119,37522
                (
                    10,
                    10,
                    1,
                    [""] * 10 * 3
                    + [""] * 4
                    + list("5,1234")
                    + ["x"]
                    + [""] * 5
                    + list("23,3")
                    + [""] * 10  # permiere
                    + (["+"] + [""] * 9) * 3  # 2 autres + retenues
                    + [""] * 10,  # res
                ),
            ),
            (
                ["23", "23"],  # 119,37522
                (
                    8,
                    4,
                    0,
                    [""] * 4 * 2
                    + [""] * 2
                    + list("23")
                    + ["x"]
                    + [""]
                    + list("23")
                    + [""] * 4  # permiere
                    + (["+"] + [""] * 3) * 2  # 21autres + retenues
                    + [""] * 4,  # res
                ),
            ),
        ],
    )
    def test_convert_multiplication(self, numbers, res):
        assert convert_multiplication(numbers) == res

    @pytest.mark.parametrize(
        "numbers, res",
        [
            (
                ["23", "5"],  # base
                (
                    5,
                    9,
                    0,
                    {
                        "dividende": "23",
                        "diviseur": "5",
                        "datas": ["", "2", "", "", "3", ""] + [""] * 39,
                    },
                ),
            ),
            (
                ["5", "4"],  # base 1,25
                (
                    7,
                    12,
                    0,
                    {
                        "dividende": "5",
                        "diviseur": "4",
                        "datas": ["", "5"] + [""] * 82,
                    },
                ),
            ),
            (
                ["24,3", "3"],  # base
                (
                    5,
                    9,
                    0,
                    {
                        "dividende": "24.3",
                        "diviseur": "3",
                        "datas": [
                            "",
                            "2",
                            "",
                            "",
                            "4,",
                            "",
                            "",
                            "3",
                            "",
                        ]
                        + [""] * 36,
                    },
                ),
            ),
            (
                ["10", "3"],  # division infinite
                (
                    17,
                    27,
                    0,
                    {
                        "dividende": "10",
                        "diviseur": "3",
                        "datas": ["", "1", "", "", "0", ""] + [""] * 453,
                    },
                ),
            ),
            (
                ["3454367", "45"],  # 76763,711111grand nombre et division infinite
                (
                    17,
                    27,
                    0,
                    {
                        "dividende": "3454367",
                        "diviseur": "45",
                        "datas": ["", "3", "", "", "4", "", "", "5", "", "", "4", ""]
                        + ["", "3", "", "", "6", "", "", "7", ""]
                        + [""] * 438,
                    },
                ),
            ),
        ],
    )
    def test_convert_division(self, numbers, res):
        assert convert_division(numbers) == res

    @pytest.mark.parametrize(
        "string, res",
        [
            ("1+2", (4, 2, 0, ["", "", "", "1", "+", "2", "", ""])),  # addition
            (" 1+ 2 ", (4, 2, 0, ["", "", "", "1", "+", "2", "", ""])),  # space
            ("1A2", None),  # no match
            (
                "2-1",
                (3, 4, 0, ["", "", "2", "", "-", "", "1", "", "", "", "", ""]),
            ),  # soustraction
            ("1*2", (4, 2, 0, ["", "", "", "2", "x", "1", "", ""])),  # mul
            (
                "2/1",
                (
                    3,
                    6,
                    0,
                    {
                        "dividende": "2",
                        "diviseur": "1",
                        "datas": ["", "2", "", "", "", ""] + [""] * 12,
                    },
                ),
            ),
        ],
    )
    def test_create_operations(self, string, res):
        assert create_operation(string) == res
