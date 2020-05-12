import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  CasTest {
    name: "ImageSection"
    testedNom: "qrc:/qml/sections/ImageSection.qml"
    params: {}

    function initPre() {
      params = {
        "sectionId": 3796,
        "sectionItem": item
      } // 767 x 669}
    }

    function initPost() {
      tryCompare(tested.image, "progress", 1.0) // permet le temps de chargement async de l'image
    }

    function cleanup() {
      tested.destroy()
    }

    function test_init() {

      tryCompare(tested.image, "implicitWidth", item.width)
      //      tryCompare(tested.image.sourceSize, "width", item.width)
    }

    function test_img_load_init() {
      compare(tested.image.source, "qrc:/tests/tst_AnnotableImage.png")
    }
    //
    function test_addannotationText() {
      ddb._addAnnotation = [{
        'id': 99,
        'relativeX': 0.25,
        'relativeY': 0.4,
        'section': 1,
        'text': "",
        'classtype': 'AnnotationText'
      }, {
        'id': 1,
        'family': '',
        'underline': false,
        'pointSize': null,
        'strikeout': false,
        'weight': null,
        'annotation': 1,
        'bgColor': 'transparent',
        'fgColor': "black"
      }, ]
      mouseClick(tested, 10, 10, Qt.LeftButton)
      var inp = tested.annotations[tested.annotations.length - 1]
      compare(inp.focus, true)
      keyPress(Qt.Key_A) //press touche pour vérifier active focus immédiat
      keyPress(Qt.Key_B)
      //test type via duck typing
      compare(inp.relativeX, 0.25)
      compare(inp.relativeY, 0.4)
      //      / tested.image.implicitHeight)
      compare(inp.text, "ab")
      //test ddbIdSet
      compare(inp.ddbId, 99)
    }

    function test_click_create_zone() {

      mousePress(tested, 10, 100, Qt.RightButton)
      compare(findChild(tested, "mouseArea").temp_rec.relativeWidth, 0.5) // jsute valeur de reout
      compare(ddb._addAnnotation.relativeWidth, 0)
      compare(findChild(tested, "mouseArea").preventStealing, true)
    }

    function test_update_zone() {
      mousePress(tested, 50, 50, Qt.RightButton)
      var rec = findChild(tested, "mouseArea").temp_rec
      rec.x = 50
      rec.y = 50 // car problème avec le mock
      mouseMove(tested, 100, 170)
      compare(rec.relativeWidth, 0.25)
      compare(rec.relativeHeight, 120 / 174) //174 et le ratio de la hauteur avec preservefit
    }

    function test_update_zone_negative_size() {
      mousePress(tested, 50, 50, Qt.RightButton)
      mouseMove(tested, 20, 20)
      var rec = findChild(tested, "mouseArea").temp_rec
      compare(rec.relativeWidth, 0)
      compare(rec.relativeHeight, 0)
    }

    function test_update_not_triggered_if_no_temp_rec() {
      //lerreur s'affiche dans les warn si'l elle existe
      mousePress(tested, 100, 100, Qt.LeftButton)
      mouseMove(tested, 50, 50)
    }
    //
    //    function test_store_zone() {
    //      // index 4 car deja 4 dans la ddb
    //      mousePress(tested, 50, 50, Qt.RightButton)
    //      var rec = findChild(tested, "mouseArea").temp_rec
    //      rec.x = 50
    //      rec.y = 50 // car problème avec le mock
    //      mouseMove(tested, 100, 170)
    //      mouseRelease(tested, 100, 170, Qt.RightButton)
    //      //      var rec = findChild(tested, "mouseArea").temp_rec
    //      //      compare(rec, null)
    //      //      compare(tested.annotations[4].relativeWidth, 0.25)
    //      //      compare(tested.annotations[4].relativeHeight, 120 / 174) //cf plus heut
    //      //      compare(tested.annotations[4].ddbId, 1)
    //
    //    }

    //    function test_load_stabylo_on_completed() {
    //      tested.destroy()
    //
    //      var ano = createObj("qrc:/qml/page/AnnotableImage.qml", {
    //        "sectionId": 1,
    //        "base": item
    //      })
    //      compare(ano.annotations.length, 4)
    //      var item2 = ano.annotations[1]
    //      compare(item2.relativeX, 0.48)
    //      compare(item2.relativeY, 0.10)
    //      compare(item2.relativeWidth, 0.226457399103139)
    //      compare(item2.relativeHeight, 0.07969151670951156)
    //      compare(item2.ddbId, 6)
    //      compare(Qt.colorEqual(item2.color, "blue"), true)

    //  }
    //
    //    function test_load_annotationText_on_completed() {
    //      tested.destroy()
    //      var ano = createObj("qrc:/qml/page/AnnotableImage.qml", {
    //        "sectionId": 1,
    //        "base": item
    //      })
    //
    //      compare(ano.annotations.length, 4)
    //      var itemx = ano.annotations[0]
    //      compare(itemx.relativeX, 0.16367713004484305)
    //      compare(itemx.relativeY, 0.6580976863753213)
    //      compare(itemx.ddbId, 7)
    //      compare(itemx.text, "un annotation")
    //
    //    }
    //
    //    function test_load_annotationText__unerlinedon_completed() {
    //      tested.destroy()
    //      var ano = createObj("qrc:/qml/page/AnnotableImage.qml", {
    //        "sectionId": 1,
    //        "base": item
    //      })
    //
    //      compare(ano.annotations.length, 4)
    //      var obj = ano.annotations[2]
    //      compare(obj.color, "#008000")
    //      compare(obj.font.underline, true)
    //    }
    //
    //    function test_delete_annotationText() {
    //      var testedText = createObj("qrc:/qml/page/AnnotationText.qml", {
    //        "ddbId": 5,
    //        "referent": tested,
    //        //        "uiManager": uiManager
    //      })
    //      tested.annotations = []
    //      tested.annotations.push(testedText)
    //
    //      mouseClick(testedText, 1, 1, Qt.MiddleButton)
    //      compare(ddb._deleteAnnotation, 5)
    //      compare(tested.annotations, [])
    //      waitForRendering(tested)
    //      compare(tested.ddbId, undefined)
    //
    //    }
    //
    //    function test_delete_stabylo() {
    //      var restabb = createObj("qrc:/qml/page/StabyloRectangle.qml", {
    //        "ddbId": 5,
    //        "referent": tested,
    //        "relativeX": 0.48,
    //        "relativeY": 0.10,
    //        "relativeHeight": 0.5,
    //        "relativeWidth": 0.5
    //      }, tested)
    //      tested.annotations = []
    //      tested.annotations.push(restabb)
    //      waitForRendering(restabb)
    //      var spy = getSpy(restabb, "deleteRequested")
    //      mouseClick(restabb, 1, 1, Qt.MiddleButton)
    //      spy.wait()
    //      compare(ddb._deleteAnnotation, 5)
    //      compare(tested.annotations, [])
    //      waitForRendering(tested)
    //      compare(restabb.ddbId, undefined)
    //    }

  }

}