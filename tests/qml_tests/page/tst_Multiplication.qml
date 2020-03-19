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
      return _.range(36, 48).includes(index) ? true : false
      }
      function readOnly(index) {
      var r = [35, 16, 34, 15, 33, 32, 41, 40, 10, 39, 9, 38, 37, 47, 46, 45, 4, 44, 3, 43, 59, 52, 58, 51, 57, 50, 56, 49, 55]
      return r.includes(index) ? false : true
      }



      property var _moveCursor
      function moveCursor(index, key) {
        _moveCursor =  [index, key]

         }
      function autoMoveNext(index) {
      var tab = {'35':16,'16':34,'34':15,'15':33,'33':32,'32':41,'41':40,'40':10,'10':39,'39':9,'9':38,'38':37,'37':47,'47':46,'46':45,'45':4,'4':44,'44':3,'3':43,'43':59,'59':52,'52':58,'58':51,'51':57,'57':50,'50':56,'56':49,'49':55,'55':55}
        cursor=tab[index]
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


//    function test_whole_usage_delegate() {
//      // test : automovenext, onfocuschanged
//      var auto = [[14, 30], [30, 49], [49, 11], [11, 26], [26, 46], [46, 7], [7, 23], [23, 42], [42, 4], [4, 20], [20, 39], [39, 36]]
//
//      mouseClick(tested.itemAtIndex(14).textinput)
//      compare(tested.currentItem.textinput.focus,true) // si pas fait
//
//      var i = 0
//      for (var x of auto) {
//        var index = _.sample(_.range(5))
//        var touche = [Qt.Key_0,Qt.Key_1,Qt.Key_2,Qt.Key_3,Qt.Key_4][index]
//        keyClick(touche)
//        compare(tested.itemAtIndex(x[0]).textinput.text, index.toString())
//        compare(model.get(x[0]).edit, index.toString())
//        compare(tested.currentIndex,auto[i][1])
//        i++
//        }
//        keyClick(Qt.Key_3)//no automove after last
//        compare(tested.currentIndex,36) //no automove after last
//      }

    function test_properties() {

      compare(tested.itemAtIndex(4).textinput.color,"#ff0000") //Red
      compare(tested.itemAtIndex(20).textinput.color,"#000000") //black
      compare(tested.itemAtIndex(52).textinput.color,"#ff0000") //Red
      compare(tested.itemAtIndex(56).textinput.color,"#000000") //black

//      compare(tested.itemAtIndex(0).textinput.horizontalAlignment,TextInput.AlignHCenter)
//      compare(tested.itemAtIndex(20).textinput.horizontalAlignment,TextInput.AlignLeft)
//      compare(tested.itemAtIndex(4).textinput.horizontalAlignment,TextInput.AlignRight)
//
//      compare(tested.itemAtIndex(0).textinput.verticalAlignment,TextInput.AlignVCenter)
//      compare(tested.itemAtIndex(20).textinput.verticalAlignment,TextInput.AlignVCenter)
//      compare(tested.itemAtIndex(4).textinput.verticalAlignment,TextInput.AlignVCenter)
//
//      compare(tested.itemAtIndex(0).textinput.readOnly,true)
//      compare(tested.itemAtIndex(20).textinput.readOnly,false)
//      compare(tested.itemAtIndex(4).textinput.readOnly,false)
//
//      compare(tested.itemAtIndex(5).textinput.background.borderColor,"#ffffff")// root color
//      compare(tested.itemAtIndex(25).textinput.background.borderColor,"#ffffff")
//      compare(tested.itemAtIndex(35).textinput.background.borderColor,"#000000") //black

    }


  }


}