import QtQuick 2.14
import ".."
import Qt.labs.qmlmodels 1.0

Item {
  width: 200
  height: 200
  id: item

  Component {
    id: modelComp
    TableModel {

      property int n_rows: rowCount

      CustomTableModelColumn {
        display: "zero"
        edit: "editZero"
        background: "bgZero"
        foreground: "fgZero"
        underline: "uZero"
        pointSize: "psZero"
      }
      CustomTableModelColumn {
        display: "un"
        edit: "editUn"
        background: "bgUn"
        foreground: "fgUn"
        underline: "uUn"
        pointSize: "psUn"
      }
      CustomTableModelColumn {
        display: "deux"
        edit: "editDeux"
        background: "bgDeux"
        foreground: "fgDeux"
        underline: "uDeux"
        pointSize: "psDeux"
      }
      rows: [
        //      [
        {
          zero: "0",
          un: "1",
          deux: "2",
          editZero: "",
          editUn: "",
          editDeux: "",
          bgZero: "red",
          bgUn: "blue",
          bgDeux: "green",
          fgZero: "black",
          fgUn: "orange",
          fgDeux: "orange",
          uZero: true,
          uUn: false,
          uDeux: false,
          psZero: 10,
          psUn: 12,
          psDeux: 14

        }, {
          zero: "3",
          un: "4",
          deux: "5",
          editZero: "",
          editUn: "",
          editDeux: "",
          bgZero: null,
          bgUn: null,
          bgDeux: "green",
          fgZero: "black",
          fgUn: "orange",
          fgDeux: "orange",
          uZero: true,
          uUn: false,
          uDeux: false,
          psZero: 10,
          psUn: 12,
          psDeux: 14
        }, {
          zero: "6",
          un: "7",
          deux: "8",
          editZero: "",
          editUn: "",
          editDeux: "",
          bgZero: null,
          bgUn: null,
          bgDeux: "green",
          fgZero: "black",
          fgUn: "orange",
          fgDeux: "orange",
          uZero: true,
          uUn: false,
          uDeux: false,
          psZero: 10,
          psUn: 12,
          psDeux: 14
        }, {
          zero: "9",
          un: "10",
          deux: "11",
          editZero: "",
          editUn: "",
          editDeux: "",
          bgZero: "red",
          bgUn: "blue",
          bgDeux: "green",
          fgZero: "black",
          fgUn: "orange",
          fgDeux: "orange",
          uZero: true,
          uUn: false,
          uDeux: false,
          psZero: 10,
          psUn: 12,
          psDeux: 14
        },

      ]

    }
  }

  CasTest {
    name: "Tableau"
    testedNom: "qrc:/qml/page/Tableau.qml"
    params: {}
    /* beautify preserve:start */
    property var model
    property var underline: false
    property var pointSize: 12
    property var base: item
    property var un
    property var zero

    /* beautify preserve:end */

    function initPre() {
      model = createTemporaryObject(modelComp, item)
      params = {
        "model": model,
        "base": item,
      }
    }

    function initPreCreate() {}

    function initPost() {
      waitForRendering(tested, 3000)
      un = tested.getItem(1)
      zero = tested.getItem(0)
    }

    function test_init() {
      compare(un, tested.getItem(1))
      compare(model.rowCount * model.columnCount, 12)
    }

    function test_getCells() {
      var cells = tested.getCells()
      compare(cells.length, 12)
      var j = 0
      for (var i of cells) {
        compare(i.tinput.text, j.toString())
        j += 1
      }
    }

    function test_some_properties() {
      compare(tested.interactive, false)
      compare(tested.clip, true)
      compare(tested.with, item.with) //item == base
      compare(tested.size, 12)
      var total_height = 0
      compare(tested.visibleArea.heightRatio, 1)
    }

    function test_selected_state() {
      compare(Qt.colorEqual(un.color, "blue"), true)
      un.state = "selected"
      compare(Qt.colorEqual(un.color, "lightsteelblue"), true)
    }

    function test_delegate_edit_text() {
      var rec = tested.getItem(2)
      var tx = rec.tinput
      compare(tx.padding, 0)
      compare(tx.text, "2") // test le onCompleted

      var wi = rec.width
      tx.text = "234"
      compare(rec.width > wi, true) // // la colonne s'élargit
      compare(model.data(model.index(0, 2), "edit"), "234") // edit fait

      var he = rec.height
      tx.text = "\n"
      compare(rec.height > he, true) // // la colonnne 'élargit en hauteur
      compare(tested.visibleArea.heightRatio, 1) // // tout s'élargit en hauteur
    }

    function test_deplacement_curseur() {
      function testFocus(prev, next, key, modifier = Qt.ControlModifier) {
        tested.getItem(prev).tinput.forceActiveFocus()
        keyClick(key, modifier)
        compare(tested.getItem(next).tinput.focus, true, `prev: ${prev}, next: ${next}`)
        if (prev != next) {
          compare(tested.getItem(prev).tinput.focus, false, `prev: ${prev}, next: ${next}`)
        }
      }
      testFocus(1, 4, Qt.Key_Down)
      testFocus(4, 1, Qt.Key_Up)
      testFocus(1, 0, Qt.Key_Left)
      testFocus(0, 1, Qt.Key_Right)
      testFocus(10, 10, Qt.Key_Down)
      testFocus(1, 1, Qt.Key_Up)
      testFocus(2, 3, Qt.Key_Right)
      testFocus(11, 11, Qt.Key_Right)
      testFocus(0, 0, Qt.Key_Left)

      // cas en limite de case
      testFocus(1, 4, Qt.Key_Down, null)
      testFocus(4, 1, Qt.Key_Up, null)
      testFocus(1, 0, Qt.Key_Left, null)
      tested.getItem(0).tinput.cursorPosition = 1
      testFocus(0, 1, Qt.Key_Right, null)
      testFocus(10, 10, Qt.Key_Down, null)
      testFocus(1, 1, Qt.Key_Up, null)
      tested.getItem(2).tinput.cursorPosition = 1
      testFocus(2, 3, Qt.Key_Right, null)
      testFocus(11, 11, Qt.Key_Right, null)
      testFocus(0, 0, Qt.Key_Left, null)

      // test rien ne se passe si en milieuxe de text
      var ite = tested.getItem(4).tinput
      ite.text = "0123\n456\n789"
      ite.cursorPosition = 6
      testFocus(4, 4, Qt.Key_Down, null)
      testFocus(4, 4, Qt.Key_Up, null)
      testFocus(4, 4, Qt.Key_Left, null)
      testFocus(4, 4, Qt.Key_Right, null)

      // test ça marcjhe si en milieu de text
      var ite = tested.getItem(4).tinput
      ite.text = "0123\n456\n789"
      ite.cursorPosition = 6
      testFocus(4, 7, Qt.Key_Down)
      ite.cursorPosition = 6
      testFocus(4, 1, Qt.Key_Up)
      ite.cursorPosition = 6
      testFocus(4, 3, Qt.Key_Left)
      ite.cursorPosition = 6
      testFocus(4, 5, Qt.Key_Right)

    }

    function test_mouse_focus() {
      //test aussi left click
      mouseClick(un.tinput)
      compare(un.tinput.focus, true)
      un.tinput.text = "jiohuijokmojlikljomkpmojl"
      var quatre = tested.getItem(4)
      quatre.tinput.text = ""
      mouseClick(quatre)
      compare(quatre.tinput.focus, true)
      compare(un.tinput.focus, false)

    }

    function test_text_menu_style() {
      var un = tested.getItem(1)
      var tx = tested.getItem(1).tinput

      //click droit ur text
      compare(uiManager.menuTarget, undefined)
      mouseClick(tx, 1, 1, Qt.RightButton)
      compare(tx.focus, true)
      compare(uiManager.menuTarget, tx) //target is tx
      menuClick(uiManager.menuFlottantText, 1, 30)
      compare(Qt.colorEqual(tx.color, "red"), true)

      // sur un
      mouseClick(un, 1, 1, Qt.RightButton)
      compare(uiManager.menuTarget, tx) //target is tx
      menuClick(uiManager.menuFlottantText, 1, 30)
      compare(Qt.colorEqual(tx.color, "red"), true)

      //underline
      mouseClick(tx, 1, 1, Qt.RightButton)
      menuClick(uiManager.menuFlottantText, 1, 60)
      compare(Qt.colorEqual(tx.color, "red"), true)
      compare(tx.font.underline, true)
    }

    function test_text_bigeer_smaller() {
      var un = tested.getItem(1)
      var tx = tested.getItem(1).tinput

      tx.forceActiveFocus()
      keyPress(Qt.Key_A)
      keyPress(Qt.Key_A)
      keyPress(Qt.Key_A)
      keyPress(Qt.Key_A)
      compare(tx.font.pointSize, 12)
      keyClick(Qt.Key_Plus, Qt.ControlModifier)
      compare(tx.font.pointSize, 14)
      keyClick(Qt.Key_Minus, Qt.ControlModifier)
      compare(tx.font.pointSize, 12)

    }

    function selected(liste) {
      // renvoie une liste d'Item depres le index
      var res = []
      for (var i of liste) {
        res.push(tested.getItem(i))
      }
      return res
    }

    function mouseSelect(liste) {
      // reproduit press, moove, reles sur les items
      mousePress(tested.getItem(liste[0]), 0, 0)
      for (var x of liste) {
        mouseMove(tested.getItem(x), 1, 1)

      }
      var [last] = liste.slice(-1)
      mouseRelease(tested.getItem(last), 1, 1)
    }

    function test_mouseSelect(liste) {
      mouseSelect([1])
      compare(tested.selectedCells, [un])
    }

    function test_press_moove_release() {
      mousePress(un, 0, 0)
      mouseMove(un, 1, 1)
      mouseRelease(un, 1, 1)
      compare(tested.selectedCells, [un])
    }

    function test_select() {

      // simple vertical
      mouseSelect([1, 4, 7, 10])
      compare(tested.selectedCells, selected([1, 4, 7, 10]))
      for (var i of tested.selectedCells) {
        compare(i.state, "selected")
      }
      // unselect all called quand click simple
      mouseClick(un)
      compare(tested.selectedCells, [])
      for (var i of tested.getCells()) {
        compare(i.state, "")
      }
    }

    function test_new_select_invalid_l_ancien() {
      mouseSelect([1, 4, 7, 10])
      mouseSelect([0, 3, 6, 9])
      compare(tested.selectedCells, selected([0, 3, 6, 9]))
      for (var i of tested.selectedCells) {
        compare(i.state, "selected")
      }
    }

    //  test fail : cf : https://bugreports.qt.io/browse/QTBUG-83637
    //      tested.unSelectAll()
    //      // new select aec ctrl  n'invalid l'ancien
    //       mouseSelect([1,4,7,10])
    ////       mouseDrag(tested.getItem(1), un.width/2, un.height/2, 0,un.height*3 )
    //      mousePress(zero, zero.width/2, zero.height/2, Qt.LeftButton,   Qt.ControlModifier)
    //       mouseMove(zero, zero.width/2, zero.height/3, Qt.LeftButton)
    //       mouseRelease(zero, zero.width/2, zero.height/3, Qt.LeftButton,  Qt.ControlModifier)
    ////       mouseDrag(zero, zero.width/2, zero.height/2, 0,zero.height*1, Qt.LeftButton,  Qt.ControlModifier , -1)
    //       compare(tested.selectedCells, selected([1,4,7,10, 0]))
    //       for (var i of tested.selectedCells) {
    //        compare(i.state, "selected")
    //      }

    function test_selectect_avec_bouton_droit_sans_effet() {

      // boutton droit
      mousePress(un, un.width, un.height / 2, Qt.RightButton)
      mouseMove(un, un.width, un.height / 3)
      mouseRelease(un, un.width, un.height / 3, Qt.RightButton)
      compare(tested.selectedCells, [])
      //      mouseDrag(un, un.width/2, un.height/2, 0,un.height*3, Qt.RightButton )
    }

    function test_on_ne_rajoute_pas_item_dans_selected_quand_moove_si_deja_selected() {

      // on se déplace dans un élément déjà currentSelectedCell
      tested.currentSelectedCell = un
      mousePress(un, un.width, un.height / 2)
      mouseMove(un, un.width, un.height / 3)
      compare(tested.selectedCells, [])
      // uniquement isTableDelegate pas testé
    }

    function test_unselect_all_deselect_current_selected() {
      //      // unSelectAll deselect currentselected
      tested.currentSelectedCell = un
      tested.unSelectAll()
      compare(tested.currentSelectedCell, null)
    }

    function test_deselect_marche_arriere() {
      // marche arrière
      tested.unSelectAll()
      mousePress(un)
      mouseMove(un, un.width / 2, un.height / 2)
      mouseMove(zero, zero.width / 2, zero.height / 2)
      compare(tested.selectedCells, [un, zero])
      mouseMove(un, un.width / 2, un.height / 2)
      compare(tested.selectedCells, [un])
      mouseRelease(un) // au cas où
    }

    function test_menu_style_cellules() {
      var tx = un.tinput

      //click droit ur text
      compare(uiManager.menuTarget, undefined)
      mouseClick(tx, 1, 1, Qt.RightButton)
      compare(tx.focus, true)
      compare(uiManager.menuTarget, tx) //target is tx
      menuClick(uiManager.menuFlottantText, 1, 30)
      compare(Qt.colorEqual(tx.color, "red"), true)

      // sur un
      mouseClick(un, 1, 1, Qt.RightButton)
      compare(uiManager.menuTarget, tx) //target is tx
      menuClick(uiManager.menuFlottantText, 1, 30)
      compare(Qt.colorEqual(tx.color, "red"), true)

      //underline
      mouseClick(tx, 1, 1, Qt.RightButton)
      menuClick(uiManager.menuFlottantText, 1, 60)
      compare(Qt.colorEqual(tx.color, "red"), true)
      compare(tx.font.underline, true)
    }

    function test_style_from_selected() {
      var un = tested.getItem(1)
      var deux = tested.getItem(2)

      function select_un_et_deux_and_show_menu() {
        mousePress(un, 1, 1, Qt.LeftButton)
        mouseMove(un, 1, 1)
        mouseMove(deux, 1, 1)
        mouseRelease(un, 1, 1)
        mouseClick(un, 1, 1, Qt.RightButton)
      }

      // change bg color
      select_un_et_deux_and_show_menu()
      var red = menuGetItem(uiManager.menuFlottantTableau, 0, [0, 1, 0])
      mouseClick(red)
      // fail if not unselected when click
      compare(un.color, red.color)
      compare(deux.color, red.color)

      // change font color
      select_un_et_deux_and_show_menu()
      var bluefont = menuGetItem(uiManager.menuFlottantTableau, 3, [0, 1])
      mouseClick(bluefont)
      // fail if not unselected when click
      verify(Qt.colorEqual(bluefont.color, "blue"))
      compare(un.tinput.color, bluefont.color)
      compare(deux.tinput.color, bluefont.color)

      // change font color and underline
      select_un_et_deux_and_show_menu()
      var greenUnderLine = menuGetItem(uiManager.menuFlottantTableau, 5, [0, 2])
      mouseClick(greenUnderLine)
      // fail if not unselected when click
      verify(Qt.colorEqual(greenUnderLine.color, "green"))
      verify(Qt.colorEqual(greenUnderLine.color, "green"))
      compare(un.tinput.color, greenUnderLine.color)
      compare(deux.tinput.color, greenUnderLine.color)
      verify(un.tinput.font.underline)
      verify(deux.tinput.font.underline)
      //TODO: fix tests quand on peut mettre underline en role
    }

  }
}