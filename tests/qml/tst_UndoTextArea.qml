import QtQuick 2.15
import "qrc:/qml/divers"

Item {
    id: item

    width: 200
    height: 200

    QtObject {
        id: stacked

        property string text
        property var _undotext
        property var _popedtext

        function undo() {
            _popedtext.push(text);
            text = _undotext.pop();
            print("le text dans undo", text);
        }

        function redo() {
            stacked._undotext.push(text);
            text = _popedtext.pop();
            print("le text dans redo", text);
        }

        function reset() {
            _undotext = [];
            _popedtext = [];
            text = "abcdef";
        }

        Component.onCompleted: reset()
    }

    Component {
        id: undocomp

        UndoTextArea {
            id: undotextid

            function setText() {
                stacked._undotext.push(stacked.text);
                stacked.text = text;
            }

            connectedStack: stacked
            bindedText: stacked.text
        }

    }

    CasTest {
        function initPre() {
            print("debut init pre");
            stacked.reset();
        }

        function initPost() {
            tested = createTemporaryObject(undocomp, item, {
            });
            tested.forceActiveFocus();
            tested.cursorPosition = 2;
            print("fin init post", tested._stack);
        }

        function test_init() {
            compare(tested.text, "abcdef");
            compare(stacked.text, "abcdef");
            keyClick(Qt.Key_X);
            tryCompare(tested,"text", "abxcdef");
            tryCompare(stacked,"text", "abxcdef");
            compare(stacked._undotext, ['abcdef']);
        }

        function test_undo_redo_basic() {
            tested.undoDelay=1
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            keyClick(Qt.Key_Z);
            tryCompare(tested,"text", "abxyzcdef")
            print(JSON.stringify(stacked._undotext))
            compare(tested.cursorPosition, 5);
            keySequence("ctrl+z");
            tryCompare(tested,"text", "abcdef")
            compare(tested.cursorPosition, 2);
            keySequence("ctrl+shift+z");
            tryCompare(tested,"text", "abxyzcdef")
            compare(tested.cursorPosition, 5);
        }
        function test_undo_redo_basic_sequentiel() {
            tested.undoDelay=0
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            keyClick(Qt.Key_Z);
            compare(tested.cursorPosition, 5);
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
            tested.undoDelay=0
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
            tested.undoDelay=0
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
            tested.undoDelay=0
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

        function test_external_data() {
            return [{
                "tag": "paste_is_longer_than_selected",
                "copyStart": 0,
                "copyEnd": 6,
                "redoPos": 8,
                "selectStart": 2,
                "selectEnd": 5,
                "sequence": "ctrl+v"
            }, {
                "tag": "paste_is_shorter_than_selected",
                "copyStart": 0,
                "copyEnd": 2,
                "redoPos": 4,
                "selectStart": 2,
                "selectEnd": 5,
                "sequence": "ctrl+v"
            }, {
                "tag": "paste_no_select",
                "copyStart": 0,
                "copyEnd": 3,
                "redoPos": 5,
                "selectStart": 2,
                "selectEnd": 2,
                "sequence": "ctrl+v"
            }, {
                "tag": "cut",
                "copyStart": 0,
                "copyEnd": 0,
                "redoPos": 2,
                "selectStart": 2,
                "selectEnd": 5,
                "sequence": "ctrl+x"
            }];
        }

        function test_external(data) {
            tested.select(data.copyStart, data.copyEnd);
            tested.copy();
            tested.select(data.selectStart, data.selectEnd);
            keySequence(data.sequence);
            compare(tested.selectionStart, data.redoPos);
            compare(tested.selectionEnd, data.redoPos);
            compare(tested.length, 6 + data.copyEnd - data.copyStart - data.selectEnd + data.selectStart);
            keySequence("ctrl+z");
            compare(tested.selectionStart, data.selectStart);
            compare(tested.selectionEnd, data.selectEnd);
            keySequence("ctrl+shift+z");
            compare(tested.selectionStart, data.redoPos);
            compare(tested.selectionEnd, data.redoPos);
        }

        function test_undo_redo_invalidate_stack_after_modif_when_undo() {
            tested.undoDelay=0
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            keyClick(Qt.Key_Z);
            compare(tested.cursorPosition, 5);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 4);
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 3);
            keyClick(Qt.Key_J);
            compare(tested.text, "abxjcdef")
            keySequence("ctrl+shift+z");
            compare(tested.text, "abxjcdef")
            keySequence("ctrl+z");
            compare(tested.text, "abxcdef")
            compare(tested.cursorPosition, 3);
      }

      function test_undo_groups() {
            tested.undoDelay=1
            keyClick(Qt.Key_X);
            keyClick(Qt.Key_Y);
            keyClick(Qt.Key_Space);
            keyClick(Qt.Key_X);
            tryCompare(stacked._undotext,"length", 3)
            compare(tested._stack.length, 3)
            compare(tested.text, "abxy xcdef")
            keySequence("ctrl+z");
            tryCompare(tested, "text", "abxy cdef")
            compare(tested.cursorPosition,5)
            keySequence("ctrl+z");
            tryCompare(tested, "text", "abxycdef")
            compare(tested.cursorPosition,4)
            keySequence("ctrl+z");
            tryCompare(tested, "text", "abcdef")
            compare(tested.cursorPosition,2)
      }
      function test_rien() {
        wait(20000)
      }

        name: "UndoTextArea"
        testedNom: "qrc:/qml/divers/UndoTextArea.qml"
        autocreate: false
    }

}
