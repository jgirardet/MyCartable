import QtQuick 2.14
import ".."
import "qrc:/js/lodash.js" as Lodash

Item {
  width: 600
  height: 600
  id: item



  Component {
  id: modelComp
  ListModel {
  id: listmodel
      property int rows: 10
      property int columns: 6
      property int cursor: 0
      property int sectionId: 0
      property int size: 60
      property int virgule: 0
      /* beautify preserve:start */
      property var datas: ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '2', '5', '1', 'x', '', '', '1', '4', '8', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
      /* beautify preserve:end */
      Component.onCompleted: {
        for (var x of datas){
          listmodel.append({"display":x, "edit":x})
        }
      }
      function isResultLine(index) {
      return _.range(34, 51).includes(index) ? true : false
      }
      function isRetenueLine(index) {
      return _.range(18).includes(index) ||  _.range(48,54).includes(index) ? true : false
      }
      function isMiddleLine(index) {
      return _.range(18, 48).includes(index) ? true : false
      }
      function isMembreLine(index) {
      return _.range(18, 30).includes(index) ? true : false
      }
      function isLine1(index) {
      return _.range(18, 24).includes(index) ? true : false
      }
      function readOnly(index) {
      var r = [35, 16, 34, 15, 33, 32, 41, 40, 10, 39, 9, 38, 37, 47, 46, 45, 4, 44, 3, 43, 59, 52, 58, 51, 57, 50, 56, 49, 55]
      return r.includes(index) ? false : true
      }
      function getInitialPosition() { return size-1}



      property var _moveCursor
      function moveCursor(index, key) {
        _moveCursor =  [index, key]

         }
   }
   }


  CasTest {
    name: "Multiplication"
    testedNom: "qrc:/qml/page/operations/Multiplication.qml"
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
      compare(model.count, model.size)
      compare(tested.model,  model)
     }

    function test_edit() {

      mouseClick(tested.itemAtIndex(52).textinput)
      compare(tested.currentItem.textinput.focus,true) // si pas fait)
      keyClick(Qt.Key_5)
      compare(tested.itemAtIndex(52).textinput.text, "5")
      compare(model.get(52).edit, "5")
      keyClick(Qt.Key_Comma)
      compare(tested.itemAtIndex(52).textinput.text, "5,")
      compare(model.get(52).edit, "5,")
   }


        function test_properties() {

          compare(tested.itemAtIndex(4).textinput.color,"#ff0000") //Red
          compare(tested.itemAtIndex(20).textinput.color,"#008000") //green
          compare(tested.itemAtIndex(52).textinput.color,"#ff0000") //Red
          compare(tested.itemAtIndex(56).textinput.color,"#000000") //black

      compare(tested.itemAtIndex(4).textinput.horizontalAlignment,TextInput.AlignHCenter)
      compare(tested.itemAtIndex(20).textinput.horizontalAlignment,TextInput.AlignHCenter)
      compare(tested.itemAtIndex(52).textinput.horizontalAlignment,TextInput.AlignHCenter)
      compare(tested.itemAtIndex(56).textinput.horizontalAlignment,TextInput.AlignHCenter)

      compare(tested.itemAtIndex(4).textinput.verticalAlignment,TextInput.AlignVCenter)
      compare(tested.itemAtIndex(20).textinput.verticalAlignment,TextInput.AlignVCenter)
      compare(tested.itemAtIndex(52).textinput.verticalAlignment,TextInput.AlignVCenter)
      compare(tested.itemAtIndex(56).textinput.verticalAlignment,TextInput.AlignVCenter)
//
      //validator
      }
      function test_validator() {
      var elem = tested.itemAtIndex(52).textinput
      mouseClick(elem)
      keyClick(Qt.Key_A)
      compare(elem.text, "")
      keyClick(Qt.Key_5)
      compare(elem.text, "5")
      keyClick(Qt.Key_Comma)
      compare(elem.text, "5,")
      keyClick(Qt.Key_Backspace)
      compare(elem.text, "5")
      keyClick(Qt.Key_Backspace)
      compare(elem.text, "")
      keyClick(Qt.Key_Comma)
      compare(elem.text, "")
      keyClick(Qt.Key_A)
      compare(elem.text, "")
      keyClick(Qt.Key_6)
      compare(elem.text, "6")
      keyClick(Qt.Key_6)
      compare(elem.text, "6")

    }
//

  }


}