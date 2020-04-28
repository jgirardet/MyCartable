import QtQuick 2.14

import ".."
Item {
  width: 200
  height: 200
  id: item

  Component {
    id: refcomp
    Item {
      x: item.x
      y: item.y
      width: item.width
      height: item.height
      /* beautify preserve:start */
      property var annotations: []
      /* beautify preserve:end */
      function deleteAnnotation(obj) {}
    }
  }

  CasTest {
    name: "Stabylo Rectangle"
    testedNom: "qrc:/qml/page/StabyloRectangle.qml"
    /* beautify preserve:start */
    property var ref
    /* beautify preserve:end */
    function initPre() {
      ref = refcomp.createObject(item)
      params = {
        "referent": ref,
        "relativeX": 0.48,
        "relativeY": 0.10
      }
    }

    function initPreCreate() {
      ddb = ddbData
    }

    function initPost() {
      ref.annotations.push(tested)
    }

    function test_id() {
      compare(tested.relativeX, 0.48)
      compare(tested.ddbId, 0)
    }

    function test_AnotXY() {
      compare(tested.x, 96)
      compare(tested.y, 20)
    }

    function test_setStyle() {
      ddb._updateAnnotation = {}
      tested.color = "blue"
      var data = {
        'type': 'color',
        'value': 'red'
      }
      tested.setStyleFromMenu(data)
      compare(tested.color, "#ff0000")
      compare(ddb._updateAnnotation[0], tested.ddbId)
      compare(ddb._updateAnnotation[1], data)
    }

    function test_menu_show() {
      compare(uiManager.menuTarget, undefined)
      mouseClick(tested, 0, 0, Qt.RightButton)
      compare(uiManager.menuFlottantStabylo.opened, true)
      compare(uiManager.menuFlottantStabylo.target, tested)
    }

    function test_menu_change_color() {
      tested.color = "blue"
      mouseClick(tested, 0, 0, Qt.RightButton)
      menuClick(uiManager.menuFlottantStabylo, 1, 30)
      compare(Qt.colorEqual(tested.color, "red"), true)

    }

    function test_tested_destroy() {
      var spy = ddb.getSpy(tested, "deleteRequested")
      mouseClick(tested, 0, 0, Qt.MiddleButton)
      spy.wait()
    }

  }
}