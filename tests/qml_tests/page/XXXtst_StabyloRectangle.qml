import QtQuick 2.14

import ".."
Item {
  id: itemparent
  width: 200
  height: 200
  Item {
    anchors.fill: parent
    implicitWidth: parent.width //important pour les tests
    id: item

  }

  function deleteAnnotation(obj) {
    _deleteAnnotation = obj
  }
  /* beautify preserve:start */
  property var _deleteAnnotation
  /* beautify preserve:end */
  CasTest {
    name: "StabyloRectangle"
    testedNom: "qrc:/qml/page/StabyloRectangle.qml"
    /* beautify preserve:start */
    property var model
    property  var objStyle
    /* beautify preserve:end */

    function initPreCreate() {
      model = ddb._loadAnnotations[1][0]
      objStyle = ddb._loadAnnotations[1][1]
      params = {
        "referent": item,
        "model": model,
        "objStyle": objStyle,
        "relativeX": 0.48,
        "relativeY": 0.10
      }
    }

    function initPost() {}

    function test_id() {
      compare(tested.relativeX, 0.48)
      compare(tested.ddbId, 6)
    }

    function test_AnotXY() {
      compare(tested.x, 96)
      compare(tested.y, 20)
    }

    function test_setStyle_color() {
      var data = {
        'style': {
          'bgColor': 'purple',
          'underline': true
        }
      }
      verify(!Qt.colorEqual(tested.color, "purple"))

      tested.setStyleFromMenu(data)

      verify(Qt.colorEqual(tested.color, "purple"))

      compare(ddb._setStyle[0], objStyle.id)
      compare(ddb._setStyle[1], data['style'])
    }

    function test_menu_show() {
      compare(uiManager.menuTarget, undefined)
      mouseClick(tested, 0, 0, Qt.RightButton)
      compare(uiManager.menuFlottantStabylo.opened, true)
      compare(uiManager.menuFlottantStabylo.target, tested)
    }

    function test_tested_destroy() {
      var spy = getSpy(tested, "deleteRequested")
      mouseClick(tested, 0, 0, Qt.MiddleButton)
      spy.wait()
      compare(itemparent._deleteAnnotation, tested)
    }

  }
}