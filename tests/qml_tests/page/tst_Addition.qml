import QtQuick 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/page/operations"
import ".."
import QtQml.Models 2.14

Item {
  id: item
  width: 200
  height: 300

  Component {
    id: ddbComp
    DdbMock {}
  }
Component {
    id: tempItemComp
    Rectangle {
      property TextInput textinput: input
      property QtObject model
      TextInput {
        id: input
        text: display
      }
    }
  }

  Component {
    id: testedComp
    Addition {
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }
  Component {
    id: testedCompDelegate
    AdditionDelegate {
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }

//  Component {
//    id: modelComp
//    QtObject {
//      property int rows: 4
//      property int columns: 3
//      property int cursor: 0
//      /* beautify preserve:start */
//      property var datas: ["", "", "", "", "", "9", "+", "", "8", "", "", ""]
//      /* beautify preserve:end */
//
//      function rowCount(parent) {return 7}
//      function data(index, role) {return datas[index]}
//
//      function isResultLine(index) {return _isResultLine}
//      property bool _isResultLine: false
//      function isRetenueLine(index) {return _isRetenueLine}
//      property bool _isRetenueLine: false
//      function isMiddleLine(index) {return _isMiddleLine}
//      property bool _isMiddleLine: false
//      function readOnly(index) {return _readOnly}
//      property bool _readOnly: false
//
//    }
//  }
  Component {
  id:modelComp
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
          listmodel.append({"display":x})
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

  TestCase {
    id: testcase
    name: "Addition"
    when: windowShown

    property Addition tested
    property DdbMock ddb
    property ListModel model
    //
    function init() {
      ddb = createTemporaryObject(ddbComp, item)
      model = createTemporaryObject(modelComp, item)
      tested = createTemporaryObject(testedComp, item, {
        'ddb': ddb,
        "model": model,
      })
    }

    function cleanup() {
      tested.destroy() //avoid warnings
    }

    function test_the_mock_model() {
      compare(model.count, 12)
      compare(tested.model.count, 12)
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


    function test_whole_usage_delegate() {
      // test : automovenext, onfocuschanged
      mouseClick(tested.itemAtIndex(11).textinput)
      compare(tested.currentItem.textinput.focus,true) // si pas fait
      keyClick(Qt.Key_5)
      compare(tested.itemAtIndex(11).textinput.text, "5")
      compare(tested.currentIndex,1)
      keyClick(Qt.Key_2)
      compare(tested.itemAtIndex(1).textinput.text, "2")
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

    function test_validator() {
      mouseClick(tested.itemAtIndex(11).textinput)
      keyClick(Qt.Key_A)
      compare(tested.currentItem.textinput.text, "")
      keyClick(Qt.Key_1)
      compare(tested.itemAtIndex(11).textinput.text, "1")
    }

    function test_move_with_arrows() {
    // on controle juste le call car fonction non refaite
      mouseClick(tested.itemAtIndex(11).textinput)
      keyClick(Qt.Key_Right)
      compare(model._moveCursor, [11, Qt.Key_Right])

    }

  }


}