import QtQuick 2.15
import "qrc:/qml/divers"

Item {
    property var stacked

    Component {
        id: stackedcomp

        QtObject {
            id: objid

            property string titre: "abcdef"
            property var undoStack
        }

    }

    Component {
        id: undocomp

        UndoAbleTextArea {
            id: undotextid

            property QtObject controler

            function setText() {
                undostack.pushText(controler, "titre", text);
            }

            font.pointSize: 16
            txtfield: controler && controler.titre ? controler.titre : ""
        }

    }

    CasTest {
        id: item

        function initPost() {
            stacked = createTemporaryObject(stackedcomp, item);
            stacked.undoStack = th.getUndoStack(item);
            tested = createTemporaryObject(undocomp, item, {
                "controler": stacked,
                "undostack": stacked.undoStack
            });
            tested.forceActiveFocus();
            tested.cursorPosition = 2;
        }

        function test_stack() {
            let st = th.getUndoStack(item);
            st.pushText(stacked, "titre", "bla");
            compare(stacked.titre, "bla");
            st.undo();
            compare(stacked.titre, "abcdef");
            st.redo();
            compare(stacked.titre, "bla");
        }

        function test_default_property() {
            verify(tested.selectByMouse);
        }

        function test_init() {
            tested.undoDelay = 0;
            compare(tested.text, "abcdef");
            compare(stacked.titre, "abcdef");
            keyClick(Qt.Key_X);
            tryCompare(tested, "text", "abxcdef");
            compare(stacked.titre, "abxcdef");
        }

        function test_undo_redo_basic() {
            tested.undoDelay = 300;
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            keyClick(Qt.Key_Z);
            tryCompare(tested, "text", "abxyzcdef");
            tryCompare(tested, "txtfield", "abxyzcdef");
            compare(tested.cursorPosition, 5);
            keySequence("ctrl+z");
            tryCompare(tested, "txtfield", "abcdef");
            tryCompare(tested, "text", "abcdef");
            compare(tested.cursorPosition, 2);
            keySequence("ctrl+shift+z");
            tryCompare(tested, "text", "abxyzcdef");
            compare(tested.cursorPosition, 5);
        }

        function test_undo_redo_basic_sequentiel() {
            tested.undoDelay = 0;
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            keyClick(Qt.Key_Z);
            tryCompare(tested, "cursorPosition", 5);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 4);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 3);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 2);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 3);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 4);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 5);
        }

        function test_debut_ligne() {
            tested.cursorPosition = 0;
            tested.undoDelay = 0;
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            compare(tested.cursorPosition, 2);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 1);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 0);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 1);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 2);
        }

        function test_fin_ligne() {
            tested.undoDelay = 0;
            tested.cursorPosition = tested.text.length - 1;
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            compare(tested.cursorPosition, 7);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 6);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 5);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 6);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 7);
        }

        function test_undo_with_backspace() {
            tested.undoDelay = 0;
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            keyClick(Qt.Key_Backspace);
            keyClick(Qt.Key_Z);
            compare(tested.cursorPosition, 4);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 3);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 4);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 3);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 2);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 3);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 4);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 3);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 4);
        }

        function test_big_erase() {
            tested.undoDelay = 0;
            tested.select(2, 5);
            keyClick(Qt.Key_Backspace);
            compare(tested.cursorPosition, 2);
            keySequence("ctrl+z");
            compare(tested.selectionStart, 2);
            compare(tested.selectionEnd, 5);
            keySequence("ctrl+shift+z");
            compare(tested.selectionStart, 2);
            compare(tested.selectionEnd, 2);
        }

        function test_undo_redo_invalidate_stack_after_modif_when_undo() {
            tested.undoDelay = 0;
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            keyClick(Qt.Key_Z);
            compare(tested.cursorPosition, 5);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 4);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 3);
            keyClick(Qt.Key_J);
            compare(tested.text, "abxjcdef");
            keySequence("ctrl+shift+z");
            compare(tested.text, "abxjcdef");
            keySequence("ctrl+z");
            compare(tested.text, "abxcdef");
            compare(tested.cursorPosition, 3);
        }

        function test_undo_groups_space() {
            tested.undoDelay = 100; // ne pas faire un interval trop court
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            keyClick(Qt.Key_Space);
            keyClick(Qt.Key_X);
            tryCompare(tested, "text", "abxy xcdef");
            tryCompare(tested, "txtfield", "abxy xcdef");
            keySequence("ctrl+z");
            tryCompare(tested, "text", "abxy cdef");
            keySequence("ctrl+z");
            tryCompare(tested, "text", "abxycdef");
            keySequence("ctrl+z");
            tryCompare(tested, "text", "abcdef");
            keySequence("ctrl+shift+z");
            tryCompare(tested, "text", "abxycdef");
            keySequence("ctrl+shift+z");
            tryCompare(tested, "text", "abxy cdef");
            keySequence("ctrl+shift+z");
            tryCompare(tested, "text", "abxy xcdef");
        }

        function test_focus_after_undo_redo() {
            // on utilise les command pour simuler une intervention extérieur
            tested.undoDelay = 0;
            keyClick(Qt.Key_X);
            let autre = createTemporaryQmlObject("import QtQuick 2.0\nRectangle {}", item);
            autre.forceActiveFocus();
            verify(!tested.activeFocus);
            stacked.undoStack.undo();
            verify(tested.activeFocus);
            autre.forceActiveFocus();
            stacked.undoStack.redo();
            verify(tested.activeFocus);
        }

        width: 200
        height: 200
        name: "UndoTextArea"
        testedNom: "qrc:/qml/divers/UndoAbleTextArea.qml"
        autocreate: false
    }

}
