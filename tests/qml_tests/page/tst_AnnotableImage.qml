//import QtQuick 2.12
//import QtQuick.Layouts 1.12
//import QtQuick.Controls 2.12
//import QtTest 1.12
//import "../../../src/main/resources/base/qml/page"
//import ".."
//Item {
//  id: item
//  width: 200
//  height: 300
//
//  Component {
//    id: ddbcomp
//    DdbMock {}
//  }
//  Component {
//    id: anottext
//    AnnotationText {
//      relativeX: 0.48
//      relativeY: 0.10
//      /* beautify preserve:start */
//      property var ddb //need to inject ddb
//      property var uiManager //need to inject ddb
//      /* beautify preserve:end */
//    }
//  }
//
//  Component {
//    id: stabcomp
//    StabyloRectangle {
//      relativeX: 0.48
//      relativeY: 0.10
//      //referent: ref
//    }
//  }
//
//  Component {
//    id: anotimg
//    AnnotableImage {
//      sectionId: 1
//      base: item
//      //                source: '../resources/tst_AnnotableImage.png' // 767 x 669
//      /* beautify preserve:start */
//      property var ddb //need to inject ddb
//      property var uiManager //need to inject ddb
//
//      /* beautify preserve:end */
//    }
//  }
  //
//  TestCase {
//    id: testcase
//    name: "AnnotableImage";when: windowShown
//    property AnnotableImage anot: null
//    property DdbMock ddb: null
//    property Item uiManager: null
//    //
//    function init() {
//      ddb = createTemporaryObject(ddbcomp, item)
//      uiManager = createTemporaryObject(Qt.createComponent("../UiManager.qml"), item)
//      verify(ddb)
//      ddb._loadSection = ddb.sp.loadSection
//      anot = createTemporaryObject(anotimg, item, {
//        'ddb': ddb,
//        "uiManager": uiManager
//      })
//      tryCompare(anot.image, "progress", 1.0) // permet le temps de chargement async de l'image
//    }
//
//    function cleanup() {
//      if (anot) {
//        for (var x of anot.annotations) {
//          x.destroy()
//        }
//        anot.destroy()
//      }
//      ddb.destroy()
//      uiManager.destroy()
//    }
import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  CasTest {
    name: "AnnotableImage"
    testedNom: "qrc:/qml/page/AnnotableImage.qml"
    params: {}

    function initPre() {
    params = {"sectionId": 1, "base": item} // 767 x 669}
    }
    function initPreCreate() {
    ddb._loadSection = ddb.sp.loadSection
    }
    function initPost() {
    tryCompare(tested.image, "progress", 1.0) // permet le temps de chargement async de l'image
    }

    function test_init() {
      compare(tested.image.sourceSize.width, item.width)
    }



    function test_img_load_init() {
      compare(tested.image.source, Qt.resolvedUrl(ddb.sp.loadSection.path))
    }


    function test_addannotationText() {
      ddb._addAnnotation = ddb.sp.addAnnotation.AnnotationText
      mouseClick(tested, 50, 30, Qt.LeftButton)
      var inp = tested.annotations[0]
      compare(inp.focus, true)
      keyPress(Qt.Key_A) //press touche pour vérifier active focus immédiat
      keyPress(Qt.Key_B)
      //test type via duck typing
      compare(inp.relativeX, 0.25)
      compare(inp.relativeY, 30 / tested.image.implicitHeight)
      compare(inp.text, "ab")
      //test ddbIdSet
      compare(inp.ddbId, 4)
    }

    function test_detroy_annotations_before_destroy() {
      mouseClick(tested, 50, 30, Qt.RightButton)
      var inp = tested.annotations[0]
    }

    function test_init_zone() {
      mousePress(tested, undefined, undefined, Qt.RightButton)
      compare(findChild(tested, "mouseArea").temp_rec.relativeWidth, 0)
      compare(findChild(tested, "mouseArea").preventStealing, true)
    }

    function test_update_zone() {
      mousePress(tested, 50, 50, Qt.RightButton)
      mouseMove(tested, 100, 170)
      var rec = findChild(tested, "mouseArea").temp_rec
      compare(rec.relativeWidth, 0.25)
      compare(rec.relativeHeight, 120 / 174) //174 et le ratio de la hauteur avec preservefit
    }

    function test_update_zone_negative_size() {
      mousePress(tested, 100, 100, Qt.RightButton)
      mouseMove(tested, 50, 50)
      var rec = findChild(tested, "mouseArea").temp_rec
      compare(rec.relativeWidth, 0)
      compare(rec.relativeHeight, 0)
    }

    function test_store_zone() {
      ddb._addAnnotation = ddb.sp.addAnnotation.Stabylo
      mousePress(tested, 50, 50, Qt.RightButton)
      mouseMove(tested, 100, 170)
      mouseRelease(tested, 100, 170, Qt.RightButton)
      var rec = findChild(tested, "mouseArea").temp_rec
      compare(rec, null)
      compare(tested.annotations[0].relativeWidth, 0.25)
      compare(tested.annotations[0].relativeHeight, 120 / 174) //cf plus heut
      compare(tested.annotations[0].ddbId, 6)

    }

    function test_load_stabylo_on_completed() {
      tested.destroy()
      ddb._loadAnnotations = ddb.sp.loadAnnotations
      ddb._loadSection = ddb.sp.loadSection

      var ano = createObj("qrc:/qml/page/AnnotableImage.qml")
      compare(ano.annotations.length, 3)
      var item = ano.annotations[1]
      compare(item.relativeX, 0.5)
      compare(item.relativeY, 0.6)
      compare(item.relativeWidth, 0.1)
      compare(item.relativeHeight, 0.2)
      compare(item.ddbId, 2)
      compare(item.color, "#008000")


    }

    function test_load_annotationText_on_completed() {
      tested.destroy()
      ddb._loadAnnotations = ddb.sp.loadAnnotations
      ddb._loadSection = ddb.sp.loadSection
      var ano = createObj("qrc:/qml/page/AnnotableImage.qml")

      compare(ano.annotations.length, 3)
      var item = ano.annotations[0]
      compare(item.relativeX, 0.1)
      compare(item.relativeY, 0.2)
      compare(item.ddbId, 1)
      compare(item.text, "un annotation")

    }

    function test_load_annotationText__unerlinedon_completed() {
      tested.destroy()
      ddb._loadAnnotations = ddb.sp.loadAnnotations
      ddb._loadSection = ddb.sp.loadSection
      var ano = createObj("qrc:/qml/page/AnnotableImage.qml")

      compare(ano.annotations.length, 3)
      var obj = ano.annotations[2]
      compare(obj.color, "#008000")
      compare(obj.font.underline, true)
    }


    function test_delete_annotationText() {
      var testedText = createObj("qrc:/qml/page/AnnotationText.qml", {
        "ddbId": 5,
        "referent": tested,
//        "uiManager": uiManager
      })
      tested.annotations.push(testedText)

      mouseClick(testedText, 1, 1, Qt.MiddleButton)
      compare(ddb._deleteAnnotation, 5)
      compare(tested.annotations, [])
      waitForRendering(tested)
      compare(tested.ddbId, undefined)

    }

    function test_delete_stabylo() {
      var restabb = createObj("qrc:/qml/page/StabyloRectangle.qml", {
        "ddbId": 5,
        "referent": tested,
        "relativeX": 0.48,
         "relativeY": 0.10,
         "relativeHeight": 0.5,
         "relativeWidth": 0.5
      }, tested)
      tested.annotations.push(restabb)
      waitForRendering(restabb)
      var spy = getSpy(restabb, "deleteRequested")
      mouseClick(restabb,1 , 1, Qt.MiddleButton)
      spy.wait()
      compare(ddb._deleteAnnotation, 5)
      compare(tested.annotations, [])
      waitForRendering(tested)
      compare(restabb.ddbId, undefined)
    }

  }

}