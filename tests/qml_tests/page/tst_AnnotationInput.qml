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
      property
      var annotations: []
    }
  }
  Component {
    id: anotinp
    AnnotationInput {
      relativeX: 0.48
      relativeY: 0.10
      //referent: ref
    }
  }
  TestCase {
    //
    name: "AnnotationInput";when: windowShown
    property AnnotationInput anot
    property Item ref

    function init() {
      //          ref = createTemporaryObject(refcomp, item)// sinon Warn
      ref = refcomp.createObject(item)
      anot = anotinp.createObject(ref, {
        "referent": ref
      })
      verify(anot)
      verify(ref)
      ref.annotations.push(anot)
    }

    function cleanup() {
      //            if (anot) {
      //                anot.destroy()
      //            }
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

    function test_anot_destroy() {
      mouseClick(anot, 1, 1, Qt.MiddleButton)
      waitForRendering(ref)
      compare(ref.annotations, [])
    }
    //        function test_anot_destroy_ref_already_destroyed() {
    //            ref.destroy()
    //            mouseClick(anot, 1, 1, Qt.MiddleButton)
    //            waitForRendering(ref)
    //            compare(ref.annotations, [])
    //        }
  }
}