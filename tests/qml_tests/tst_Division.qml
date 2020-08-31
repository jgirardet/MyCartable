import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/js/lodash.js" as Lodash

Item {
    id: item

    width: 600
    height: 600

    Component {
        id: modelComp

        ListModel {
            id: listmodel

            property int rows: 5
            property int columns: 9
            property int cursor: 0
            property int sectionId: 0
            property int size: 45
            property int virgule: 0
            property int diviseur: 11
            property real dividende: 264
            property string quotient: ""
            property var corps
            property var datas: ["", "2", "", "", "6", "", "", "4", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
            property var _editables: [34, 37, 40, 10, 43, 13, 16, 19, 22, 25, 28, 31]
            property var _moveCursor
            property var _addRetenues: ""

            function isDividendeLine(index) {
                return _.range(0, 9).includes(index) ? true : false;
            }

            function isMembreLine(index) {
                return Math.floor(index / columns) & 1 ? true : false;
            }

            function isRetenue(index) {
                return [11, 3, 6, 14, 21, 24, 29, 32].includes(index) ? true : false;
            }

            function isRetenueGauche(index) {
                return [3, 6, 21, 24].includes(index) ? true : false;
            }

            function isRetenueDroite(index) {
                return [11, 14, 29, 32].includes(index) ? true : false;
            }

            function readOnly(index) {
                return !isEditable(index);
            }

            function isEditable(index) {
                return _editables.includes(index);
            }

            function getInitialPosition() {
                return size - 1;
            }

            function moveCursor(index, key) {
                _moveCursor = [index, key];
            }

            function goToResultLine() {
                if (corps.currentIndex == 13)
                    corps.currentIndex = 25;
                else if (currentIndex == 31)
                    corps.currentIndex = 43;

            }

            function getPosByQuotient() {
                cursor = 13;
            }

            function goToAbaisseLine() {
                corps.currentIndex = 25;
            }

            function addRetenues() {
                _addRetenues = "added";
            }

            Component.onCompleted: {
                for (var x of datas) {
                    listmodel.append({
                        "display": x,
                        "edit": x
                    });
                }
            }
        }

    }

    CasTest {
        property var model
        property var quotient
        property var corps

        function initPre() {
            model = createTemporaryObject(modelComp, item);
            params = {
                "model": model
            };
        }

        function initPost() {
            quotient = findChild(tested, "quotientField");
            corps = findChild(tested, "corps");
            model.corps = corps;
        }

        function test_the_mock_model() {
            compare(model.count, model.size);
            compare(tested.model, model);
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
            quotient.forceActiveFocus();
            compare(corps.focus, false);
            compare(quotient.focus, true);
            keyClick(Qt.Key_Return);
            compare(corps.itemAtIndex(13).textinput.focus, true);
            compare(quotient.focus, false);
            keyClick(Qt.Key_Return);
            compare(corps.focus, false);
            compare(quotient.focus, true);
            // got to line result
            mouseClick(corps.itemAtIndex(13));
            keyClick(Qt.Key_Minus);
            compare(corps.currentIndex, 25);
            // got to line : chiffre abaisse
            mouseClick(corps.itemAtIndex(13));
            keyClick(Qt.Key_Plus);
            compare(corps.currentIndex, 25);
            // addRetenue
            keyClick(Qt.Key_Asterisk);
            compare(model._addRetenues, "added");
        }

        function test_retenu_not_focusable() {
            var it = corps.itemAtIndex(3).textinput;
            it.text = 2;
            //      it.forceActiveFocus()
            mouseClick(it);
            keyClick(Qt.Key_9);
            compare(it.text, "2");
        }

        function test_dividende_is_readonly() {
            var it = corps.itemAtIndex(3).textinput;
            compare(it.readOnly, true);
        }

        function test_foucs_onclick_case() {
            for (var i of Array(model.size).keys()) {
                if (!model._editables.includes(i)) {
                    var it = corps.itemAtIndex(i).textinput;
                    it.focus = false;
                    compare(it.focus, false, i);
                    mouseClick(it);
                    compare(it.focus, false, i);
                }
            }
            for (var i of model._editables) {
                var it = corps.itemAtIndex(i).textinput;
                mouseClick(it);
                compare(it.focus, true, i);
            }
        }

        name: "DivisionSection"
        testedNom: "qrc:/qml/operations/DivisionSectionBase.qml"
    }

}
