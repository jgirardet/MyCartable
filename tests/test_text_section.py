from PySide2.QtGui import QTextDocument

#
# class TestProperties:
#     def test_document(self, reset_db, qtbot):
#         doc = DocumentEditor()
#         o = QObject()
#         d = QTextDocument(parent=o)
#         with qtbot.waitSignal(doc.documentChanged):
#             doc.document = o
#         assert doc._document == doc.document == d
#
#     def test_sectionId(self, reset_db, check_simple_property):
#         f_textSection()
#         check_simple_property("sectionId", 1)
#
#     def test_position(self, check_simple_property):
#         check_simple_property("position", 1)
#
#     def test_selectionStart(self, check_simple_property):
#         check_simple_property("selectionStart", None)
#
#     def test_selectionEnd(self, check_simple_property):
#         check_simple_property("selectionEnd", None)
#
#
# class TestSignal:
#     def test_sectionIdChanged(self, doc: DocumentEditor, qtbot, reset_db):
#         f_textSection(text="<html><body>bla</body></html")
#
#         # on part du principe que le set vaut le signal
#         # c plus pratique comme ça.
#         # mais ne rien mettre d'autre dans sectionId.setter
#         doc.sectionId = 1
#         assert doc._sectionId == 1
#         with db_session:
#             assert doc._proxy.id == 1
#         assert doc._document.toPlainText() == "bla"
#
#         # item missing in db
#         doc.sectionId = 2
#         assert doc._sectionId == doc.sectionId == 2
#         with db_session:
#             assert doc._proxy == None

entete = """<!DOCTYPE
HTML
PUBLIC
"-//W3C//DTD
HTML
4.0//EN"
"http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta
name="qrichtext"
content="1"
/><style
type="text/css">
p,
li
{
white-space:
pre-wrap;
}
</style></head><body
style="
font-family:'';
font-weight:400;
font-style:normal;"""

RE_HEADER = "^#+\s.+"


class TestBloc:
    def test_headerify(self):
        q = QTextDocument()
        q.setHtml("<p>aaa</p><h1># bbb</h1>")

        bloc = q.begin()
        while bloc.isValid():
            print(bloc.text())
            # while bloc != self.q.end():
            # m = re.match(RE_HEADER, bloc.text())
            for it in bloc.begin():
                a = it.fragment()
                print(a.text())
            bloc = bloc.next()

        assert q.toHtml()[:] == "bla"
