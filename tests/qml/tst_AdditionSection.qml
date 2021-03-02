// baseoperation testé ici car addition très simple

import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 200

    CasTest {
        property var secDB
        property var sec
        property var page

        function initPre() {
            secDB = fk.f("additionSection", {
                "string": "9+8"
            });
            page = th.getBridgeInstance(item, "Page", secDB.page);
            sec = page.getSection(0);
            params = {
                "section": sec,
                "sectionItem": item
            };
        }

        function initPost() {
        }

        function test_the_model() {
            compare(tested.model, sec.model);
            compare(tested.count, 12);
        }

        function test_init() {
            compare(tested.keyNavigationEnabled, false);
            compare(tested.width, 150);
            compare(tested.height, 200);
        }

        function test_cursor_binding() {
            sec.model.cursor = 11;
            compare(tested.currentIndex, 11);
        }

        function test_on_currentItemchanged() {
            tested.currentIndex = 1;
            tested.currentIndex = 6;
            compare(tested.currentItem.textinput.focus, true);
            //test no focus if input no exists, erreur dans les waringing du test
            tested.currentIndex = 999;
        }

        function test_keys_and_validator() {
            var elem = tested.itemAtIndex(11).textinput;
            mouseClick(elem);
            compare(sec.datas[11], "");
            //1 entier
            keyClick(Qt.Key_5);
            compare(sec.datas[11], "5");
            ///del et backspace
            mouseClick(elem);
            keyClick(Qt.Key_Backspace);
            compare(sec.datas[11], "");
            mouseClick(elem);
            keyClick(Qt.Key_5);
            compare(sec.datas[11], "5");
            mouseClick(elem);
            keyClick(Qt.Key_Delete);
            compare(sec.datas[11], "");
            // validator refuse alphabet
            mouseClick(elem);
            keyClick(Qt.Key_A);
            compare(sec.datas[11], "");
            //valiadator n'ademet qu'un chiffre
            mouseClick(elem);
            keyClick(Qt.Key_5);
            compare(sec.datas[11], "5");
            mouseClick(elem);
            keyClick(Qt.Key_5);
            compare(sec.datas[11], "5");
        }

        function test_move_with_arrows() {
            mouseClick(tested.itemAtIndex(11).textinput);
            keyClick(Qt.Key_Left);
            keyClick(Qt.Key_5);
            compare(sec.datas[10], "5");
            mouseClick(tested.itemAtIndex(10).textinput);
            keyClick(Qt.Key_Right);
            keyClick(Qt.Key_4);
            compare(sec.datas[11], "4");
            tested.destroy();
        }

        function test_focus_is_highlighted() {
            var it = tested.itemAtIndex(1).textinput;
            it.focus = true;
            compare(Qt.colorEqual(it.background.color, "yellow"), true);
        }

        function test_edit() {
            // test : automovenext, onfocuschanged
            mouseClick(tested.itemAtIndex(11).textinput);
            compare(tested.currentItem.textinput.focus, true); // si pas fait
            keyClick(Qt.Key_5);
            compare(sec.datas[11], "5");
        }

        function test_properties() {
            compare(tested.itemAtIndex(0).textinput.bottomPadding, 0);
            compare(tested.itemAtIndex(3).textinput.bottomPadding, 5);
            compare(tested.itemAtIndex(11).textinput.bottomPadding, 5);
            compare(tested.itemAtIndex(0).textinput.topPadding, 5);
            compare(tested.itemAtIndex(3).textinput.topPadding, 0);
            compare(tested.itemAtIndex(11).textinput.topPadding, 5);
            compare(tested.itemAtIndex(0).textinput.color, "#ff0000"); //Red
            compare(tested.itemAtIndex(3).textinput.color, "#000000"); //black
            compare(tested.itemAtIndex(11).textinput.color, "#000000");
            compare(tested.itemAtIndex(0).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(tested.itemAtIndex(3).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(tested.itemAtIndex(11).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(tested.itemAtIndex(0).textinput.verticalAlignment, TextInput.AlignBottom);
            compare(tested.itemAtIndex(3).textinput.verticalAlignment, TextInput.AlignTop);
            compare(tested.itemAtIndex(11).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(tested.itemAtIndex(0).textinput.readOnly, true);
            compare(tested.itemAtIndex(3).textinput.readOnly, true);
            compare(tested.itemAtIndex(11).textinput.readOnly, false);
            compare(tested.itemAtIndex(0).textinput.background.borderColor, "#ffffff"); // root color
            compare(tested.itemAtIndex(3).textinput.background.borderColor, "#ffffff");
            compare(tested.itemAtIndex(11).textinput.background.borderColor, "#000000"); //black
        }

        name: "AdditionSection"
        testedNom: "qrc:/qml/sections/AdditionSection.qml"
    }

}
