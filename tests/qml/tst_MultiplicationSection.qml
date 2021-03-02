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
            secDB = fk.f("multiplicationSection", {
                "string": "251*148"
            });
            page = th.getBridgeInstance(item, "Page", secDB.page);
            sec = page.getSection(0);
            params = {
                "section": sec,
                "sectionItem": item
            };
        }

        function test_the_mock_model() {
            compare(tested.count, 60);
            compare(tested.model, sec.model);
        }

        function test_focus_is_highlighted() {
            var it = tested.itemAtIndex(1).textinput;
            it.focus = true;
            compare(Qt.colorEqual(it.background.color, "yellow"), true);
        }

        function test_font_change_for_parent_highlighted_num() {
            var it = tested.itemAtIndex(22).textinput;
            compare(it.font.underline, false);
            compare(it.font.weight, Font.Normal);
            it = tested.itemAtIndex(23).textinput;
            compare(it.font.underline, true);
            compare(it.font.weight, Font.Black);
        }

        function test_edit() {
            mouseClick(tested.itemAtIndex(52).textinput);
            compare(tested.currentItem.textinput.focus, true); // si pas fait)
            keyClick(Qt.Key_5);
            compare(sec.datas[52], "5");
            //            model.get(52).display = "5"; //manually update display
            compare(tested.currentItem.textinput.focus, true);
            // si pas fait)
            mouseClick(tested.itemAtIndex(52).textinput);
            keyClick(Qt.Key_Comma);
            compare(sec.datas[52], "5,");
        }

        function test_properties() {
            compare(tested.itemAtIndex(4).textinput.color, "#ff0000"); //Red
            fuzzyCompare(tested.itemAtIndex(20).textinput.color, "blue", 0);
            fuzzyCompare(tested.itemAtIndex(26).textinput.color, "green", 0);
            compare(tested.itemAtIndex(52).textinput.color, "#ff0000"); //Red
            compare(tested.itemAtIndex(56).textinput.color, "#000000"); //black
            compare(tested.itemAtIndex(4).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(tested.itemAtIndex(20).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(tested.itemAtIndex(52).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(tested.itemAtIndex(56).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(tested.itemAtIndex(4).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(tested.itemAtIndex(20).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(tested.itemAtIndex(52).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(tested.itemAtIndex(56).textinput.verticalAlignment, TextInput.AlignVCenter);
        }

        name: "MultiplicationSection"
        testedNom: "qrc:/qml/sections/MultiplicationSection.qml"
    }

}
