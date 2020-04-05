import QtQuick 2.14
import ".."

// baseoperation testé ici car addition très simple

Item {
  width: 200
  height: 200
  id: item

  Component {
  id: modelComp
  ListModel {
  id: listmodel
    property int rows: 4
    property int sectionId: 0
      property int columns: 3
      property int cursor: 0
      property int size: 12
      /* beautify preserve:start */
      property var datas: ["", "", "", "", "", "9", "+", "", "8", "", "", ""]
      /* beautify preserve:end */
      Component.onCompleted: {
        for (var x of datas){
          listmodel.append({"display":x, "edit":x})
        }
      }
      function isResultLine(index) {
      return [9,10,11].includes(index) ? true : false
      }
      function isRetenueLine(index) {
      return [0,1,2].includes(index) ? true : false
      }
      function isMiddleLine(index) {
      return [3,4,5,6,7,8].includes(index) ? true : false
      }
      function readOnly(index) {
      return [0,2,3,4,5,6,7,8,9].includes(index) ? true : false
      }
      property var _moveCursor
      function moveCursor(index, key) {
        _moveCursor =  [index, key]

         }
      function getInitialPosition() { return size-1}
        }
   }


  CasTest {
    name: "Addition"
    testedNom: "qrc:/qml/page/operations/Addition.qml"
    /* beautify preserve:start */
    property var model
    /* beautify preserve:end */

    function initPre() {
      model = createTemporaryObject(modelComp,item)
      params = {"model": model}
    }

    function initPost() {
    }

    function test_the_mock_model() {
      compare(model.count, 12)
      compare(tested.model,  model)
      }

        function test_init() {
      compare(tested.keyNavigationEnabled, false)
      compare(tested.width, 150)
      compare(tested.height, 200)
    }
        function test_cursor_binding() {
       model.cursor = 11
       compare(tested.currentIndex, 11)
    }

    function test_on_currentItemchanged() {
      tested.currentIndex = 1
      tested.currentIndex = 6
      compare(tested.currentItem.textinput.focus,true)

      //test no focus if input no exists, erreur dans les waringing du test
      tested.currentIndex = 999
  }
//
    function test_keys_and_validator() {
      var elem = tested.itemAtIndex(11).textinput
      var mod = model.get(11)
      mouseClick(elem)
      compare(mod.edit, "")

      //1 entier
      keyClick(Qt.Key_5)
      compare(mod.edit, "5")

      ///del et backspace
      keyClick(Qt.Key_Backspace)
      compare(mod.edit, "")
      keyClick(Qt.Key_5)
      compare(mod.edit, "5")
      keyClick(Qt.Key_Delete)
      compare(mod.edit, "")

      // validator refuse alphabet
      keyClick(Qt.Key_A)
      compare(mod.edit, "")

      //valiadator n'ademet qu'un chiffre
      keyClick(Qt.Key_5)
      compare(mod.edit, "5")
      keyClick(Qt.Key_5)
      compare(mod.edit, "5")

    }


     function test_move_with_arrows() {
    // on controle juste le call car fonction non refaite
      mouseClick(tested.itemAtIndex(11).textinput)
      keyClick(Qt.Key_Right)
      compare(model._moveCursor, [11, Qt.Key_Right])
      tested.destroy()

    }


    function test_edit() {
      // test : automovenext, onfocuschanged
      mouseClick(tested.itemAtIndex(11).textinput)
      compare(tested.currentItem.textinput.focus,true) // si pas fait
      keyClick(Qt.Key_5)
      compare(model.get(11).edit, "5")
    }

    function test_properties() {
      compare(tested.itemAtIndex(0).textinput.bottomPadding,0)
      compare(tested.itemAtIndex(3).textinput.bottomPadding,5)
      compare(tested.itemAtIndex(11).textinput.bottomPadding,5)
      compare(tested.itemAtIndex(0).textinput.topPadding,5)
      compare(tested.itemAtIndex(3).textinput.topPadding,0)
      compare(tested.itemAtIndex(11).textinput.topPadding,5)
      compare(tested.itemAtIndex(0).textinput.color,"#ff0000") //Red
      compare(tested.itemAtIndex(3).textinput.color,"#000000") //black
      compare(tested.itemAtIndex(11).textinput.color,"#000000")
      compare(tested.itemAtIndex(0).textinput.horizontalAlignment,TextInput.AlignHCenter)
      compare(tested.itemAtIndex(3).textinput.horizontalAlignment,TextInput.AlignHCenter)
      compare(tested.itemAtIndex(11).textinput.horizontalAlignment,TextInput.AlignHCenter)
      compare(tested.itemAtIndex(0).textinput.verticalAlignment,TextInput.AlignBottom)
      compare(tested.itemAtIndex(3).textinput.verticalAlignment,TextInput.AlignTop)
      compare(tested.itemAtIndex(11).textinput.verticalAlignment,TextInput.AlignVCenter)
      compare(tested.itemAtIndex(0).textinput.readOnly,true)
      compare(tested.itemAtIndex(3).textinput.readOnly,true)
      compare(tested.itemAtIndex(11).textinput.readOnly,false)
      compare(tested.itemAtIndex(0).textinput.background.borderColor,"#ffffff")// root color
      compare(tested.itemAtIndex(3).textinput.background.borderColor,"#ffffff")
      compare(tested.itemAtIndex(11).textinput.background.borderColor,"#000000") //black

    }



  }


}