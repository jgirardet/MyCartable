from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtCore import QObject
from PySide2.QtGui import QTextDocument, QTextCursor, QColor, QFont
from package.database.factory import f_textSection, TextSection

# from package.page.text_section import DocumentEditor, RE_AUTOPARAGRAPH
from bs4 import BeautifulSoup
from pony.orm.core import EntityProxy, db_session

from package.page.text_section import (
    CSS,
    blockCharFormat,
    BLACK,
    _CSS_BASE,
    blockFormat,
    RE_AUTOPARAGRAPH_DEBUT,
    RE_AUTOPARAGRAPH_FIN,
    TextSectionEditor,
)


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
}
h1 {
     font-size:30pt;
     color:#D40020;
     font-weight:600;
     text-decoration:underline;
     text-transform:uppercase;
     margin-top:18px;
     margin-left:10px;
     margin-right:10px;
}
h2 {
     font-size:25pt;
     color:#006A4E;
     font-weight:600;
     text-decoration:underline;
     margin-top:16px;
     margin-left:10px;
     margin-right:10px;
}
h3 {
     font-size:25pt;
     color:#0048BA;
     font-weight:400;
     text-decoration:underline;
     margin-top:14px;
     margin-left:10px;
     margin-right:10px;
}
h4 {
     color:#363636;
     font-size:20pt;
     font-weight:400;
     text-decoration:underline;
     margin-top:18px;
     margin-left:10px;
     margin-right:10px;
}
p {
     color:#363636;
     background-color:#E6E6E6;
     font-family:Verdana;
     font-size:20pt;
     font-weight:96;
     margin-top:12px;
     margin-left:10px;
     margin-right:10px;
}
 """.replace(
            "\n", ""
        ).replace(
            " ", ""
        )
    )


def test_BlockFormat():
    assert blockFormat[0] == blockFormat["p"]
    assert blockFormat[1] == blockFormat["h1"]
    with pytest.raises(KeyError):
        blockFormat[3.5]


@pytest.mark.parametrize("level", ["h1", "h2", "h3", "h4", "p"])
def test_block_char_format(level):
    fmt = blockCharFormat[level]
    assert fmt.foreground().color() == _CSS_BASE[level]["color"]
    assert fmt.background().color() == _CSS_BASE[level].get(
        "background-color", _CSS_BASE["body"].get("background-color")
    )
    assert fmt.fontPointSize() == float(_CSS_BASE[level]["font-size"].strip("pt"))
    print(fmt.fontUnderline(), _CSS_BASE[level].get("text-decoration"))
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
    "string", ["# a", "# ab", "# abc", "## a", "## ab", "### a", "#### a", "# a"]
)
def test_re_autoparagraph_debut(string):
    assert RE_AUTOPARAGRAPH_DEBUT.match(string)


@pytest.mark.parametrize("string", [" # a", "#", "# ", "# a ", "#a"])
def test_re_autoparagraph_debut(string):
    assert not RE_AUTOPARAGRAPH_DEBUT.match(string)


@pytest.mark.parametrize(
    "string", ["a #", "ab #", "abc #", "a ##", "ab ##", "a ###", "a ####"]
)
def test_re_autoparagraph_debut(string):
    assert RE_AUTOPARAGRAPH_FIN.match(string)


@pytest.mark.parametrize("string", [" a #", " #", "#", "a#"])
def test_re_autoparagraph_debut(string):
    assert not RE_AUTOPARAGRAPH_FIN.match(string)


@pytest.fixture()
def doc() -> TextSectionEditor:
    def factory(content="", pos=0, selectionStart=0, selectionEnd=0):
        obj = TextSectionEditor(1, content, pos, selectionStart, selectionEnd)
        obj._update_ddb = MagicMock()

        # doc.bs4 = lambda: BeautifulSoup(
        #     doc.document.toHtml().replace("\n", ""), "html.parser"
        return obj

    return factory


p_base = f"""<p style= " margin-top:{_CSS_BASE["p"]["margin-top"]}; margin-bottom:12px; margin-left:{_CSS_BASE["p"]["margin-left"]}; margin-right:{_CSS_BASE["p"]["margin-right"]}; -qt-block-indent:0; text-indent:0px; background-color:{_CSS_BASE["p"]["background-color"].lower()};">"""
span_base = f"""<span style=" font-family:'{_CSS_BASE["p"]["font-family"]}'; font-size:{_CSS_BASE["p"]["font-size"]}; font-weight:{_CSS_BASE["p"]["font-weight"]}; color:{_CSS_BASE["p"]["color"].lower()}; background-color:{_CSS_BASE["p"]["background-color"].lower()};">"""


def cmp_html(lhs, il, rhs, ir):
    lhs = BeautifulSoup(lhs, "html.parser").body.contents[il]
    print(rhs)
    rhs = BeautifulSoup(rhs, "html.parser").contents[ir]
    assert lhs == rhs


class TestSectionEditor:
    def test_init(self, doc):
        d = doc("<p>acd</p>", pos=3, selectionStart=4, selectionEnd=5)
        assert d.sectionId == 1
        assert d.defaultStyleSheet() == CSS
        cmp_html(d.toHtml(), 1, f"{p_base}{span_base}acd</span></p>", 0)
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
        res["eventAccepted"] == True
        res["cursorPosition"] == 3
        res["text"] == res_text


#
# @pytest.mark.parametrize(
#     "pre_content, content, pos, selectionStart, selectionEnd, update_ddb, res_text, cursorPosition, eventAccepted",
#     [("<p>a<p>", "<p>ab<p>", 2, 2, 2, True, "aaa", 2, True),],
# )
# def test_onChange(
#     pre_content,
#     content,
#     pos,
#     selectionStart,
#     selectionEnd,
#     update_ddb,
#     res_text,
#     cursorPosition,
#     eventAccepted,
# ):
#     pre_content = "<body>" + pre_content + "</body>"
#     section = f_textSection(text=pre_content)
#     ts = TextSectionEditor(
#         section.id,
#         content,
#         pos=pos,
#         selectionStart=selectionStart,
#         selectionEnd=selectionEnd,
#     )
#     with patch.object(ts, "_update_ddb"):
#         response = ts.onChange()
#         # breakpoint()
#         # assert ts._update_ddb.assert_called()
#     # response = ts.onChange()
#     assert response == {
#         "text": res_text,
#         "cursorPosition": cursorPosition,
#         "eventAccepted": eventAccepted,
#     }


# class TestProperties:


#     def test_re_autoparagraph(self):
#         r = RE_AUTOPARAGRAPH
#         assert r.match("# zef")
#         assert r.match("###### zef")
#         assert not r.match(" # zef")
#         assert not r.match("####### zef")
#         assert not r.match("## zef ")
#         assert not r.match("##  zef")
#
#     def test_document(self, reset_db, qtbot):
#         doc = DocumentEditor()
#         o = QObject()
#         d = QTextDocument(parent=o)
#         with qtbot.waitSignal(doc.documentChanged):
#             doc.document = o
#         assert doc._document == doc.document == d
#
#     # def test_sectionId(self, reset_db, doc, check_simple_property):
#     #     assert doc.sectionId == 0
#     #     f_textSection()
#     #     check_simple_property("sectionId", 1)
#
#     def test_update_proxy_triggered_on_section_id_changed(self, doc, reset_db):
#         a = f_textSection()
#         doc.sectionId = 1
#         assert doc.document.toPlainText() == a.text
#
#     def test_selectionStart(self, doc, qtbot):
#         with qtbot.assertNotEmitted(doc.selectionStartChanged):
#             doc.selectionStart = 5
#         assert doc._cursor.position() == doc.selectionStart
#
#     def test_selectionEnd(self, doc, qtbot):
#         doc._cursor.insertText("un deux trois quatre cinq")
#         doc.selectionStart = 3
#         with qtbot.assertNotEmitted(doc.selectionEndChanged):
#             doc.selectionEnd = 7
#         assert doc._cursor.selectionEnd() == doc.selectionEnd
#         assert doc._cursor.selectedText() == "deux"
#
#     def test_paragraphAutoFormat_return_false_cases(self, doc):
#         doc._cursor.insertText("un deux trois quatre cinq")
#
#         # test middle line
#         doc._cursor.setPosition(5)
#         assert not doc.paragraphAutoFormat()
#
#         # test re not matched
#         doc._cursor.movePosition(QTextCursor.EndOfBlock)
#         assert not doc.paragraphAutoFormat()
#
#         # test level > 6
#         doc._cursor.insertText("####### blabla")
#         assert not doc.paragraphAutoFormat()
#
#     def test_paragraphAuto_ok_fin_de_docement(self, doc: DocumentEditor):
#         doc.document.setHtml("# blabla")
#         assert doc.paragraphAutoFormat()
#         html = doc.bs4()
#         assert len(html.body) == 2
#         bloc = doc.document.begin()
#         assert bloc.blockFormat() == BlockFormats[1]
#         assert html.body.h1.text == "blabla"
#         assert "font-weight:696" in html.body.h1.span["style"]  # check charformat
#         assert "-qt-paragraph-type:empty" in html.body.p["style"]
#
#     def test_paragraphAuto_ok_avec_text_avant(self, doc: DocumentEditor):
#         doc.document.setHtml("<h2>blabla</h2><p># hello</p>")
#         doc._cursor = QTextCursor(doc.document.begin().next())
#         doc._cursor.movePosition(QTextCursor.EndOfBlock)
#         assert doc._cursor.atBlockEnd()
#         assert doc.paragraphAutoFormat()
#         html = doc.bs4()
#         bloc = doc.document.begin()
#         assert bloc.text() == "blabla"
#         assert doc.document.blockCount() == 3
#         assert bloc.blockFormat().headingLevel() == 2
#
#         bloc = bloc.next()
#         assert bloc.blockFormat() == BlockFormats[1]
#         assert bloc.text() == "hello"
#
#         assert "font-weight:696" in html.body.h1.span["style"]  # check charformat
#         assert "-qt-paragraph-type:empty" in html.body.p["style"]
#
#     def test_paragraphAuto_ok_milieu_de_doc(self, doc: DocumentEditor):
#         doc.document.setHtml("<p># blabla</p><p>hello</p>")
#         doc._cursor = QTextCursor(doc.document.begin())
#         doc._cursor.movePosition(QTextCursor.EndOfBlock)
#         assert doc.paragraphAutoFormat()
#         html = doc.bs4()
#         assert len(html.body) == 2
#         bloc = doc.document.begin()
#         assert bloc.blockFormat() == BlockFormats[1]
#         assert "font-weight:696" in html.body.h1.span["style"]  # check charformat
#         assert "hello" == html.body.p.text
#
#     @pytest.mark.skip("broken")
#     @pytest.mark.parametrize(
#         "start,end, param, value, res",
#         [
#             (4, 4, "fgColor", QColor("red"), "color:#ff0000"),  # no selection color
#             (3, 7, "fgColor", QColor("blue"), "color:#0000ff"),  # selection color
#             (
#                 3,
#                 7,
#                 "underline",
#                 True,
#                 ["color:#0000ff", "text-decoration: underline"],  # selection underlien
#             ),
#             (
#                 4,
#                 4,
#                 "underline",
#                 QColor("blue"),
#                 [
#                     "color:#0000ff",
#                     "text-decoration: underline",
#                 ],  # no selection underline
#             ),
#             (4, 4, "nothing", "red", None),  # Bad type
#             (4, 4, "fgColor", "rouge", None),  # bad value
#         ],
#     )
#     def test_setStyle_color(
#         self, doc: DocumentEditor, qtbot, start, end, param, value, res, signal=True
#     ):
#         doc.document.setHtml("<p>un deux trois</p>")
#         backup = doc.document.toHtml()
#
#         doc.selectionStart = start
#         doc.selectionEnd = end
#
#         with qtbot.waitSignal(doc.selectionCleared):
#             doc.setStyleFromMenu({"style": {param: value}})
#
#         html = doc.bs4().p.span
#         if res is not None:
#             assert html.text == "deux"
#             res = [res] if isinstance(res, str) else res
#             print(res)
#             print(doc.bs4())
#             print([x in html["style"] for x in res])
#             assert all(x in html["style"] for x in res)
#         else:
#             assert backup == doc.document.toHtml()
#
#     def test_update_proxy(self, doc, ddbr):
#         # bad id
#         doc.sectionId = 99999
#         assert doc._proxy is None
#
#         # good id
#         a = f_textSection()
#         doc._update_block_format = MagicMock()
#         doc.sectionId = 1
#
#         # test set_html and format block called
#         assert doc.bs4().p.text == a.text
#         doc._update_block_format.assert_called_with()
#
#         # test proxy set
#         assert isinstance(doc._proxy, EntityProxy)
#         with db_session:
#             assert doc._proxy.id == a.id
#
#     def test_update_proxy_do_not_change_modified(self, doc, reset_db):
#
#         a = f_textSection(text=f"<html><body>bla</body></html>")
#         # updaté si pas html
#         doc._updateProxy(a.id)
#         with db_session:
#             assert a.modified == doc._proxy.modified
#
#     def test_update_block_format(self, doc):
#         doc.document.setHtml("<p>bla</p><h1>titre</h1>")
#         doc._update_block_format()
#
#         bloc = doc.document.begin()
#         for x in ["p", 1]:
#             assert bloc.blockFormat() == BlockFormats[x]
#             bloc = bloc.next()
#
#     def test_onDocumentContentChanged(self, ddbr, doc, qtbot):
#         a = f_textSection()
#         doc.sectionId = a.id
#         with qtbot.waitSignal(doc.dao.updateRecentsAndActivites):
#             doc.document.setHtml("<p>bla</p><h1>titre</h1>")
#         with db_session:
#             x = ddbr.TextSection[a.id]
#             assert x.text == doc._proxy.text
#             assert x.text == doc.document.toHtml()
