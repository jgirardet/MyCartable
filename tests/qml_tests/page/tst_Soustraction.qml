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
    property int rows: 4
      property int columns: 17
      property int cursor: 0
      property int sectionId: 0
      property int size: 40
      /* beautify preserve:start */
      property var datas: ['',  '', '4', '', '', '3', '', '', '2', '', ',' ,'', '5', '', '', '4', '', '-', '', '3', '', '', '9', '', '', '1', '', ',' ,'', '4', '', '', '1', '', '',  '', '' , '', '', '' , '', '', '' , '', ',', '', '',  '', '', '' , '']
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
      return _.range(17).includes(index) ? true : false
      }
      function isMiddleLine(index) {
      return _.range(17, 34).includes(index) ? true : false
      }
      function readOnly(index) {
      return [4, 36, 7, 39, 42, 11, 14, 46, 49, 20, 23, 26, 30].includes(index) ? false : true
      }
      property var _moveCursor
      function moveCursor(index, key) {
        _moveCursor =  [index, key]

         }
      function autoMoveNext(index) {
        var tab = {'14':30,'30':49,'49':11,'11':26,'26':46,'46':7,'7':23,'23':42,'42':4,'4':20,'20':39,'39':36,'36':36}
        cursor=tab[index]
        }

       function isRetenueDroit(index) {
       return [20, 23, 26, 30].includes(index)
       }

       function isRetenueGauche(index) {
       return [4, 7, 11, 14].includes(index)
       }
       function getInitialPosition() { return size-1}
   }
   }


  CasTest {
    name: "Soustraction"
    testedNom: "qrc:/qml/page/operations/Soustraction.qml"
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
      compare(model.count, 51)
      compare(tested.model,  model)
     }


    function test_edit() {
      // test : automovenext, onfocuschanged

      mouseClick(tested.itemAtIndex(14).textinput)
      compare(tested.currentItem.textinput.focus,true) // si pas fait
      keyClick(Qt.Key_5)
      compare(tested.itemAtIndex(14).textinput.text, "5")
      compare(model.get(14).edit, "5")
  }

    function test_properties() {
      //retenu droite{20, 23, 26, 30}
      compare(tested.itemAtIndex(0).textinput.leftPadding,5)
      compare(tested.itemAtIndex(20).textinput.leftPadding,0)
      // "Gauche", {4, 7, 11, 14}
      compare(tested.itemAtIndex(0).textinput.rightPadding,5)
      compare(tested.itemAtIndex(4).textinput.rightPadding,1)

      compare(tested.itemAtIndex(0).textinput.color,"#000000") //black
      compare(tested.itemAtIndex(20).textinput.color,"#ff0000") //Red
      compare(tested.itemAtIndex(4).textinput.color,"#ff0000") //Red

      compare(tested.itemAtIndex(0).textinput.horizontalAlignment,TextInput.AlignHCenter)
      compare(tested.itemAtIndex(20).textinput.horizontalAlignment,TextInput.AlignLeft)
      compare(tested.itemAtIndex(4).textinput.horizontalAlignment,TextInput.AlignRight)

      compare(tested.itemAtIndex(0).textinput.verticalAlignment,TextInput.AlignVCenter)
      compare(tested.itemAtIndex(20).textinput.verticalAlignment,TextInput.AlignVCenter)
      compare(tested.itemAtIndex(4).textinput.verticalAlignment,TextInput.AlignVCenter)

      compare(tested.itemAtIndex(0).textinput.readOnly,true)
      compare(tested.itemAtIndex(20).textinput.readOnly,false)
      compare(tested.itemAtIndex(4).textinput.readOnly,false)

      compare(tested.itemAtIndex(5).textinput.background.borderColor,"#ffffff")// root color
      compare(tested.itemAtIndex(25).textinput.background.borderColor,"#ffffff")
      compare(tested.itemAtIndex(35).textinput.background.borderColor,"#000000") //black

    }


  }


}