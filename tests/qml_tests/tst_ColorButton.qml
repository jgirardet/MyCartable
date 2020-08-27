import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 300

    CasTest {
        //      compare(editor.res.value, "#ff0000")
        //                "attrs": {
        //                }

        property var style: {
            "fgColor": "red"
        }

        function test_init() {
            compare(tested.color, "#ff0000");
            compare(tested.style.fgColor, "red");
        }

        function test_ontriggered() {
            var editor = {
                "res": null,
                "setStyleFromMenu": function(args) {
                    this.res = args;
                }
            };
            var menu = createObj("qrc:/qml/menu/BaseMenu.qml");
            uiManager.menuTarget = editor;
            tested.menu = menu;
            mouseClick(tested);
            var expected = {
                "style": {
                    "fgColor": "red"
                },
                "attrs": {
                }
            };
            compare(editor.res, expected);
        }

        name: "ColorButton"
        testedNom: "qrc:/qml/menu/ColorButton.qml"
        params: {
            "color": "red",
            "style": style
        }
    }

}
