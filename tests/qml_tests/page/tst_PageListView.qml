import QtQuick 2.12
import QtTest 1.12
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
    PageListView {
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }
  ListModel {
    id: listmodel
    //    ListElement {
    //        display: {lid:25} //{"id":25, "classtype":"ImageSection"}
    //    }
    //    ListElement {
    //        display: {"id":32, "classtype":"ImageSection"}
    //    }
    //    ListElement {
    //        display: {"id":64, "classtype":"ImageSection"}
    //    }
    //    ListElement {
    //        display: {"id":89, "classtype":"ImageSection"}
    //    }
    //    ListElement {
    //        display: {"id":100, "classtype":"ImageSection"}
    //    }
    //    ListElement {
    //        display: {"id":200, "classtype":"ImageSection"}
    //    }
  }

  TestCase {
    id: testcase
    name: "PageListView"
    when: windowShown

    property PageListView tested
    property DdbMock ddb
    //
    function init() {
      ddb = createTemporaryObject(ddbComp, item)

      var listData = [{
        "display": {
          "id": 34,
          "classtype": "ImageAnnotation"
        }
      }, {
        "display": {
          "id": 45,
          "classtype": "Stabylo"
        }
      }, {
        "display": {
          "id": 99,
          "classtype": "ImageAnnotation"
        }
      }, {
        "display": {
          "id": 102,
          "classtype": "ImageAnnotation"
        }
      }, {
        "display": {
          "id": 300,
          "classtype": "ImageAnnotation"
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
    }

    function test_model() {
      tested.currentIndex = 0
      tested.currentIndex =1
      compare(tested.currentItem.curSectionId, 45)
//      print(tested.contentItem.children[0].item)
//      compare(Object.keys(tested.contentItem.children[1]), 45)
    }

  }
}