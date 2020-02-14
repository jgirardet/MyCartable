import QtQuick 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/page/menu"
import ".."

Item {
  id: item
  width: 200
  height: 300

  Component {
    id: ddbComp
    DdbMock {}
  }

  Component {
    id: testedComp
    ColorButton {
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }

  TestCase {
    id: testcase
    name: "ColorButton"
    when: windowShown

    property ColorButton tested
    property DdbMock ddb
    //
    function init() {
      ddb = createTemporaryObject(ddbComp, item)
      tested = createTemporaryObject(testedComp, item, {
        'ddb': ddb
      })
    }

    function cleanup() {
    }

    function test_init() {
      // check color is color type
      tested.color = "red"
      compare(tested.color, "#ff0000")
    }

    function test_ontriggered() {
      var editor = {
        res:null,
        setStyle: function(args) {
          this.res = args
        }
      }
     var menu = {editor: editor}
     tested.menu = menu
     tested.type = "color"
     tested.color = "red"
     mouseClick(tested)
     compare(editor.res.type, "color")
     compare(editor.res.value, "#ff0000")
    }
  }
}