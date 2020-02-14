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
    id: ddbcomp
    DdbMock {}
  }

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
  Component {
    id: anotinp
    AnnotationText {
      relativeX: 0.48
      relativeY: 0.10
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }
  TestCase {
    //
    name: "AnnotationText";when: windowShown
    property AnnotationText anot
    property Item ref
    property DdbMock ddb: null

    function init() {
      ddb = createTemporaryObject(ddbcomp, item)
      //      et pas   ref = createTemporaryObject(refcomp, item)// sinon Warn
      ref = refcomp.createObject(item)
      anot = anotinp.createObject(ref, {
        'ddb': ddb,
        "referent": ref
      })
      verify(anot)
      verify(ref)
      ref.annotations.push(anot)
    }

    function test_AnotXY() {
      compare(anot.x, 96)
      compare(anot.y, 20)
    }

    function test_focus() {
      anot.focus = true
      compare(anot.background.border.color, "#21be2b")
      anot.focus = false
      compare(anot.background.border.color, "#00000000")
    }

    function test_some_property() {
      compare(anot.selectByMouse, true)
    }

    function test_hover() {
      anot.focus = false
      mouseMove(anot, 1, 1)
      compare(anot.focus, true)
      var anot2 = createTemporaryObject(anotinp, ref, {
        "referent": ref,
        "relativeX": 0.8,
        "relativeY": 0.8
      })
      mouseMove(anot2, 1, 1)
      compare(anot.focus, false)
      compare(anot2.focus, true)
    }

    function test_hover_cursor_at_end() {
      anot.text = "12345678"
      mouseMove(anot, 1, 1)
      mouseClick(anot)
      compare(anot.cursorPosition, 4)
      mouseMove(anot, anot.width + 10, anot.height + 10)
      anot.focus = false
      mouseMove(anot, 1, 1)
      compare(anot.cursorPosition, 8)
    }

    //    function test_anot_destroy() {
    //      mouseClick(anot, 1, 1, Qt.MiddleButton)
    //      waitForRendering(ref)
    //      compare(ref.annotations, [])
    //    }

    function test_update_text() {
      anot.ddbId = 3
      anot.text = "bla"
      compare(ddb._updateAnnotation[0], 3)
      compare(ddb._updateAnnotation[1].value, "bla")
      compare(ddb._updateAnnotation[1].type, "text")
    }

//    function test_update_style() {
//      ddb._updateAnnotation = {}
//      stab.color = "blue"
//      var data = {'type':'color', 'value': 'red'}
//      stab.setStyle(data)
//      compare(stab.color,"#ff0000")
//      compare(ddb._updateAnnotation[0], stab.ddbId)
//      compare(ddb._updateAnnotation[1], data)
//    }

//
//    function test_menu_show() {
//      mouseClick(stab, 0, 0, Qt.RightButton)
//      compare(findChild(stab, "menuflottant").opened,true )
//    }
//
//    function test_menu_change_color() {
//      compare(stab.color, "#806633")
//      mouseClick(stab, 0, 0, Qt.RightButton)
//      var red = findChild(stab, "menuflottant")
//      waitForRendering(stab)
//      mouseClick(stab, red.x, red.y, Qt.LeftButton)
//      compare(Qt.colorEqual(stab.color, "red"), true)
//
//    }

  }
}