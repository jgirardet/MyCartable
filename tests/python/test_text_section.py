import uuid
from string import Template
from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtGui import QTextDocument, QColor, QFont, QKeyEvent, QBrush
from factory import f_textSection, TextSection

# from package.page.text_section import DocumentEditor, RE_AUTOPARAGRAPH
from bs4 import BeautifulSoup
from package.utils import KeyW
from pony.orm.core import db_session, flush

from package.page.text_section import (
    CSS,
    blockCharFormat,
    BLACK,
    _CSS_BASE,
    blockFormat,
    RE_AUTOPARAGRAPH_DEBUT,
    RE_AUTOPARAGRAPH_FIN,
    TextSectionEditor,
    collect_block_and_char_format,
    BLUE,
    GREEN,
    RED,
    TextSectionFormatter,
)

from fixtures import compare_char_format


def test_css():
    assert (
        CSS.replace("\n", "").replace(" ", "")
        == """body {
     color:#363636;
     background-color:#E6E6E6;
     font-family:Verdana;
     font-size:20pt;
     font-weight:96;
     margin-top:12px;
     margin-bottom:0px;
}
p {
     color:#363636;
     font-family:Verdana;
     font-size:20pt;
     font-weight:96;
     margin-top:12px;
     margin-left:10px;
     margin-right:10px;
     margin-bottom:0px;
}
h1 {
     font-family:Verdana;
     font-size:30pt;
     color:#D40020;
     font-weight:600;
     text-decoration:underline;
     text-transform:uppercase;
     margin-top:18px;
     margin-left:10px;
     margin-right:10px;
     margin-bottom:0px;
}
h2 {
     font-family:Verdana;
     font-size:25pt;
     color:#006A4E;
     font-weight:600;
     text-decoration:underline;
     margin-top:16px;
     margin-left:10px;
     margin-right:10px;
     margin-bottom:0px;
}
h3 {
     font-family:Verdana;
     font-size:25pt;
     color:#0048BA;
     font-weight:400;
     text-decoration:underline;
     margin-top:14px;
     margin-left:10px;
     margin-right:10px;
     margin-bottom:0px;
}
h4 {
     font-family:Verdana;
     font-size:21pt;
     color:#363636;
     font-weight:400;
     text-decoration:underline;
     margin-top:18px;
     margin-left:10px;
     margin-right:10px;
     margin-bottom:0px;
}
 """.replace(
            "\n", ""
        ).replace(
            " ", ""
        )
    )


def test_p_before_h_in_css():
    # l'ordre dans le css base est importannt
    a = list(_CSS_BASE.keys())
    assert a[0] == "body"
    assert a[1] == "p"
    assert a[2] == "h1"
    assert a[3] == "h2"
    assert a[4] == "h3"
    assert a[5] == "h4"


def test_BlockFormat():
    assert blockFormat[0] == blockFormat["p"]
    assert blockFormat[1] == blockFormat["h1"]
    with pytest.raises(KeyError):
        blockFormat[3.5]


@pytest.mark.parametrize("level", ["h1", "h2", "h3", "h4", "p"])
def test_block_char_format(level):
    fmt = blockCharFormat[level]
    assert fmt.foreground().color() == QColor(_CSS_BASE[level]["color"])
    # assert fmt.background().color() == QColor(
    #     _CSS_BASE[level].get(
    #         "background-color", _CSS_BASE["body"].get("background-color")
    #     )
    # )
    assert fmt.fontPointSize() == float(_CSS_BASE[level]["font-size"].strip("pt"))
    under = (
        fmt.fontUnderline() == True
        if _CSS_BASE[level].get("text-decoration", False)
        else False
    )
    assert fmt.fontUnderline() == under

    assert fmt.fontWeight() == int(_CSS_BASE[level].get("font-weight")) / 8
    tf = _CSS_BASE[level].get("text-transform")
    if tf:
        tf = QFont.AllUppercase if tf == "uppercase" else QFont.AllLowercase
    else:
        tf = QFont.MixedCase
    assert fmt.fontCapitalization() == tf


@pytest.mark.parametrize("level", ["h1", "h2", "h3", "h4", "p"])
def test_block_format(level):
    fmt = blockFormat[level]
    if level == "p":
        assert fmt.headingLevel() == 0
    else:
        assert fmt.headingLevel() == int(level[1])
    # assert fmt.foreground().color() == _CSS_BASE[level]["color"]
    assert fmt.topMargin() == float(
        _CSS_BASE[level]
        .get("margin-top", _CSS_BASE["body"].get("margin-top"))
        .strip("px")
    )
    assert fmt.leftMargin() == float(_CSS_BASE[level]["margin-left"].strip("px"))
    assert fmt.rightMargin() == float(_CSS_BASE[level]["margin-right"].strip("px"))


