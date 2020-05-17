import QtQuick 2.14

import ".."
Item {
  id: parentitem
  width: 200 // important pout les tests
  height: 200 //important pour les tests
  Item {
    anchors.fill: parent
    implicitWidth: width //important pour les tests
    id: item
  }

  function deleteAnnotation(obj) {}
  CasTest {
    name: "AnnotationText"
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
    //    DdbData {}

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
      var datapre = {
        'fgColor': 'yellow',
        'bgColor': 'red',
        'underline': false
      }

      var data = {
        'style': {
          'fgColor': 'blue',
          'bgColor': 'purple',
          'underline': true
        }
      }

      verify(!Qt.colorEqual(tested.color, "blue"))
      tested.objStyle.underline = false
      tested.objStyleChanged()
      verify(!Qt.colorEqual(tested.background.color, "purple"))
      tryCompare(tested.font, "underline", false)
      //      verify(!tested.font.underline)

      tested.setStyleFromMenu(data)

      verify(Qt.colorEqual(tested.color, "blue"))
      verify(Qt.colorEqual(tested.background.color, "purple"))
      verify(tested.font.underline)

      compare(ddb._setStyle[0], 2)
      compare(ddb._setStyle[1], data['style'])
    }

    function test_menu_show() {
      compare(uiManager.menuTarget, undefined)
      mouseClick(tested, 0, 0, Qt.RightButton)
      compare(uiManager.menuFlottantText.opened, true)
      compare(uiManager.menuFlottantText.target, tested)
    }

    function test_add_new_line() {
      tested.text = ""
      mouseClick(tested)
      keyClick(Qt.Key_A)
      keyClick(Qt.Key_Return)
      keyClick(Qt.Key_B)
      compare(tested.text, "a\nb")
    }

    function test_taille_du_texte() {
      // pointSize empty donc default  = annotationCurrentTextSizeFactor
      compare(tested.fontSizeFactor, uiManager.annotationCurrentTextSizeFactor)

      compare(tested.fontSizeFactor, uiManager.annotationCurrentTextSizeFactor)
    }

    function test_taille_du_text_fonction_taille_image() {
      var old = (item.height / uiManager.annotationCurrentTextSizeFactor) | 0
      compare(tested.font.pixelSize, old)
      parentitem.height = parentitem.height * 2
      //      tested.referent.height = tested.referent.height * 2
      waitForRendering(tested)
      compare(tested.font.pixelSize, old * 2)
    }

    function test_grossi__text() {
      var size = tested.font.pixelSize
      compare(tested.fontSizeFactor, 15)
      tested.focus = true
      keyClick(Qt.Key_Plus, Qt.ControlModifier)
      compare(tested.fontSizeFactor, 14)
      compare(ddb._setStyle[1]['pointSize'], 14)
      verify(tested.font.pixelSize > size)
    }

    function test_diminue__text() {
      var size = tested.font.pixelSize
      tested.focus = true
      compare(tested.fontSizeFactor, 15)
      keyClick(Qt.Key_Minus, Qt.ControlModifier)
      compare(tested.fontSizeFactor, 16)
      compare(ddb._setStyle[1]['pointSize'], 16)
      verify(tested.font.pixelSize < size)
    }

    function test_drag() {
      var old = Qt.point(tested.x, tested.y)
      mouseDrag(tested, 1, 1, 20, 10, Qt.LeftButton, Qt.ControlModifier)
      compare(tested.x, old.x + 20)
      compare(tested.y, old.y + 10)
    }

    function test_move_with_arrows_left() {
      var old = Qt.point(tested.x, tested.y)
      keyClick(Qt.Key_Left, Qt.ControlModifier)
      compare(tested.x, old.x - tested.moveStep)
      compare(tested.y, old.y)
      compare(ddb._updateAnnotation[0], tested.ddbId)
      compare(ddb._updateAnnotation[1]["relativeX"], tested.x / parentitem.width)
      compare(ddb._updateAnnotation[1]["relativeY"], tested.y / parentitem.width)
    }

    function test_move_with_arrows_right() {
      var old = Qt.point(tested.x, tested.y)
      keyClick(Qt.Key_Right, Qt.ControlModifier)
      compare(tested.x, old.x + tested.moveStep)
      compare(tested.y, old.y)
      compare(ddb._updateAnnotation[0], tested.ddbId)
      compare(ddb._updateAnnotation[1]["relativeX"], tested.x / parentitem.width)
      compare(ddb._updateAnnotation[1]["relativeY"], tested.y / parentitem.width)
    }

    function test_move_with_arrows_up() {
      var old = Qt.point(tested.x, tested.y)
      keyClick(Qt.Key_Up, Qt.ControlModifier)
      compare(tested.x, old.x)
      compare(tested.y, old.y - tested.moveStep)
      compare(ddb._updateAnnotation[0], tested.ddbId)
      compare(ddb._updateAnnotation[1]["relativeX"], tested.x / parentitem.width)
      compare(ddb._updateAnnotation[1]["relativeY"], tested.y / parentitem.width)
    }

    function test_move_with_arrows_down() {
      var old = Qt.point(tested.x, tested.y)
      keyClick(Qt.Key_Down, Qt.ControlModifier)
      compare(tested.x, old.x)
      compare(tested.y, old.y + tested.moveStep)
      compare(ddb._updateAnnotation[0], tested.ddbId)
      compare(ddb._updateAnnotation[1]["relativeX"], tested.x / parentitem.width)
      compare(ddb._updateAnnotation[1]["relativeY"], tested.y / parentitem.width)
    }

  }

}