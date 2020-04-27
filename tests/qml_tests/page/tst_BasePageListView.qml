import QtQuick 2.14
import QtTest 1.14
import ".."

Item {
  id: item
  width: 200
  height: 300

  Component {
    id: modelComp
    ListModel {
      signal rowsInserted(int index, int row, int col)
      signal modelReset()
      property int lastPosition: 0
      id: listmodel
      Component.onCompleted: {
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
      }
    }

  }

  CasTest {
    name: "BasePageListView"
    testedNom: "qrc:/qml/page/BasePageListView.qml"
    property ListModel listmodel

    function initPre() {
      listmodel = createTemporaryObject(modelComp, item)
      params = {
        'model': listmodel
      }
    }

    function initPost() {}

    //    function test_init() {
    //      compare(tested.clip, true)
    //      compare(tested.highlightMoveDuration, -1)
    //      compare(tested.boundsBehavior, Flickable.DragOverBounds)
    //
    //      compare(tested.currentIndex, 0)
    //    }
    //
    //    function test_currentindex_bind_last_position() {
    //      compare(tested.currentIndex, 0)
    //      listmodel.lastPosition = 4
    //      compare(tested.currentIndex, 4)
    //    }

  }
}