@pytest.mark.parametrize(
    "string",
    [
        "# a",
        "# ab",
        "# abc",
        "## a",
        "## ab",
        "### a",
        "#### a",
        "# a",
        "# a a",
        "# a ",
    ],
)
def test_re_autoparagraph_debut(string):
    assert RE_AUTOPARAGRAPH_DEBUT.match(string)


@pytest.mark.parametrize("string", [" # a", "#", "# ", "#a"])
def test_re_autoparagraph_debut_fail(string):
    assert not RE_AUTOPARAGRAPH_DEBUT.match(string)


@pytest.mark.parametrize(
    "string",
    ["a #", "ab #", "abc #", "a ##", "ab ##", "a ###", "a ####", "a b c #", " a #"],
)
def test_re_autoparagraph_fin(string):
    assert RE_AUTOPARAGRAPH_FIN.match(string)


@pytest.mark.parametrize("string", [" #", "#", "a#"])
def test_re_autoparagraph_fin_fail(string):
    assert not RE_AUTOPARAGRAPH_FIN.match(string)


@pytest.fixture()
def doc() -> TextSectionEditor:
    def factory(content="", pos=0, selectionStart=0, selectionEnd=0):
        selectionStart = selectionStart or pos
        selectionEnd = selectionEnd or pos
        obj = TextSectionEditor(
            uuid.uuid4(), content, pos, selectionStart, selectionEnd
        )
        obj._update_ddb = MagicMock()

        # doc.bs4 = lambda: BeautifulSoup(
        #     doc.document.toHtml().replace("\n", ""), "html.parser"
        return obj

    return factory


@pytest.fixture()
def char_fmt():
    res, _ = collect_block_and_char_format()
    return res


@pytest.fixture()
def block_fmt():
    _, res = collect_block_and_char_format()
    return res


def event(key, text, modifiers, scancode=0):
    ev = QKeyEvent(QKeyEvent.KeyPress, key, modifiers, text)
    return {
        "key": ev.key(),
        "nativeScanCode": scancode,
        "text": ev.text(),
        "modifiers": ev.modifiers(),
    }


p_style_string = f""" margin-top:{_CSS_BASE["p"]["margin-top"]}; margin-bottom:{_CSS_BASE["body"]["margin-bottom"]}; margin-left:{_CSS_BASE["p"]["margin-left"]}; margin-right:{_CSS_BASE["p"]["margin-right"]}; -qt-block-indent:0; text-indent:0px;"""
span_style_string = f""" font-family:'{_CSS_BASE["p"]["font-family"]}'; font-size:{_CSS_BASE["p"]["font-size"]}; font-weight:{_CSS_BASE["p"]["font-weight"]}; color:{_CSS_BASE["p"]["color"].lower()};"""
p_span = Template(
    f"""<p style= "{p_style_string}"><span style="{span_style_string}">$val</span></p>"""
)
# p_base_no_bg = f"""<p style= " margin-top:{_CSS_BASE["p"]["margin-top"]}; margin-bottom:{_CSS_BASE["body"]["margin-bottom"]}; margin-left:{_CSS_BASE["p"]["margin-left"]}; margin-right:{_CSS_BASE["p"]["margin-right"]}; -qt-block-indent:0; text-indent:0px;">"""
# span_base = f"""<span style=" font-family:'{_CSS_BASE["p"]["font-family"]}'; font-size:{_CSS_BASE["p"]["font-size"]}; font-weight:{_CSS_BASE["p"]["font-weight"]}; color:{_CSS_BASE["p"]["color"].lower()};">"""
# p_empty = f"""<p style="-qt-paragraph-type:empty; margin-top:{_CSS_BASE["p"]["margin-top"]}; margin-bottom:0px; margin-left:{_CSS_BASE["p"]["margin-left"]}; margin-right:{_CSS_BASE["p"]["margin-right"]}; -qt-block-indent:0; text-indent:0px; font-size:{_CSS_BASE["p"]["font-size"]}; font-weight:{_CSS_BASE["p"]["font-weight"]}; color:{_CSS_BASE["p"]["color"].lower()};"><br /></p>"""
p_empty = f"""<p style="-qt-paragraph-type:empty;{p_style_string}{span_style_string}"><br /></p>"""
h1 = Template(
    f"""<h1 style=" margin-top:{_CSS_BASE["h1"]["margin-top"]}; margin-bottom:0px; margin-left:{_CSS_BASE["h1"]["margin-left"]}; margin-right:{_CSS_BASE["h1"]["margin-right"]}; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Verdana'; font-size:{_CSS_BASE["h1"]["font-size"]}; font-weight:{_CSS_BASE["h1"]["font-weight"]}; text-decoration: {_CSS_BASE["h1"]["text-decoration"]}; color:{_CSS_BASE["h1"]["color"].lower()}; text-transform:{_CSS_BASE["h1"]["text-transform"]};">$val</h1>"""
)


