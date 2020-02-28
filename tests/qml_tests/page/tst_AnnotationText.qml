import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/page"
import ".."
Item {
  width: 200
  height: 200
  id: item

  Component {
    id: refcomp
    Item {
      width: item.width
      height: item.height
      /* beautify preserve:start */
      property var annotations: []
      /* beautify preserve:end */
      function deleteAnnotation(obj) {}
    }
  }

  CasTest {
    name: "AnnotationText Cas"
    testedNom: "qrc:/qml/page/AnnotationText.qml"
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
     function initPost() {
      ref.annotations.push(tested)
     }
    function test_AnotXY() {
      compare(tested.x, 96)
      compare(tested.y, 20)
    }

    function test_focus() {
      tested.focus = true
      compare(tested.background.border.color, "#21be2b")
      tested.focus = false
      compare(tested.background.border.color, "#00000000")
    }

    function test_some_property() {
      compare(tested.selectByMouse, true)
    }

    function test_hover() {
      tested.focus = false
      mouseMove(tested, 1, 1)
      compare(tested.focus, true)
      var tested2 = createObj("qrc:/qml/page/AnnotationText.qml", {
        "referent": ref,
        "relativeX": 0.8,
        "relativeY": 0.8,
        "uiManager": uiManager
      })
      mouseMove(tested2, 1, 1)
      compare(tested.focus, false)
      compare(tested2.focus, true)
    }

    function test_hover_cursor_at_end() {
      tested.text = "12345678"
      mouseMove(tested, 1, 1)
      mouseClick(tested)
      compare(tested.cursorPosition, 4)
      mouseMove(tested, tested.width + 10, tested.height + 10)
      tested.focus = false
      mouseMove(tested, 1, 1)
      compare(tested.cursorPosition, 8)
    }

    function test_tested_destroy_if_empty_when_leave() {
      tested.focus=true
      var spy = getSpy(tested, "deleteRequested")
      tested.text=""
      tested.focus=false
      spy.wait()
    }

    function test_update_text() {
      tested.ddbId = 3
      tested.text = "bla"
      compare(ddb._updateAnnotation[0], 3)
      compare(ddb._updateAnnotation[1].value, "bla")
      compare(ddb._updateAnnotation[1].type, "text")
    }

    function test_setStyle_color() {
      ddb._updateAnnotation = {}
      tested.color = "blue"
      var data = {'type':'color', 'value': 'red'}
      tested.setStyleFromMenu(data)
      compare(tested.color,"#ff0000")
      compare(ddb._updateAnnotation[0], tested.ddbId)
      compare(ddb._updateAnnotation[1], data)
    }

    function test_setStyle_underline() {
      ddb._updateAnnotation = {}
      var data = {'type':'underline', 'value': "red"}
      tested.setStyleFromMenu(data)
      compare(tested.color,"#ff0000")
      compare(tested.font.underline,true)
      compare(ddb._updateAnnotation[0], tested.ddbId)
      compare(ddb._updateAnnotation[1], data)
    }

    function test_setStyle_remove_underline() {
      ddb._updateAnnotation = {}
      tested.color = "blue"
      tested.font.underline = true
      var data = {'type':'color', 'value': "red"}
      tested.setStyleFromMenu(data)
      compare(tested.color,"#ff0000")
      compare(tested.font.underline,false)
      compare(ddb._updateAnnotation[0], tested.ddbId)
      compare(ddb._updateAnnotation[1], data)
    }

    function test_menu_show() {
      mouseClick(tested, 0, 0, Qt.RightButton)
      compare(uiManager.menuTarget,tested )
    }

      function test_menu_change_color() {
    compare(tested.color, "#353637")
    tested.text= "1234"
    tested.focus=true
    mouseClick(tested,  Qt.RightButton)
//    var red = findChild(tested, "menuflottant")
    waitForRendering(tested)
//    var menu = uiManager.menuFlottantText
//    waitForRendering(tested)
//    sleep(1000)
    mouseClick(tested)
//    sleep(5000)
    print(tested.color)
    compare(Qt.colorEqual(tested.color, "red"), true)

  }

    }

}