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
  Component {
    id: modelComp
    ListModel {
      signal rowsInserted(int index, int row, int col)
      signal modelReset()
      property int lastPosition: 0
    }
  }

  TestCase {
    id: testcase
    name: "BasePageListView"
    when: windowShown

    property BasePageListView tested
    property DdbMock ddb
    property ListModel listmodel
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



      listmodel = createTemporaryObject(modelComp, item, {
        'ddb': ddb,
        'model': listmodel
      })
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
      compare(tested.highlightMoveDuration,  -1)
      compare(tested.boundsBehavior,  Flickable.DragOverBounds)

      compare(tested.currentIndex, 0)
    }

    function test_currentindex_bind_last_position () {
    // ignore warn : Error: Invalid write to global property "currentIndex"
      compare(tested.currentIndex, 0)
    tested.model.lastPosition = 32
      compare(tested.currentIndex, 32)
    }


  }
}