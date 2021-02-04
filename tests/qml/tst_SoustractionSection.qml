import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/js/lodash.js" as Lodash

Item {
    id: item

    width: 600
    height: 600

    CasTest {
        property var secDB
        property var sec
        property var page

        function initPre() {
            secDB = fk.f("soustractionSection", {
                "string": "432,54-91,41"
            });
            page = th.getBridgeInstance(item, "Page", secDB.page);
            sec = page.getSection(0);
            params = {
                "section": sec,
                "sectionItem": item
            };
        }

        function test_the_mock_model() {
            compare(tested.count, 51);
            compare(tested.model, sec.model);
        }

        function test_focus_is_highlighted() {
            var it = tested.itemAtIndex(1).textinput;
            it.focus = true;
            compare(Qt.colorEqual(it.background.color, "yellow"), true);
        }

        function test_edit() {
            mouseClick(tested.itemAtIndex(36).textinput);
            keyClick(Qt.Key_5);
            compare(sec.datas[36], "5");
        }

        function test_properties() {
            //retenu droite{20, 23, 26, 30}
            compare(tested.itemAtIndex(0).textinput.leftPadding, 5);
            compare(tested.itemAtIndex(20).textinput.leftPadding, 0);
            // "Gauche", {4, 7, 11, 14}
            compare(tested.itemAtIndex(0).textinput.rightPadding, 5);
            compare(tested.itemAtIndex(4).textinput.rightPadding, 1);
            compare(tested.itemAtIndex(0).textinput.color, "#000000"); //black
            compare(tested.itemAtIndex(20).textinput.color, "#ff0000"); //Red
            compare(tested.itemAtIndex(4).textinput.color, "#ff0000"); //Red
            compare(tested.itemAtIndex(0).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(tested.itemAtIndex(20).textinput.horizontalAlignment, TextInput.AlignLeft);
            compare(tested.itemAtIndex(4).textinput.horizontalAlignment, TextInput.AlignRight);
            compare(tested.itemAtIndex(0).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(tested.itemAtIndex(20).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(tested.itemAtIndex(4).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(tested.itemAtIndex(0).textinput.readOnly, true);
            compare(tested.itemAtIndex(36).textinput.readOnly, false);
            compare(tested.itemAtIndex(42).textinput.readOnly, false);
            compare(tested.itemAtIndex(5).textinput.background.borderColor, "#ffffff"); // root color
            compare(tested.itemAtIndex(25).textinput.background.borderColor, "#ffffff");
            compare(tested.itemAtIndex(35).textinput.background.borderColor, "#000000"); //black
        }

        name: "SoustractionSection"
        testedNom: "qrc:/qml/sections/SoustractionSection.qml"
    }

}