def cmp_html(lhs, il, rhs, ir=0):
    il = il * 2 + 1  # on saute les \n
    sl = BeautifulSoup(lhs, "html.parser")
    lhs = sl.body.contents[il]
    rl = BeautifulSoup(rhs, "html.parser")
    rhs = rl.contents[ir]
    assert lhs == rhs


def has_style_attr(html, para, span, key, value):
    x = BeautifulSoup(html, "html.parser")
    styles = (
        x.body.contents[para * 2 + 1]
        .contents[span]
        .attrs["style"]
        .replace(" ", "")
        .split(";")
    )
    for kv in styles:
        k, v = kv.split(":")
        if k == key:
            assert v == value
            return True
    assert False, f"{key} not in {styles}"


class TestSectionEditor:
    def test_init(self, doc):
        d = doc("<p>acd</p>", pos=3, selectionStart=4, selectionEnd=5)
        assert isinstance(d.sectionId, uuid.UUID)
        assert d.defaultStyleSheet() == CSS
        cmp_html(d.toHtml(), 0, p_span.substitute(val="acd"))

        assert d.cur.position() == 3
        assert d.s_start == 4
        assert d.s_end == 5
        d.result = {"text": "", "cursorPosition": 3, "eventAccepted": False}
        self.pending = False

    def test_len(self, doc):
        d = doc("<p>acd</p>")
        assert d.len == 4

    def test_s_len(self, doc):
        d = doc("<p>acd</p>", selectionStart=4, selectionEnd=7)
        assert d.s_len == 3

    def test_pos(self, doc):
        d = doc("<p>acd</p>", pos=6)
        assert d.pos == 0
        d = doc("<p>acd</p>", pos=2)
        assert d.pos == 2

    def test_onChange(self, doc):
        d = doc("<p>acd</p>", pos=3)
        res_text = d.toHtml()
        res = d.onChange()
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 3
        assert res["text"] == res_text

    def test_onKey_no_change(self, doc):
        d = doc("<p>acd</p>", pos=3)
        res_text = d.toHtml()
        event = {"key": int(Qt.Key_A), "modifiers": int(Qt.NoModifier)}
        res = d.onKey(event)
        d._update_ddb.assert_not_called()
        assert res["eventAccepted"] == False
        assert res["cursorPosition"] == 3
        assert res["text"] == res_text

    def test_onKey_return_no_change(self, doc):
        d = doc("<p>acd</p>", pos=3)
        res_text = d.toHtml()
        event = {"key": int(Qt.Key_Return), "modifiers": int(Qt.NoModifier)}
        res = d.onKey(event)
        d._update_ddb.assert_not_called()
        assert res["eventAccepted"] == False
        assert res["cursorPosition"] == 3
        assert res["text"] == res_text

    def test_onKey_return_header_autoformat(self, doc):
        d = doc("<p># a</p>", pos=3)
        event = {"key": int(Qt.Key_Return), "modifiers": int(Qt.NoModifier)}
        res = d.onKey(event)
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 2
        cmp_html(res["text"], 0, h1.substitute(val="a"))
        cmp_html(res["text"], 1, p_empty)

    def test_onKey_return_header_autoformat_reverse(self, doc):
        d = doc("<p>a #</p>", pos=3)
        event = {"key": int(Qt.Key_Return), "modifiers": int(Qt.NoModifier)}
        res = d.onKey(event)
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 2
        cmp_html(res["text"], 0, h1.substitute(val="a"))
        cmp_html(res["text"], 1, p_empty)

    def test_onKey_return_p_after_heading(self, doc):
        d = doc("<h1>a</h1>", pos=3)
        event = {"key": int(Qt.Key_Return), "modifiers": int(Qt.NoModifier)}
        res = d.onKey(event)
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 2
        cmp_html(res["text"], 1, p_empty)

    def test_onKey_return_p_shift_modifier(self, doc):
        d = doc("<p>abc</p>", pos=1)
        event = {"key": int(Qt.Key_Return), "modifiers": int(Qt.ControlModifier)}
        res = d.onKey(event)
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 4
        cmp_html(res["text"], 0, p_span.substitute(val="abc"))
        cmp_html(res["text"], 1, p_empty)

    def test_onKey_return_p_ctrl_modifier(self, doc):
        d = doc("<p>abc</p>", pos=1)
        event = {"key": int(Qt.Key_Return), "modifiers": int(Qt.ShiftModifier)}
        res = d.onKey(event)
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 0
        cmp_html(res["text"], 0, p_empty)
        cmp_html(res["text"], 1, p_span.substitute(val="abc"))

    def test_onKey_u_ctrl_modifier(self, doc, char_fmt):
        d = doc("<p>abc</p>", pos=1)
        res = d.onKey(event(Qt.Key_U, "u", Qt.ControlModifier))
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 3
        assert has_style_attr(res["text"], 0, 0, "text-decoration", "underline")
        cfmt = char_fmt["p"]
        cfmt.setFontUnderline(True)
        assert d.cur.charFormat() == cfmt

    #
    @pytest.mark.parametrize(
        "key, text, scancode, color",
        [
            (Qt.Key_1, "1", KeyW.KEY_1, BLACK,),
            (Qt.Key_2, "2", KeyW.KEY_2, BLUE,),
            (Qt.Key_3, "3", KeyW.KEY_3, GREEN,),
            (Qt.Key_4, "4", KeyW.KEY_4, RED,),
        ],
    )
    def test_onKey_Number_ctrl_modifier(
        self, key, text, scancode, color, doc, char_fmt
    ):
        d = doc("<p>abc</p>", pos=1)
        d.cur.blockCharFormat().setForeground(QBrush(QColor("#123456")))
        d.cur.setPosition(1)
        res = d.onKey(event(key, text, Qt.ControlModifier, scancode=scancode))
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 3
        assert has_style_attr(res["text"], 0, 0, "color", color.lower())
        cfmt = char_fmt["p"]
        cfmt.setForeground(QBrush(QColor(color)))
        assert compare_char_format(d.cur.charFormat(), cfmt)

    def test_onLoad(self, doc, reset_db, char_fmt, block_fmt):
        f = f_textSection(
            text="""<body><h1>bli</h1><p>noir<span style="color:#123456;">bleu</span></p></body>"""
        )
        d = doc()
        d.sectionId = str(f.id)
        res = d.onLoad()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 13

        # partie H1
        titre = d.begin()
        assert titre.blockFormat() == block_fmt[1]
        assert titre.text() == "bli"
        assert compare_char_format(titre.charFormat(), char_fmt[1])

        # partie paragraphe sans formattage supplémentaire
        parag = titre.next()
        assert parag.blockFormat() == block_fmt[0]
        assert compare_char_format(parag.charFormat(), char_fmt[0])
        fg = list(parag.begin())
        assert fg[0].fragment().text() == "noir"

        # partie avec un span
        assert fg[1].fragment().text() == "bleu"
        assert fg[1].fragment().charFormat().foreground().color() == QColor("#123456")

    def test_on_Menu_no_selection(self, doc, char_fmt, block_fmt):
        d = doc("<p>abc def</p>", pos=1)
        res = d.onMenu(style={"fgColor": RED})
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 3

        # compare html
        assert has_style_attr(res["text"], 0, 0, "color", RED.lower())
        assert has_style_attr(res["text"], 0, 1, "color", BLACK.lower())

        # compare fragment
        fg = list(d.begin())
        assert fg[0].fragment().charFormat().foreground().color() == QColor(RED)
        assert fg[1].fragment().charFormat().foreground().color() == QColor(BLACK)

    @pytest.mark.parametrize("pos, s_start, s_end", [(1, 1, 5), (5, 1, 5)])
    def test_on_Menu_selection(self, doc, char_fmt, block_fmt, pos, s_start, s_end):
        d = doc("<p>abc def</p>", pos=pos, selectionStart=s_start, selectionEnd=s_end)
        res = d.onMenu(style={"fgColor": RED})
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 5

        # compare html
        assert has_style_attr(res["text"], 0, 0, "color", BLACK.lower())
        assert has_style_attr(res["text"], 0, 1, "color", RED.lower())
        assert has_style_attr(res["text"], 0, 2, "color", BLACK.lower())

        # compare fragment
        fg = list(d.begin())
        assert fg[0].fragment().charFormat().foreground().color() == QColor(BLACK)
        assert fg[1].fragment().charFormat().foreground().color() == QColor(RED)
        assert fg[2].fragment().charFormat().foreground().color() == QColor(BLACK)

    #
    def test_on_Menu_underline(self, doc, char_fmt, block_fmt):
        d = doc("<p>abc def</p>", pos=1, selectionStart=1, selectionEnd=5)
        res = d.onMenu(style={"underline": True})
        d._update_ddb.assert_called()
        assert res["eventAccepted"] == True
        assert res["cursorPosition"] == 5

        # compare html
        assert has_style_attr(res["text"], 0, 1, "text-decoration", "underline")

        # compare fragment
        fg = list(d.begin())
        assert not fg[0].fragment().charFormat().fontUnderline()
        assert fg[1].fragment().charFormat().fontUnderline()
        assert not fg[2].fragment().charFormat().fontUnderline()

    def test_onMenu_no_change(self, doc):
        d = doc("<p>acd</p>", pos=3)
        res_text = d.toHtml()
        res = d.onMenu(style={"blabla": True})
        d._update_ddb.assert_not_called()
        assert res["eventAccepted"] == False
        assert res["cursorPosition"] == 3
        assert res["text"] == res_text

    def test_update_ddb(self, ddbr):
        f = f_textSection(text="""<body><p>noir</p></body>""")
        d = TextSectionEditor(1, content="""<body><p>noirA</p></body>""")
        d.sectionId = str(f.id)
        d._update_ddb()
        with db_session:
            assert TextSection[f.id].text == "<body><p><span>noirA</span></p></body>"


