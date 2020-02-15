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
    id: anottext
    AnnotationText {
      relativeX: 0.48
      relativeY: 0.10
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }

  Component {
    id: stabcomp
    StabyloRectangle {
      relativeX: 0.48
      relativeY: 0.10
      //referent: ref
    }
  }

  Component {
    id: anotimg
    AnnotableImage {
      sectionId: 1
      base: item
      //                source: '../resources/tst_AnnotableImage.png' // 767 x 669
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
      ddb._loadSection = ddb.sp.loadSection
      anot = createTemporaryObject(anotimg, item, {
        'ddb': ddb
      })
      tryCompare(anot.image, "progress", 1.0) // permet le temps de chargement async de l'image
    }

    function cleanup() {
      if (anot) {
        for (var x of anot.annotations) {
          x.destroy()
        }
        anot.destroy()
      }
      ddb.destroy()
    }

    function test_init() {
      compare(anot.image.sourceSize.width, item.width)
    }

    function test_addannotationText() {
      ddb._addAnnotation = ddb.sp.addAnnotation.AnnotationText
      mouseClick(anot, 50, 30, Qt.LeftButton)
      var inp = anot.annotations[0]
      compare(inp.focus, true)
      keyPress(Qt.Key_A) //press touche pour vérifier active focus immédiat
      keyPress(Qt.Key_B)
      //test type via duck typing
      compare(inp.relativeX, 0.25)
      compare(inp.relativeY, 30 / anot.image.implicitHeight)
      compare(inp.text, "ab")
      //test ddbIdSet
      compare(inp.ddbId, 4)
    }

    function test_detroy_annotations_before_destroy() {
      mouseClick(anot, 50, 30, Qt.RightButton)
      var inp = anot.annotations[0]
    }

    function test_init_zone() {
      mousePress(anot, undefined, undefined, Qt.RightButton)
      compare(findChild(anot, "mouseArea").temp_rec.relativeWidth, 0)
      compare(findChild(anot, "mouseArea").preventStealing, true)
    }

    function test_update_zone() {
      mousePress(anot, 50, 50, Qt.RightButton)
      mouseMove(anot, 100, 170)
      var rec = findChild(anot, "mouseArea").temp_rec
      compare(rec.relativeWidth, 0.25)
      compare(rec.relativeHeight, 120 / 174) //174 et le ratio de la hauteur avec preservefit
    }

    function test_update_zone_negative_size() {
      mousePress(anot, 100, 100, Qt.RightButton)
      mouseMove(anot, 50, 50)
      var rec = findChild(anot, "mouseArea").temp_rec
      compare(rec.relativeWidth, 0)
      compare(rec.relativeHeight, 0)
    }

    function test_store_zone() {
      ddb._addAnnotation = ddb.sp.addAnnotation.Stabylo
      mousePress(anot, 50, 50, Qt.RightButton)
      mouseMove(anot, 100, 170)
      mouseRelease(anot, 100, 170, Qt.RightButton)
      var rec = findChild(anot, "mouseArea").temp_rec
      compare(rec, null)
      compare(anot.annotations[0].relativeWidth, 0.25)
      compare(anot.annotations[0].relativeHeight, 120 / 174) //cf plus heut
      compare(anot.annotations[0].ddbId, 5)

      // check popup not opened
      compare(findChild(anot, "menuflottant").opened,false )
    }

    function test_affiche_popup() {
      mouseClick(anot, 100, 100, Qt.RightButton)
       var rec = findChild(anot, "menuflottant")
       compare(rec.opened,true )
    }

    function test_img_load_init() {
      compare(anot.image.source, Qt.resolvedUrl(ddb.sp.loadSection.path))
    }

    function test_load_stabylo_on_completed() {
      anot.destroy()
      ddb._loadAnnotations = ddb.sp.loadAnnotations
      ddb._loadSection = ddb.sp.loadSection

      var ano = createTemporaryObject(anotimg, item, {
        'ddb': ddb
      })
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
      anot.destroy()
      ddb._loadAnnotations = ddb.sp.loadAnnotations
      ddb._loadSection = ddb.sp.loadSection

      var ano = createTemporaryObject(anotimg, item, {
        'ddb': ddb
      })
      compare(ano.annotations.length, 3)
      var item = ano.annotations[0]
      compare(item.relativeX, 0.1)
      compare(item.relativeY, 0.2)
      compare(item.ddbId, 1)
      compare(item.text, "un annotation")

    }

    function test_load_annotationText__unerlinedon_completed() {
      anot.destroy()
      ddb._loadAnnotations = ddb.sp.loadAnnotations
      ddb._loadSection = ddb.sp.loadSection

      var ano = createTemporaryObject(anotimg, item, {
        'ddb': ddb
      })
      compare(ano.annotations.length, 3)
      var obj = ano.annotations[2]
      compare(obj.color, "#008000")
      compare(obj.font.underline, true)

    }

    function test_delete_annotationText() {
      var anotText = anottext.createObject(anot, {
        'ddb': ddb,
        "ddbId": 5,
        "referent": anot,
        "text": "blabla"
      })
      anot.annotations.push(anotText)

      mouseClick(anotText, 1, 1, Qt.MiddleButton)
      compare(ddb._deleteAnnotation, 5)
      compare(anot.annotations, [])
      waitForRendering(anot)
      compare(anot.ddbId, undefined)

    }

    function test_delete_stabylo() {
      anot.destroy()
      ddb._loadAnnotations = ddb.sp.loadAnnotations
      ddb._loadSection = ddb.sp.loadSection
      ddb._deleteAnnotation = null

      var anno = createTemporaryObject(anotimg, item, {
        'ddb': ddb
      })
      var stab = anno.annotations[1]
      sleep(5000)
      print(stab.ddbId)
      mouseClick(stab, 0, 0, Qt.MiddleButton)
      waitForRendering(anno)
      compare(anno.annotations.length, 2)
      compare(ddb._deleteAnnotation, 2)
      compare(anno.ddbId, undefined)

    }


  }
}