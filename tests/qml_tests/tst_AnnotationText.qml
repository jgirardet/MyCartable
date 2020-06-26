import QtQuick 2.15

FocusScope {
  id: item
  width: 200 // important pout les tests
  height: 200 //important pour les tests
  focus: true
  property Item model: Item {
    /* beautify preserve:start */
     property var _removeRow:3
     /* beautify preserve:end */
    function removeRow(secId, flag) {
      _removeRow = [secId, flag]
    }
  }

  function move(dx, dy) {
    _move = [dx, dy]
  }
  /* beautify preserve:start */
  property var _move: null
  /* beautify preserve:end */
  //  function deleteAnnotation(obj) {}
  CasTest {
    name: "AnnotationText"
    testedNom: "qrc:/qml/annotations/AnnotationText.qml"
    /* beautify preserve:start */
    property var annot
    property var edit
    /* beautify preserve:end */
    function initPre() {
      //    item.currentAnnotation = null
      //      item.model._removeRow = 0
      edit = null
      annot = {
        "sectionId": 2,
        "classtype": "AnnotationText",
        "x": 0.4,
        "y": 0.2,
        "id": 34
        //        "height": 0.8
      }

      params = {
        "annot": annot,
        "referent": item,
        //        "index": index,
        "edit": edit
      }
    }

    function initPreCreate() {}

    function initPost() {

    }

    function test_initY() {
      compare(tested.pointSizeStep, 1)
      compare(tested.moveStep, 5)
      compare(tested.menu, uiManager.menuFlottantAnnotationText)
      compare(tested.height, tested.contentHeight)
      compare(tested.width, tested.contentWidth + 5)
    }

    function test_focus() {
      verify(tested.activeFocus) // focus at init empty text
      item.focus = false
      verify(!tested.focus)
      item.focus = true
      verify(tested.focus)
    }

    function test_init_from_annot() {
      // at init
      compare(tested.color, "#000000")
      compare(tested.font.underline, false)
      compare(tested.text, "")
      var bg = tested.background
      verify(Qt.colorEqual(bg.color, "blue"))
      annot = {
        "sectionId": 2,
        "classtype": "AnnotationText",
        "x": 0.4,
        "y": 0.2,
        "id": 34,
        "fgColor": "#123456",
        "bgColor": "#654321",
        "underline": true,
        "text": "blabla",
        "pointSize": 3
      }
      compare(tested.color, "#123456")
      compare(tested.font.underline, true)
      compare(tested.text, "blabla")
      verify(Qt.colorEqual(bg.color, "#654321"))

    }

    function test_font_size() {
      compare(tested.fontSizeFactor, 15) // value uiManager.annotationCurrentTextSizeFactor
      compare(tested.font.pixelSize, 13) // 200/15
      annot = {
        "sectionId": 2,
        "classtype": "AnnotationText",
        "x": 0.4,
        "y": 0.2,
        "pointSize": 3
      }
      var tested2 = createObj(testedNom, {
        "annot": annot,
        "referent": item,
      }, item)
      compare(tested2.fontSizeFactor, 3)
      compare(tested2.font.pixelSize, 66) // 200/3
      tested2.destroy() // avoid warning
    }

    function test_timer_remove_triggred_at_init() {
      var tm = findChild(tested, "timerRemove")
      verify(tm.running) // running at start
      tm.stop()
      tm.interval = 0

      // not text, remove
      tested.text = ""
      tm.start()
      wait(5)
      compare(item.model._removeRow, [annot.id, true])

      //  text, no remove
      item.model._removeRow = null
      tested.text = "aa"
      tm.start()
      wait(5)
      compare(item.model._removeRow, null)
    }

    function test_background() {
      // color teste plus haut dans test_init_from_annot
      var bg = tested.background
      // border
      item.focus = false
      verify(Qt.colorEqual(bg.border.color, "transparent"))
      item.focus = true
      verify(Qt.colorEqual(bg.border.color, "#21be2b"))
      compare(bg.opacity, ddb.annotationTextBGOpacity)
    }

    function test_focus_changed_cursor_at_end() {
      tested.text = "12345678"
      tested.cursorPosition = 2
      tested.focus = false
      tested.focus = true
      compare(tested.cursorPosition, 8)
    }

    function test_focus_changed_timerremovestart_if_empty_text() {
      var tm = findChild(tested, "timerRemove")
      tm.stop()
      tested.text = ""
      tested.focus = false
      tested.focus = true
      verify(tm.running)
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
      item.height = item.height * 2
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
    //

    function test_move_data() {
      return [{
        "key": Qt.Key_Left,
        "movex": -5,
        "movey": 0,
      }, {
        "key": Qt.Key_Right,
        "movex": 5,
        "movey": 0,
      }, {
        "key": Qt.Key_Up,
        "movex": 0,
        "movey": -5,
      }, {
        "key": Qt.Key_Down,
        "movex": 0,
        "movey": 5,
      }, ]
    }

    function test_move(data) {
      keyClick(data.key, Qt.ControlModifier)
      compare(item._move, [data.movex, data.movey])
    }

    function test_on_textChanged() {
      keyClick(Qt.Key_A)
      compare(edit, {
        "id": 34,
        "text": "a"
      })

    }

    function test_checkPointIsNotDraw() {
      verify(!tested.checkPointIsNotDraw(4, 5))
    }

  }
}