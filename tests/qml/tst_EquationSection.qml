import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 200

    Classeur {
        id: classeur_id
    }

    CasTest {
        property var eq
        property var eqObj
        property var pageObj
        property string init_content: "1     \n__ + 1\n15    "

        function initPre() {
            eq = fk.f("equationSection", {
                "content": init_content,
                "curseur": 10
            });
            pageObj = th.getBridgeInstance(classeur_id, "Page", eq.page);
            eqObj = pageObj.getSection(0);
            params = {
                "section": eqObj,
                "sectionItem": item
            };
        }

        function initPost() {
        }

        function test_init() {
            mouseClick(tested);
            tryCompare(tested, "text", init_content);
            tryCompare(tested, "cursorPosition", 13);
        }

        function test_keypress() {
            mouseClick(tested);
            verify(tested.focus);
            tested.cursorPosition = 9;
            compare(tested.cursorPosition, 9);
            keyClick(Qt.Key_5);
            tryCompare(tested, "cursorPosition", 11);
            tryCompare(tested, "text", "1      \n__5 + 1\n15     ");
        }

        function test_isfocusable() {
            tested.cursorPosition = 10;
            mouseClick(tested, tested.width - 5, tested.height - 5);
            compare(tested.cursorPosition, 10);
            mouseClick(tested, 23, 53);
            compare(tested.cursorPosition, 15);
        }

        function test_undo_redo() {
            mouseClick(tested);
            keyClick(Qt.Key_A);
            compare(tested.cursorPosition, 15);
            compare(tested.text, "1      \n__ + 1a\n15     ");
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 13);
            compare(tested.text, init_content);
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 15);
            compare(tested.text, "1      \n__ + 1a\n15     ");
        }

        function test_bug_131() {
            eqObj.content = ""
            mouseClick(tested)
            keyClick(Qt.Key_Backspace)
        }

        name: "EquationSection"
        testedNom: "qrc:/qml/sections/EquationSection.qml"
        params: {
            "sectionItem": item
        }
    }

}
