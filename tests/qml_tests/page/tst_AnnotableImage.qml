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
    id: ddbcomp
    DdbMock {}
  }
  Component {
    id: anotimg
    AnnotableImage {
      content: {
        'content': '/home/jimmy/dev/cacahuete/MyCartable/tests/qml_tests/resources/tst_AnnotableImage.png',
        'annotations': []
      }
      //                source: '../resources/tst_AnnotableImage.png' // 767 x 669
      base: item
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }
  //
  TestCase {
    id: testcase
    name: "AnnotableImage";when: windowShown
    property AnnotableImage anot: null
    property DdbMock ddb: null
    //
    function init() {
      ddb = createTemporaryObject(ddbcomp, item)
      verify(ddb)
      //      anot = createTemporaryObject(anotimg, item)
      anot = createTemporaryObject(anotimg, item, {
        'ddb': ddb
      })
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
      ddb._addAnnotation = 1
      mousePress(anot, 50, 50)
      mouseMove(anot, 100, 170)
      mouseRelease(anot, 100, 170)
      var rec = findChild(anot, "mouseArea").temp_rec
      compare(rec, null)
      compare(anot.annotations[0].relativeWidth, 0.25)
      compare(anot.annotations[0].relativeHeight, 120 / 174) //cf plus heut
      compare(anot.annotations[0].ddbId, 1)
    }
    //
    function test_some_property() {
      // empeche le scroll quand onPositionChanged
      compare(findChild(anot, "mouseArea").preventStealing, true)
    }

    function test_load_stabylo_on_completed() {
      ddb._loadAnnotations = [{
            "classtype": "Stabylo",
            "id": 1,
            "section": 1,
            "x": 0.3,
            "y": 0.4,
            "width": 0.5,
            "height": 0.6,
          }]
       var ano = createTemporaryObject(anotimg, item, {
        'ddb': ddb
      })

      compare(ano.annotations.length, 1)
      var item = ano.annotations[0]
      compare(item.relativeX, 0.3)
      compare(item.relativeY, 0.4)
      compare(item.relativeWidth, 0.5)
      compare(item.relativeHeight, 0.6)

    }

//    function test_load_annotation_on_completed() {
//      var ano = createTemporaryObject(anotimg, item, {
//        "content": {
//          'content': '/home/jimmy/dev/cacahuete/MyCartable/tests/qml_tests/resources/tst_AnnotableImage.png',
//          'annotations': [{
//            "classtype": "Annotation",
//            "id": 1,
//            "section": 1,
//            "x": 0.3,
//            "y": 0.4,
//            "text": "blabla"
//          }]
//
//        }
//      })
//
//      compare(ano.annotations.length, 1)
//      var item = ano.annotations[0]
//      compare(item.relativeX, 0.3)
//      compare(item.relativeY, 0.4)
//      compare(item.text, "blabla")
//    }
  }
}