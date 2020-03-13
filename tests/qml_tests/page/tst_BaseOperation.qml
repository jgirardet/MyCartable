import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  Component {
  id: modelComp
  ListModel {
  id: listmodel
    property int rows: 4
      property int columns: 3
      property int cursor: 0
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
      function autoMoveNext(index) {
        switch (index) {
            case 1: {
            cursor=10;
            break;
            }
            case 11: {
            cursor=1;
            break;
            }
          };
        }
        }
   }


  CasTest {
    name: "BaseOperation"
    testedNom: "qrc:/qml/page/operations/BaseOperation.qml"
    /* beautify preserve:start */
    property var model
    /* beautify preserve:end */

    function initPre() {
      model = createTemporaryObject(modelComp,item)
      params = {"model": model, "delegateClass": "addition"}
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
      compare(tested.currentItem.textinput.text,"+")
      compare(tested.currentItem.textinput.focus,true)
  }
//
//  function test_validator() {
//      mouseClick(tested.itemAtIndex(11).textinput)
//      keyClick(Qt.Key_A)
//      compare(tested.currentItem.textinput.text, "")
//      keyClick(Qt.Key_1)
//      compare(tested.itemAtIndex(11).textinput.text, "1")
//    }
//
//    function test_move_with_arrows() {
//    // on controle juste le call car fonction non refaite
//      mouseClick(tested.itemAtIndex(11).textinput)
//      keyClick(Qt.Key_Right)
//      compare(model._moveCursor, [11, Qt.Key_Right])
//      tested.destroy()
//
//    }





  }


}