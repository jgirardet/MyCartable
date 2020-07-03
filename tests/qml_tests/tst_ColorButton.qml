import QtQuick 2.14

Item {
    id: item

    width: 200
    height: 300

    CasTest {
        //      compare(editor.res.value, "#ff0000")

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
            compare(editor.res, {
                "style": {
                    "fgColor": "red"
                }
            });
        }

        name: "ColorButton"
        testedNom: "qrc:/qml/menu/ColorButton.qml"
        params: {
            "color": "red",
            "style": style
        }
    }

}