@pytest.mark.parametrize(
    "data, res",
    [
        ("<p>noir</p>", "<body><p><span>noir</span></p></body>"),
        (
            """<p><span style=" color:#123456;">noir</p>""",
            """<body><p><span style=" color:#123456;">noir</span></p></body>""",
        ),
        ("""<h1>noir</h1>""", """<body><h1>noir</h1></body>""",),
        ("""<h2>noir</h2>""", """<body><h2>noir</h2></body>""",),
        ("""<h3>noir</h3>""", """<body><h3>noir</h3></body>""",),
        ("""<h4>noir</h4>""", """<body><h4>noir</h4></body>""",),
        (
            """<h1>noir</h1><p><span style=" color:#123456;">noir</p><h2>noir</h2>""",
            """<body><h1>noir</h1><p><span style=" color:#123456;">noir</span></p><h2>noir</h2></body>""",
        ),
        (
            f"""<p><span style=" color:{_CSS_BASE["p"]["color"]};">noir</p>""",
            """<body><p><span>noir</span></p></body>""",
        ),
        (
            f"""<p><span style=" font-family:{_CSS_BASE["p"]["font-family"]};">noir</p>""",
            """<body><p><span>noir</span></p></body>""",
        ),
        (
            f"""<p><span style=" font-family:blum;">noir</p>""",
            """<body><p><span style=" font-family:blum;">noir</span></p></body>""",
        ),
        (f"""<p></p>""", """<body><p><span><br/></span></p></body>"""),
        (
            f"""<p><span style=" text-transform:lowercase;">noir</p>""",
            """<body><p><span style=" text-transform:lowercase;">noir</span></p></body>""",
        ),
    ],
)
def test_TextSectoinFormatter(data, res):
    a = QTextDocument()
    a.setDefaultStyleSheet(CSS)
    a.setHtml(data)
    builded = TextSectionFormatter(a.toHtml()).build_body()
    assert builded == res


def test_textsectoinformatter_empty_h():
    a = TextSectionFormatter("""<body><h1></h1></body>""")
    assert a.build_body() == """<body><h1></h1></body>"""


def test_textsectoinformatter_tag_inconnu():
    a = TextSectionFormatter("""<body><bla></bla></body>""")
    with pytest.raises(TypeError):
        a.build_body()


def test_textsectoinformatter_span_is_str():
    a = TextSectionFormatter("""<body><p>a</p></body>""")
    assert a.build_body() == """<body><p>a</p></body>"""
