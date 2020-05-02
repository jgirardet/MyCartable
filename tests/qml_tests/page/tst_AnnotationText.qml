import QtQuick 2.14

import ".."
Item {
  width: 200 // important pout les tests
  height: 200 //important pour les tests
  id: item
  function deleteAnnotation(obj) {}

  CasTest {
    name: "AnnotationText Cas"
    testedNom: "qrc:/qml/page/AnnotationText.qml"
    /* beautify preserve:start */
    property var objStyle
    property var model
    /* beautify preserve:end */
    function initPre() {

    }

    function initPreCreate() {
      model = ddb._loadAnnotations[0][0]
      objStyle = ddb._loadAnnotations[0][1]
      params = {
        "referent": item,
        "model": model,
        "objStyle": objStyle
      }
    }

    function initPost() {
      //      ref.annotations.push(tested)

    }
    DdbData {}

    function test_AnotXY() {
      compare(tested.x, 80)
      compare(tested.y, 100)
    }

    function test_focus() {
      tested.focus = true
      compare(tested.background.border.color, "#21be2b")
      compare(uiManager.menuTarget, tested)
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
        "referent": item,
        "model": model,
        "objStyle": objStyle
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
      tested.focus = true
      var spy = getSpy(tested, "deleteRequested")
      tested.text = ""
      tested.focus = false
      spy.wait()
    }

    function test_update_text() {
      tested.ddbId = 3
      tested.text = "bla"
      compare(ddb._updateAnnotation[0], 3)
      compare(ddb._updateAnnotation[1], {
        "text": "bla"
      })
    }

    function test_setStyle_color() {
      var data = {
        'style': {
          'fgColor': 'blue',
          'bgColor': 'red',
          'underline': true
        }
      }
      verify(!Qt.colorEqual(tested.color, "blue"))
      verify(!Qt.colorEqual(tested.background.color, "red"))
      verify(!tested.font.underline)

      tested.setStyleFromMenu(data)

      verify(Qt.colorEqual(tested.color, "blue"))
      verify(Qt.colorEqual(tested.background.color, "red"))
      verify(tested.font.underline)

      compare(ddb._setStyle[0], objStyle.id)
      compare(ddb._setStyle[1], data['style'])
    }

    function test_menu_show() {
      compare(uiManager.menuTarget, undefined)
      mouseClick(tested, 0, 0, Qt.RightButton)
      compare(uiManager.menuFlottantText.opened, true)
      compare(uiManager.menuFlottantText.target, tested)
    }

  }

}