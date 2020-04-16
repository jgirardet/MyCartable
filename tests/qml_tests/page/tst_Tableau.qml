import QtQuick 2.14
import ".."
 import Qt.labs.qmlmodels 1.0

Item {
  width: 400
  height: 400
  id: item

  Component {
    id: modelComp
    TableModel {

            property int n_rows: rowCount

            TableModelColumn { display: "zero";edit: "zero" }
            TableModelColumn { display: "un" ;edit: "zero"}
            TableModelColumn { display: "deux" ;edit: "zero"}

            // Each row is one type of fruit that can be ordered
            rows: [
                {             // les indices dans tested
                  zero: "0", //0 ?????
                  un: "1", //6
                  deux: "2" //7
                },
                {
                  zero: "3", //8
                  un: "4", //9
                  deux: "5" //10
                },
                {
                  zero: "6", //11
                  un: "7",  //12
                  deux: "8"  //13
                },
                {
                  zero: "9", //14
                  un: "10", //15
                  deux: "11" //16
                }
                ]


    }
  }

  CasTest {
    name: "Tableau"
    testedNom: "qrc:/qml/page/Tableau.qml"
    params: {}
    /* beautify preserve:start */
    property var model
    /* beautify preserve:end */

    function initPre() {
      model = createTemporaryObject(modelComp, item)
      params = {
        "model": model,
        "base":item,
      }
    }

    function initPreCreate() {}

    function initPost() {
    waitForRendering(tested, 3000)
    }

    function test_init() {
      compare(model.rowCount*model.columnCount, 12)
    }

    function test_getItem() {
    //test aussi contentY pour le bug d'affichage
    // test aussi getRowCol
      for (const i of Array(12).keys()) {
       var tt = tested.getItem(i)
//       print(tt.tinput.text, i)
       compare(tt.tinput.text, i.toString())
        }
      }

    function test_some_properties() {
      compare(tested.interactive, false)
      compare(tested.clip, true)
      compare(tested.with, item.with) //item == base
      compare(tested.size, 12)
      var total_height = 0
      compare(tested.visibleArea.heightRatio,1)
    }

    function test_delegate_edit_text() {
      var rec = tested.getItem(2)
      var tx = rec.tinput
      compare(tx.padding, 0)
      compare(tx.text, "2") // test le onCompleted

      var wi = rec.width
      tx.text = "234"
      compare(rec.width>wi,true ) // // la colonne s'élargit
      compare(model.data(model.index(0,2), "edit"), "234") // edit fait

      var he = rec.height
      tx.text = "\n"
      compare(rec.height>he,true ) // // la colonnne 'élargit en hauteur
      compare(tested.visibleArea.heightRatio,1 ) // // tout s'élargit en hauteur
    }


    function test_deplacement_curseur() {
        function testFocus(prev, next, key, modifier=Qt.ControlModifier ) {
        tested.getItem(prev).tinput.forceActiveFocus()
        keyClick(key, modifier)
        compare(tested.getItem(next).tinput.focus, true, `prev: ${prev}, next: ${next}`)
        if (prev != next){
        compare(tested.getItem(prev).tinput.focus, false, `prev: ${prev}, next: ${next}`)
          }
        }
        testFocus(1,4, Qt.Key_Down)
        testFocus(4,1, Qt.Key_Up)
        testFocus(1,0, Qt.Key_Left)
        testFocus(0,1, Qt.Key_Right)
        testFocus(10,10, Qt.Key_Down)
        testFocus(1,1, Qt.Key_Up)
        testFocus(2,3, Qt.Key_Right)
        testFocus(11,11, Qt.Key_Right)
        testFocus(0,0, Qt.Key_Left)

        // cas en limite de case
        testFocus(1,4, Qt.Key_Down, null)
        testFocus(4,1, Qt.Key_Up, null)
        testFocus(1,0, Qt.Key_Left, null)
        tested.getItem(0).tinput.cursorPosition = 1
        testFocus(0,1, Qt.Key_Right, null)
        testFocus(10,10, Qt.Key_Down, null)
        testFocus(1,1, Qt.Key_Up, null)
        tested.getItem(2).tinput.cursorPosition = 1
        testFocus(2,3, Qt.Key_Right, null)
        testFocus(11,11, Qt.Key_Right, null)
        testFocus(0,0, Qt.Key_Left, null)

        // test rien ne se passe si en milieuxe de text
        var ite = tested.getItem(4).tinput
        ite.text = "0123\n456\n789"
        ite.cursorPosition = 6
        testFocus(4,4, Qt.Key_Down, null)
        testFocus(4,4, Qt.Key_Up, null)
        testFocus(4,4, Qt.Key_Left, null)
        testFocus(4,4, Qt.Key_Right, null)

        // test ça marcjhe si en milieu de text
        var ite = tested.getItem(4).tinput
        ite.text = "0123\n456\n789"
        ite.cursorPosition = 6
        testFocus(4,7, Qt.Key_Down)
        ite.cursorPosition = 6
        testFocus(4,1, Qt.Key_Up)
        ite.cursorPosition = 6
        testFocus(4,3, Qt.Key_Left)
        ite.cursorPosition = 6
        testFocus(4,5, Qt.Key_Right)

    }


    function test_mouse_focus() {
    //test aussi left click
      var un = tested.getItem(1)
      mouseClick(un.tinput)
      compare(un.tinput.focus, true)
      un.tinput.text="jiohuijokmojlikljomkpmojl"
      var quatre = tested.getItem(4)
      quatre.tinput.text=""
      mouseClick(quatre)
      compare(quatre.tinput.focus, true)
      compare(un.tinput.focus, false)

    }


    function test_text_menu_style() {
        var rec = tested.getItem(1)
        var tx = tested.getItem(1).tinput

        //click droit ur text
        compare(uiManager.menuTarget, undefined)
        mouseClick(tx, 1,1,Qt.RightButton)
        compare(tx.focus, true)
        compare(uiManager.menuTarget, tx) //target is tx
        menuClick(uiManager.menuFlottantText, 1, 30)
        compare(Qt.colorEqual(tx.color, "red"), true)

        // sur rec
        mouseClick(rec, 1,1,Qt.RightButton)
        compare(uiManager.menuTarget, tx) //target is tx
        menuClick(uiManager.menuFlottantText, 1, 30)
        compare(Qt.colorEqual(tx.color, "red"), true)

        //underline
        mouseClick(tx, 1,1,Qt.RightButton)
        menuClick(uiManager.menuFlottantText, 1, 60)
        compare(Qt.colorEqual(tx.color, "red"), true)
        compare(tx.font.underline, true)
    }

//    function test_menu_style_cellules() {
//        var rec = tested.getItem(1)
////        var tx = tested.getItem(1).tinput
//
//        //click droit ur text
//        compare(uiManager.menuTarget, undefined)
//        mouseClick(tx, 1,1,Qt.RightButton)
//        compare(tx.focus, true)
//        compare(uiManager.menuTarget, tx) //target is tx
//        menuClick(uiManager.menuFlottantText, 1, 30)
//        compare(Qt.colorEqual(tx.color, "red"), true)
//
//        // sur rec
//        mouseClick(rec, 1,1,Qt.RightButton)
//        compare(uiManager.menuTarget, tx) //target is tx
//        menuClick(uiManager.menuFlottantText, 1, 30)
//        compare(Qt.colorEqual(tx.color, "red"), true)
//
//        //underline
//        mouseClick(tx, 1,1,Qt.RightButton)
//        menuClick(uiManager.menuFlottantText, 1, 60)
//        compare(Qt.colorEqual(tx.color, "red"), true)
//        compare(tx.font.underline, true)
//    }
  }
}