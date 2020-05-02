import QtQuick 2.14
import ".."

Item {
  id: item
  width: 200
  height: 300

  CasTest {
    name: "ColorButton"
    testedNom: "qrc:/qml/menu/ColorButton.qml"
    /* beautify preserve:start */
    property var style : {
      "fgColor": "red"
    }
    /* beautify preserve:end */
    params: {
      "color": "red",
      "style": style

    }

    function test_init() {
      compare(tested.color, "#ff0000")
      compare(tested.style.fgColor, "red")
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
      print(JSON.stringify(editor.res))
      compare(editor.res, {
        "style": {
          'fgColor': "red"
        }
      })
      //      compare(editor.res.value, "#ff0000")
    }
  }
}