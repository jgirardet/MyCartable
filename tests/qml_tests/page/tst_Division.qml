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
      property int rows: 5
      property int columns: 9
      property int cursor: 0
      property int sectionId: 0
      property int size: 45
      property int virgule: 0
      property int diviseur: 11
      property real dividende: 264
      property string quotient: ""

      /* beautify preserve:start */
      property var datas: ['', '2', '', '', '6', '', '', '4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
      /* beautify preserve:end */
      Component.onCompleted: {
        for (var x of datas){
          listmodel.append({"display":x, "edit":x})
        }
      }
//      function isResultLine(index) {
//      return false
//      }
//      function isRetenueLine(index) {
//      return false
//      }
//      function isMiddleLine(index) {
//      return true
//      }
      function isDividendeLine(index) {
      return _.range(0, 9).includes(index) ? true : false
      }
      function isMembreLine(index) {
      return Math.floor(index / columns) & 1 ? true : false
      }
      function isRetenue(index) {
      return [11, 3, 6, 14, 21, 24, 29, 32].includes(index) ? true : false
      }
      function isRetenueGauche(index) {
      return [ 3, 6,  21, 24].includes(index) ? true : false
      }
      function isRetenueDroite(index) {
      return [ 11, 14,  29, 32].includes(index) ? true : false
      }
      function readOnly(index) {
      var r = [3, 6, 10, 11, 13, 14, 16, 17, 18, 19, 21, 22, 24, 25, 28, 29, 31, 32, 34, 35, 37, 40, 43]
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
    name: "Division"
    testedNom: "qrc:/qml/page/operations/Division.qml"
    /* beautify preserve:start */
    property var model
    property var quotient
    property var corps
    /* beautify preserve:end */

    function initPre() {
      model = createTemporaryObject(modelComp,item)
      params = {"model": model}
    }

    function initPost() {
      quotient = findChild(tested, "quotientField")
      corps = findChild(tested, "corps")
    }

    function test_the_mock_model() {
      compare(model.count, model.size)
      compare(tested.model,  model)
     }

     function test_focus_from_operation_to_quotient_and_back() {
        quotient.forceActiveFocus()
        compare(corps.focus, false)
        compare(quotient.focus, true)
        keyClick(Qt.Key_Return)
        compare(corps.focus, true)
        compare(quotient.focus, false)
        keyClick(Qt.Key_Return)
        compare(corps.focus, false)
        compare(quotient.focus, true)
     }
//
//    function test_edit() {
//
//      mouseClick(tested.itemAtIndex(52).textinput)
//      compare(tested.currentItem.textinput.focus,true) // si pas fait)
//      keyClick(Qt.Key_5)
//      compare(tested.itemAtIndex(52).textinput.text, "5")
//      compare(model.get(52).edit, "5")
//      keyClick(Qt.Key_Comma)
//      compare(tested.itemAtIndex(52).textinput.text, "5,")
//      compare(model.get(52).edit, "5,")
//   }
//
//
        function test_properties() {
//        //1,10 (text) et 11 retenu droit,  21 : retenue gauche
          compare(corps.itemAtIndex(1).textinput.color,"#000000") //black
          compare(corps.itemAtIndex(10).textinput.color,"#000000") //black
          compare(corps.itemAtIndex(11).textinput.color,"#ff0000") //Red
          compare(corps.itemAtIndex(21).textinput.color,"#ff0000") //Red

      compare(corps.itemAtIndex(1).textinput.horizontalAlignment,TextInput.AlignHCenter)
      compare(corps.itemAtIndex(10).textinput.horizontalAlignment,TextInput.AlignHCenter)
      compare(corps.itemAtIndex(11).textinput.horizontalAlignment,TextInput.AlignLeft)
      compare(corps.itemAtIndex(21).textinput.horizontalAlignment,TextInput.AlignRight)

      compare(corps.itemAtIndex(1).textinput.verticalAlignment,TextInput.AlignVCenter)
      compare(corps.itemAtIndex(10).textinput.verticalAlignment,TextInput.AlignVCenter)
      compare(corps.itemAtIndex(11).textinput.verticalAlignment,TextInput.AlignVCenter)
      compare(corps.itemAtIndex(21).textinput.verticalAlignment,TextInput.AlignVCenter)
//
      }
      function test_validator() {
      var elem = quotient
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