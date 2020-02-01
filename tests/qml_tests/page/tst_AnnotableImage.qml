import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/page"
import ".."
Item {
  id: item
  width: 200
  height: 300
  Component {
    id: anotimg
    AnnotableImage {
      content: {
        'content': '/home/jimmy/dev/cacahuete/MyCartable/tests/qml_tests/resources/tst_AnnotableImage.png'
      }
      //                source: '../resources/tst_AnnotableImage.png' // 767 x 669
      base: item
    }
  }
  //
  TestCase {
    id: testcase
    name: "AnnotableImage";when: windowShown
    property AnnotableImage anot: null
    //
    function init() {
      anot = createTemporaryObject(anotimg, item)
      tryCompare(anot.image, "progress", 1.0) // permet le temps de chargement async de l'image
    }

    function cleanup() {
      for (var x of anot.annotations) {
        x.destroy()
      }
      anot.destroy()
    }

    function test_init() {
      compare(anot.image.annotationInput.url, "qrc:/qml/page/AnnotationInput.qml")
      compare(anot.image.sourceSize.width, item.width)
    }

    function test_addannotation() {
      mouseClick(anot, 50, 30, Qt.RightButton)
      var inp = anot.annotations[0]
      compare(inp.focus, true)
      keyPress(Qt.Key_A)
      keyPress(Qt.Key_B)
      compare(inp.text, "ab")
      compare(inp.relativeX, 0.25)
      compare(inp.relativeY, 30 / anot.image.implicitHeight)
    }
    // r
    function test_detroy_annotations_before_destroy() {
      mouseClick(anot, 50, 30, Qt.RightButton)
      var inp = anot.annotations[0]
    }

    function test_init_zone() {
      mousePress(anot)
      compare(findChild(anot, "mouseArea").temp_rec.relativeWidth, 0)
    }

    function test_update_zone() {
      mousePress(anot, 50, 50)
      mouseMove(anot, 100, 170)
      var rec = findChild(anot, "mouseArea").temp_rec
      compare(rec.relativeWidth, 0.25)
      compare(rec.relativeHeight, 120 / 174) //174 et le ratio de la hauteur avec preservefit
    }

    function test_update_zone_negative_size() {
      mousePress(anot, 100, 100)
      mouseMove(anot, 50, 50)
      var rec = findChild(anot, "mouseArea").temp_rec
      compare(rec.relativeWidth, 0)
      compare(rec.relativeHeight, 0)
    }
    //
    function test_store_zone() {
      mousePress(anot, 50, 50)
      mouseMove(anot, 100, 170)
      mouseRelease(anot, 100, 170)
      var rec = findChild(anot, "mouseArea").temp_rec
      compare(rec, null)
      compare(anot.annotations[0].relativeWidth, 0.25)
      compare(anot.annotations[0].relativeHeight, 120 / 174) //cf plus heut
    }
    //
    function test_some_property() {
      // empeche le scroll quand onPositionChanged
      compare(findChild(anot, "mouseArea").preventStealing, true)
    }

    function test
  }
}