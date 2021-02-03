import MyCartable 1.0
import QtQuick 2.15

Item {
    id: item

    width: 200
    height: 200

    Classeur {
        id: classeur_id
    }

    CasTest {
        property var sec
        property var pageObj
        property QtObject secObj

        function initPre() {
            sec = fk.f("textSection", {
                "text": "x"
            });
            pageObj = th.getBridgeInstance(classeur_id, "Page", sec.page);
            secObj = pageObj.getSection(0);
            params = {
                "section": secObj,
                "sectionItem": item
            };
        }

        function initPost() {
            tested.forceActiveFocus();
            tested.cursorPosition = 1;
        }

        function test_init() {
            compare(sec.id, secObj.id);
            compare(tested.section, secObj);
            verify(!tested.doNotUpdate);
            compare(tested.getText(0, 1), "x");
        }

        function test_standard_keypress() {
            keyClick(Qt.Key_A);
            compare(tested.getText(0, 2), "xa");
            keyClick(Qt.Key_B);
            compare(tested.getText(0, 3), "xab");
        }

        function test_undo_redo() {
            keyClick(Qt.Key_A);
            compare(tested.getText(0, 2), "xa");
            keySequence("ctrl+z");
            compare(tested.getText(0, 2), "x");
            keySequence("ctrl+shift+z");
            compare(tested.getText(0, 2), "xa");
        }

        function test_auto_format() {
            keyClick(Qt.Key_A);
            keyClick(Qt.Key_Space);
            keySequence("#, return");
            verify(tested.text.includes("color:#363636")); //couleur rouge == format ok
        }

        function test_format_via_menu() {
            let rec = tested.positionToRectangle(0);
            print(JSON.stringify(rec));
            mouseClick(tested, rec.x, rec.y + 5, Qt.RightButton);
            mouseClick(tested.menu.contentItem, 10, 10, Qt.LeftButton, Qt.NoModifier, 100);
            verify(tested.text.includes("color:#d40020")); //couleur rouge == format ok
        }

        name: "TextSection"
        testedNom: "qrc:/qml/sections/TextSection.qml"
    }

}
