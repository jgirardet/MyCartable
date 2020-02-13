from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import QObject
from PySide2.QtGui import QTextDocument, QTextCursor
from fixtures import is_blockFormat
from package.database.factory import f_textSection
from package.page.blockFormat import BlockFormats
from package.page.charFormat import CharFormats
from package.page.text_section import DocumentEditor, RE_AUTOPARAGRAPH
from bs4 import BeautifulSoup
from pony.orm.core import EntityProxy, db_session


@pytest.fixture()
def doc() -> DocumentEditor:
    doc = DocumentEditor()
    doc._document = QTextDocument()
    doc._init()
    doc.bs4 = lambda: BeautifulSoup(
        doc.document.toHtml().replace("\n", ""), "html.parser"
    )
    return doc


class TestProperties:
    def test_re_autoparagraph(self):
        r = RE_AUTOPARAGRAPH
        assert r.match("# zef")
        assert r.match("###### zef")
        assert not r.match(" # zef")
        assert not r.match("####### zef")
        assert not r.match("## zef ")
        assert not r.match("##  zef")

    def test_document(self, reset_db, qtbot):
        doc = DocumentEditor()
        o = QObject()
        d = QTextDocument(parent=o)
        with qtbot.waitSignal(doc.documentChanged):
            doc.document = o
        assert doc._document == doc.document == d

    def test_sectionId(self, reset_db, doc, check_simple_property):
        assert doc.sectionId == 0
        f_textSection()
        check_simple_property("sectionId", 1)

    def test_update_proxy_triggered_on_section_id_changed(self, doc, reset_db):
        a = f_textSection()
        doc.sectionId = 1
        assert doc.document.toPlainText() == a.text

    def test_selectionStart(self, doc, qtbot):
        with qtbot.assertNotEmitted(doc.selectionStartChanged):
            doc.selectionStart = 5
        assert doc._cursor.position() == doc.selectionStart

    def test_selectionEnd(self, doc, qtbot):
        doc._cursor.insertText("un deux trois quatre cinq")
        doc.selectionStart = 3
        with qtbot.assertNotEmitted(doc.selectionEndChanged):
            doc.selectionEnd = 7
        assert doc._cursor.selectionEnd() == doc.selectionEnd
        assert doc._cursor.selectedText() == "deux"

    def test_paragraphAutoFormat_return_false_cases(self, doc):
        doc._cursor.insertText("un deux trois quatre cinq")

        # test middle line
        doc._cursor.setPosition(5)
        assert not doc.paragraphAutoFormat()

        # test re not matched
        doc._cursor.movePosition(QTextCursor.EndOfBlock)
        assert not doc.paragraphAutoFormat()

        # test level > 6
        doc._cursor.insertText("####### blabla")
        assert not doc.paragraphAutoFormat()

    def test_paragraphAuto_ok_fin_de_docement(self, doc: DocumentEditor):
        doc.document.setHtml("# blabla")
        assert doc.paragraphAutoFormat()
        html = doc.bs4()
        assert len(html.body) == 2
        bloc = doc.document.begin()
        assert bloc.blockFormat() == BlockFormats[1]
        assert "font-weight:696" in html.body.h1.span["style"]  # check charformat
        assert "-qt-paragraph-type:empty" in html.body.p["style"]

    def test_paragraphAuto_ok_milieu_de_doc(self, doc: DocumentEditor):
        doc.document.setHtml("<p># blabla</p><p>hello</p>")
        doc._cursor = QTextCursor(doc.document.begin())
        doc._cursor.movePosition(QTextCursor.EndOfBlock)
        assert doc.paragraphAutoFormat()
        html = doc.bs4()
        print(html)
        assert len(html.body) == 2
        bloc = doc.document.begin()
        assert bloc.blockFormat() == BlockFormats[1]
        assert "font-weight:696" in html.body.h1.span["style"]  # check charformat
        assert "hello" == html.body.p.text

    @pytest.mark.parametrize(
        "start,end, type_, value, res",
        [
            (4, 4, "color", "red", "color:#ff0000"),  # no selection color
            (3, 7, "color", "blue", "color:#0000ff"),  # selection color
            (
                3,
                7,
                "underline",
                "blue",
                ["color:#0000ff", "text-decoration: underline"],  # selection underlien
            ),
            (
                4,
                4,
                "underline",
                "blue",
                [
                    "color:#0000ff",
                    "text-decoration: underline",
                ],  # no selection underline
            ),
            (4, 4, "nothing", "red", None),  # Bad type
            (4, 4, "color", "rouge", None),  # bad value
        ],
    )
    def test_setStyle_color(
        self, doc: DocumentEditor, qtbot, start, end, type_, value, res, signal=True
    ):
        doc.document.setHtml("<p>un deux trois</p>")
        backup = doc.document.toHtml()

        doc.selectionStart = start
        doc.selectionEnd = end

        with qtbot.waitSignal(doc.selectionCleared):
            doc.setStyle({"type": type_, "value": value})

        html = doc.bs4().p.span
        if res is not None:
            assert html.text == "deux"
            res = [res] if isinstance(res, str) else res
            assert all(x in html["style"] for x in res)
        else:
            assert backup == doc.document.toHtml()

    def test_update_proxy(self, doc, reset_db):
        # bad id
        doc.sectionId = 99999
        assert doc._proxy is None

        # good id
        a = f_textSection()
        doc._update_block_format = MagicMock()
        doc.sectionId = 1

        # test set_html and format block called
        assert doc.bs4().p.text == a.text
        doc._update_block_format.assert_called_with()

        # test proxy set
        assert isinstance(doc._proxy, EntityProxy)
        with db_session:
            assert doc._proxy.id == a.id

    def test_update_block_format(self, doc):
        doc.document.setHtml("<p>bla</p><h1>titre</h1>")
        doc._update_block_format()

        bloc = doc.document.begin()
        for x in ["p", 1]:
            assert bloc.blockFormat() == BlockFormats[x]
            bloc = bloc.next()
