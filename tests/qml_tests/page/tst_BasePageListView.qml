import QtQuick 2.14
import QtTest 1.14
import "../../../src/main/resources/base/qml/page"
import ".."

Item {
  id: item
  width: 200
  height: 300

  Component {
    id: ddbComp
    DdbMock {}
  }

  Component {
    id: testedComp
    BasePageListView {
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }
  ListModel {
    id: listmodel
    signal rowsInserted(int index, int row, int col)
    signal modelReset()
  }

  TestCase {
    id: testcase
    name: "BasePageListView"
    when: windowShown

    property BasePageListView tested
    property DdbMock ddb
    //
    function init() {
      ddb = createTemporaryObject(ddbComp, item)

      var listData = [{
        "page": {
          "id": 34,
          "classtype": "TextSection"
        }
      }, {
        "page": {
          "id": 45,
          "classtype": "TextSection"
        }
      }, {
        "page": {
          "id": 99,
          "classtype": "ImageSection"
        }
      }, {
        "page": {
          "id": 102,
          "classtype": "ImageSection"
        }
      }, {
        "page": {
          "id": 300,
          "classtype": "TextSection"
        }
      }, ]

      for (var x of listData) {
        listmodel.append(x)
      }

      tested = createTemporaryObject(testedComp, item, {
        'ddb': ddb,
        'model': listmodel
      })
    }

    function cleanup() {}

    function test_init() {
      compare(tested.clip, true)
      compare(tested.highlightMoveDuration,  1000)
      compare(tested.highlightMoveVelocity,  -1)
      compare(tested.boundsBehavior,  Flickable.DragOverBounds)

      compare(tested.currentIndex, 0)
    }


    function test_onInsertRow() {
      // ignore warn  : Error: Invalid write to global property "currentIndex"
      tested.model.rowsInserted(0,123, 0)
      compare(tested.currentIndex, 123)
    }

    function test_reset() {
    // ignore warn : Error: Invalid write to global property "currentIndex"
      tested.currentIndex = 23
      tested.model.modelReset()
      compare(tested.currentIndex, 0)
    }

//    function test_model() {
//      tested.currentIndex = 0
//      tested.currentIndex =1
//      compare(tested.currentItem.curSectionId, 45)
////      print(tested.contentItem.children[0].item)
////      compare(Object.keys(tested.contentItem.children[1]), 45)
//    }

  }
}