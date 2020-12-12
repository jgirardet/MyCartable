import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 200

    CasTest {
        property var eq
        property var eqObj

        function initPre() {
            eq = fk.f("equationSection", {
                "content": "1     \n__ + 1\n15    ",
                "curseur": 10
            });
            eqObj = th.getBridgeInstance(item, "EquationSection", eq.id);
            params = {
                "section": eqObj,
                "sectionItem": item
            };
        }

        function initPost() {
        }

        function test_init() {
            tryCompare(tested, "text", "1     \n__ + 1\n15    ");
            tryCompare(tested, "cursorPosition", 10);
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

        name: "EquationSection"
        testedNom: "qrc:/qml/sections/EquationSection.qml"
        params: {
            "sectionItem": item
        }
    }

}
