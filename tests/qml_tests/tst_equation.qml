import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 200

    CasTest {
        function initPre() {
        }

        function initPreCreate() {
        }

        function initPost() {
            ddb._loadSection = {
                "id": "sectionId",
                "created": "2019-09-22T19:21:57.521813",
                "modified": "2019-09-22T19:21:57.521813",
                "page": "pageId",
                "position": 1,
                "classtype": "EquationSection",
                "content": "1     \n__ + 1\n15    ",
                "curseur": 10
            };
            tested.sectionId = "sectionId";
        }

        function test_init() {
            // test on section id changed
            tryCompare(tested, "text", "1     \n__ + 1\n15    ");
            tryCompare(tested, "cursorPosition", 10);
        }

        function test_keypress() {
            ddb._updateEquation = {
                "content": "1      \n__5 + 1\n15     ",
                "curseur": 12
            };
            mouseClick(tested);
            verify(tested.focus);
            tested.cursorPosition = 10;
            tryCompare(tested, "cursorPosition", 10);
            keyClick(Qt.Key_5);
            tryCompare(tested, "cursorPosition", 12);
            tryCompare(tested, "text", "1      \n__5 + 1\n15     ");
            compare(ddb._updateEquationParams[0], "sectionId");
            compare(ddb._updateEquationParams[1], "1     \n__ + 1\n15    ");
            compare(ddb._updateEquationParams[2], 10);
            compare(ddb._updateEquationParams[3], "{\"objectName\":\"\",\"key\":53,\"text\":\"5\",\"modifiers\":0,\"isAutoRepeat\":false,\"count\":65535,\"nativeScanCode\":0,\"accepted\":false}");
        }

        function test_isfocusable() {
            tested.cursorPosition = 9;
            ddb._isEquationFocusable = false;
            mouseClick(tested, 23, 53);
            compare(tested.cursorPosition, 9);
            ddb._isEquationFocusable = true;
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
