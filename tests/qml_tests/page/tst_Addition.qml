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
    name: "Addition"
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



    function test_whole_usage_delegate() {
      // test : automovenext, onfocuschanged
      mouseClick(tested.itemAtIndex(11).textinput)
      compare(tested.currentItem.textinput.focus,true) // si pas fait
      keyClick(Qt.Key_5)
      compare(tested.itemAtIndex(11).textinput.text, "5")
      compare(model.get(11).edit, "5")
      compare(tested.currentIndex,1)
      keyClick(Qt.Key_2)
      compare(tested.itemAtIndex(1).textinput.text, "2")
      compare(model.get(1).edit, "2")
      compare(tested.currentIndex,10)
      keyClick(Qt.Key_3)
      compare(tested.currentItem.textinput.text, "3") //no automove after last


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