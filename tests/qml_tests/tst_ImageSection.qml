import QtQuick 2.14

Item {
  width: 200
  height: 300
  id: item

  //  property var model: Item {
  //    id: model
  //    property var _addAnnotation: null

  //
  //    function addAnnotation(mx, my, mwidth, mheight) {
  //      _addAnnotation = [mx, my, mwidth, mheight]
  //    }
  //
  //    function rowCount
  //  }
  Component {
    id: modelComp
    ListModel {
      id: listmodel
      /* beautify preserve:start */
      ////      property int rows: 0
      property var _addAnnotation: null
            /* beautify preserve:end */
      function addAnnotation(mx, my, mwidth, mheight) {
        _addAnnotation = [mx, my, mwidth, mheight]
      }
    }
  }

  CasTest {
    name: "ImageSection"
    testedNom: "qrc:/qml/annotations/ImageSectionBase.qml"
    /* beautify preserve:start */
    property var model
    property var canvas
    /* beautify preserve:end */
    params: {}

    function initPre() {
      model = createTemporaryObject(modelComp, item)

      params = {
        "sectionId": 3796,
        "sectionItem": item,
        "model": model
      } // 767 x 669}

      //      item.model._addAnnotation = null
    }

    function initPost() {
      tryCompare(tested, "progress", 1.0) // permet le temps de chargement async de l'image
      canvas = findChild(tested, "canvasFactory")
    }

    //    function cleanup() {
    //      tested.destroy()
    //    }

    function test_init() {
      tryCompare(tested, "implicitWidth", item.width)
    }

    function test_img_load_init() {
      compare(tested.source, "qrc:/tests/tst_AnnotableImage.png")
      compare(tested.width, 200)
      compare(tested.height, 174) // 669 * item.width / 767
    }

    function test_Mousearea_init() {
      compare(tested.mousearea.width, tested.width)
      compare(tested.mousearea.height, tested.height)
    }

    function test_left_click_no_modifier_currenttool_is_text() {
      uiManager.annotationCurrentTool = "text"
      mouseClick(tested, 3, 10, Qt.LeftButton)
      compare(model._addAnnotation, [3, 10, 200, 174])
    }

    function test_left_click_no_modifier_currenttool_is_not_text() {
      uiManager.annotationCurrentTool = "rect"
      mouseClick(tested, 3, 10, Qt.LeftButton)
      compare(model._addAnnotation, null)
    }

    function test_left_click_ctrl_modifier() {
      uiManager.annotationCurrentTool = "rect"
      mouseClick(tested, 3, 10, Qt.LeftButton, Qt.ControlModifier)
      compare(model._addAnnotation, [3, 10, 200, 174])
    }

    function test_right_click_ctrl_modifier() {
      uiManager.annotationCurrentTool = "text"
      mousePress(tested, 3, 10, Qt.RightButton, Qt.ControlModifier)
      compare(model._addAnnotation, null)
      verify(canvas.painting) // painting True == startDraw called
      verify(canvas.useDefaultTool)
    }

    function test_left_press_currentool_is_not_text() {
      uiManager.annotationCurrentTool = "trait"
      uiManager.annotationDessinCurrentTool = "trait"
      mousePress(tested, 3, 10, Qt.LeftButton)
      verify(canvas.painting) // painting True == startDraw called
      verify(!canvas.useDefaultTool)
      compare(canvas.tool, "trait")
    }

    function test_release_enddraw() {
      mousePress(tested, 3, 10, Qt.RightButton, Qt.ControlModifier)
      verify(canvas.painting) // painting True == startDraw called
      mouseRelease(tested, 3, 10, Qt.RightButton)
      verify(!canvas.painting)
    }

    function test_move_draw() {
      mousePress(tested, 3, 10, Qt.RightButton, Qt.ControlModifier)
      verify(!canvas.visible)
      mouseMove(tested, 33, 100)
      waitForRendering(canvas)
      verify(canvas.visible) // onPaint called
    }

    function test_right_click_affiche_menu() {
      compare(uiManager.menuFlottantImage.visible, false)
      mouseClick(tested, 0, 0, Qt.RightButton)
      compare(uiManager.menuFlottantImage.visible, true)

    }

    function test_annotation_repeter() {
      var rep = findChild(tested, "repeater")
      compare(rep.count, 0)
      model.append({
        "annot": {
          "sectionId": 2,
          "classtype": "AnnotationText"
        }
      })
      compare(rep.count, 1)
    }

    function test_CanvasFactory_init() {
      compare(canvas.mouse, tested.mousearea)
      compare(canvas.width, tested.width)
      compare(canvas.height, tested.height)
    }

    function test_setStyleFromMenu_all(data) {
      uiManager.annotationDessinCurrentLineWidth = 1
      uiManager.annotationDessinCurrentStrokeStyle = "#ffffff"
      uiManager.annotationCurrentTool = "rect"
      uiManager.annotationDessinCurrentTool = "trait"
      tested.setStyleFromMenu({
        "style": {
          "pointSize": 15,
          "fgColor": "#111111",
          "tool": "ellipse"
        }
      })
      compare(uiManager.annotationDessinCurrentLineWidth, 15)
      compare(uiManager.annotationDessinCurrentStrokeStyle, "#111111")
      compare(uiManager.annotationCurrentTool, "ellipse")
      compare(uiManager.annotationDessinCurrentTool, "ellipse")
    }

    function test_setStyleFromMenu_to_text(data) {
      uiManager.annotationCurrentTool = "rect"
      uiManager.annotationDessinCurrentTool = "trait"
      tested.setStyleFromMenu({
        "style": {
          "tool": "text"
        }
      })
      compare(uiManager.annotationCurrentTool, "text")
      compare(uiManager.annotationDessinCurrentTool, "fillrect")
    }

    function test_setStyleFromMenu_nothing(data) {
      uiManager.annotationDessinCurrentLineWidth = 1
      uiManager.annotationDessinCurrentStrokeStyle = "#ffffff"
      uiManager.annotationCurrentTool = "rect"
      uiManager.annotationDessinCurrentTool = "trait"
      tested.setStyleFromMenu({})
      compare(uiManager.annotationDessinCurrentLineWidth, 1)
      compare(uiManager.annotationDessinCurrentStrokeStyle, "#ffffff")
      compare(uiManager.annotationCurrentTool, "rect")
      compare(uiManager.annotationDessinCurrentTool, "trait")
    }

  }

}