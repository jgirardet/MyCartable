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
        property var quotient
        property var corps
        property var page

        function initPre() {
            secDB = fk.f("divisionSection", {
                "string": "264/11"
            });
            page = th.getBridgeInstance(item, "Page", secDB.page);
            sec = page.getSection(0);
            params = {
                "section": sec,
                "sectionItem": item
            };
        }

        function initPost() {
            quotient = findChild(tested, "quotientField");
            corps = findChild(tested, "corps");
        }

        function test_the_mock_model() {
            compare(sec.size, 45);
            compare(tested.model, sec.model);
        }

        function test_properties() {
            //        //1,10 (text) et 11 retenu droit,  21 : retenue gauche
            compare(corps.itemAtIndex(1).textinput.color, "#000000");
            //black
            compare(corps.itemAtIndex(10).textinput.color, "#000000");
            //black
            compare(corps.itemAtIndex(11).textinput.color, "#ff0000");
            //Red
            compare(corps.itemAtIndex(21).textinput.color, "#ff0000");
            compare(corps.itemAtIndex(1).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(corps.itemAtIndex(10).textinput.horizontalAlignment, TextInput.AlignHCenter);
            compare(corps.itemAtIndex(11).textinput.horizontalAlignment, TextInput.AlignLeft);
            compare(corps.itemAtIndex(21).textinput.horizontalAlignment, TextInput.AlignRight);
            compare(corps.itemAtIndex(1).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(corps.itemAtIndex(10).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(corps.itemAtIndex(11).textinput.verticalAlignment, TextInput.AlignVCenter);
            compare(corps.itemAtIndex(21).textinput.verticalAlignment, TextInput.AlignVCenter);
        }

        function test_regex_validator_data() {
            return [{
                "inp": "",
                "res": true
            }, {
                "inp": "1",
                "res": true
            }, {
                "inp": "12",
                "res": true
            }, {
                "inp": "1123443",
                "res": true
            }, {
                "inp": "1,",
                "res": true
            }, {
                "inp": "1,0",
                "res": true
            }, {
                "inp": "1,13245",
                "res": true
            }];
        }

        function test_regex_validator(data) {
            var exp = quotient.validator.regularExpression;
            compare(Boolean(data.inp.match(exp)), data.res);
        }

        function test_focus_is_highlighted() {
            var it = corps.itemAtIndex(1).textinput;
            it.focus = true;
            compare(Qt.colorEqual(it.background.color, "yellow"), true);
        }

        function test_morekeys() {
            //focus quotient ou corps quand Entrée pressé
            //            corps.itemAtIndex(13).textinput.text = "é";
            quotient.forceActiveFocus();
            compare(corps.focus, false);
            compare(quotient.focus, true);
            keyClick(Qt.Key_Return);
            compare(corps.itemAtIndex(16).textinput.focus, true);
            compare(quotient.focus, false);
            keyClick(Qt.Key_Return);
            compare(corps.focus, false);
            compare(quotient.focus, true);
            // got to line result
            mouseClick(corps.itemAtIndex(13));
            keyClick(Qt.Key_3);
            mouseClick(corps.itemAtIndex(13));
            keyClick(Qt.Key_Minus);
            compare(corps.currentIndex, 22);
            // got to line : chiffre abaisse
            mouseClick(corps.itemAtIndex(20));
            keyClick(Qt.Key_3);
            keyClick(Qt.Key_Plus);
            compare(corps.currentIndex, 25);
            // addRetenue
            mouseClick(corps.itemAtIndex(20));
            keyClick(Qt.Key_Asterisk);
            compare(corps.itemAtIndex(14).textinput.text, "1");
            compare(corps.itemAtIndex(6).textinput.text, "1");
        }

        function test_retenu_not_focusable() {
            var it = corps.itemAtIndex(3).textinput;
            it.text = 2;
            mouseClick(it);
            keyClick(Qt.Key_9);
            compare(it.text, "2");
        }

        function test_dividende_is_readonly() {
            var it = corps.itemAtIndex(3).textinput;
            compare(it.readOnly, true);
        }

        function test_foucs_onclick_case() {
            for (var i of Array(sec.size).keys()) {
                var it = corps.itemAtIndex(i).textinput;
                if (sec.model.readOnly(i)) {
                    it.focus = false;
                    compare(it.focus, false, i);
                    mouseClick(it);
                    compare(it.focus, false, i);
                } else {
                    mouseClick(it);
                    compare(it.focus, true, i);
                }
            }
        }

        function test_quotient() {
            mouseClick(tested.quotient);
            keyClick(Qt.Key_1);
            compare(tested.quotient.text, "1");
            tested.section.undoStack.undo();
            compare(tested.quotient.text, "");
            tested.section.undoStack.redo();
            compare(tested.quotient.text, "1");
        }

        name: "DivisionSection"
        testedNom: "qrc:/qml/sections/DivisionSection.qml"
    }

}
