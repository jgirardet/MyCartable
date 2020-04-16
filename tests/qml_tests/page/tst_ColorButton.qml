import QtQuick 2.14
import ".."

Item {
  id: item
  width: 200
  height: 300

  CasTest {
    name: "ColorButton"
    testedNom: "qrc:/qml/menu/ColorButton.qml"
    params: {
      "color": "red",
      "type": "color"
    }

    function test_init() {
      compare(tested.color, "#ff0000")
      compare(tested.type, "color")
    }

    function test_ontriggered() {
      var editor = {
        res: null,
        setStyleFromMenu: function(args) {
          this.res = args
        }
      }
      var menu = createObj("qrc:/qml/menu/BaseMenu.qml")
      uiManager.menuTarget = editor
      tested.menu = menu
      mouseClick(tested)
      compare(editor.res.type, "color")
      compare(editor.res.value, "#ff0000")
    }
  }
}