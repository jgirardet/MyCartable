import QtQuick 2.15

Item {
  id: item
  width: 200 // important pout les tests
  height: 300 //important pour les
  implicitWidth: width
  implicitHeight: height // si pas de taille, pas ed paint
  CasTest {
    id: testCase
    name: "AnnotationDessin"
    testedNom: "qrc:/qml/annotations/AnnotationDessin.qml"
    /* beautify preserve:start */
    property var annot
    /* beautify preserve:end */
    function initPre() {
      annot = {
        "sectionId": 2,
        "classtype": "AnnotationDessin",
        "x": 0.4,
        "y": 0.2,
        "id": 34,
        "fgColor": "#0000ff",
        "bgColor": "#654321",
        "pointSize": 12,
        "width": 0.4,
        "height": 0.5,
        "startX": 0.3,
        "startY": 0.7,
        "endX": 0.5,
        "endY": 0.9
      }

      params = {
        "annot": annot,
        "referent": item,
      }
    }

    function initPreCreate() {}

    function initPost() {

    }

    function test_ini() {
      compare(tested.menu, uiManager.menuFlottantAnnotationDessin)
      compare(tested.strokeStyle, "#0000ff")
      compare(tested.fillStyle, "#654321")
      compare(tested.lineWidth, 12)
    }

    function test_requestPaint_on_fgcolor() {
      var spy = getSpy(tested, "painted")
      annot.fgColor = "#33333"
      spy.wait()
    }

    function test_requestPaint_on_bg_color() {
      var spy = getSpy(tested, "painted")
      annot.bgColor = "#33333"
      spy.wait()
    }

    function test_requestPaint_on_lineWidth() {
      var spy = getSpy(tested, "painted")
      annot.pointSize = 999
      spy.wait()
    }

    function test_draw_data() {
      return [{
        "tool": "trait"
      }, {
        "tool": "rect"
      }, {
        "tool": "fillrect"
      }, {
        "tool": "ellipse"
      }, ]
    }

    function test_draw(data) {
      // en pratique on test surtout en regression
      var spy = getSpy(tested, "painted")
      annot.tool = data.tool
      tested.requestPaint()
      spy.wait()
      var img = Qt.createQmlObject(`import QtQuick 2.15; Image {source: 'assets/${data.tool}.png'}`, item)
      var c = Qt.createQmlObject(`import QtQuick 2.15; Canvas {height:${tested.height};width:${tested.width}}`, item)
      tryCompare(c, "available", true)
      var ctx = c.getContext("2d")
      ctx.drawImage(img, 0, 0)
      compare(tested.toDataURL(), c.toDataURL())
    }

    function test_fillrect_opacity() {
      var spy = getSpy(tested, "painted")
      annot.tool = "fillrect"
      tested.opacity = 1
      tested.requestPaint()
      spy.wait()
      compare(tested.opacity, 0.2)

      var spy = getSpy(tested, "painted")
      annot.tool = "rect"
      tested.opacity = 1
      tested.requestPaint()
      spy.wait()
      compare(tested.opacity, 1)
    }

    function test_checkpointis_NotDraw_data() {
      // strokeREct(24, 205, 16, 30)
      //linewidth = 12
      return [{
          "mx": 1,
          "my": 1,
          "res": true
        }, {
          "mx": 24 + 1, // en haut a gauche
          "my": 105 + 2,
          "res": false
        }, {
          "mx": 24 + 7, // trou
          "my": 105 + 7,
          "res": true
        }, {
          "mx": 40, // en haut a gauche
          "my": 135,
          "res": false
        }

      ]
    }

    function test_checkpointis_NotDraw(data) {
      var spy = getSpy(tested, "painted")
      annot.tool = "rect"
      tested.requestPaint()
      spy.wait()
      compare(tested.checkPointIsNotDraw(data.mx, data.my), data.res)
    }

  }
}