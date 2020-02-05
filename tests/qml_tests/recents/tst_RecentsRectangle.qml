import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/recents"
import ".."
Item {
  id: item
  width: 200
  height: 300

  Component {
    id: ddbcomp
    DdbMock {}
  }

  Component {
    id: testedcomp
    RecentsRectangle {
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }

  //
  TestCase {
    id: testcase
    name: "RecentsRectangle";when: windowShown
    property RecentsRectangle tested: null
    property DdbMock ddb: null
    property RecentsListView lv
    //
    function init() {
      ddb = createTemporaryObject(ddbcomp, item)
      verify(ddb)
      //ddb.recentsModel = ddb.sp.recentsModel
      tested = createTemporaryObject(testedcomp, item, {
        'ddb': ddb
      })
      lv = findChild(tested, "recentsListView")
    }

    function cleanup() {
      if (tested) {
        tested.destroy()
      }
    }

    function test_init() {
      compare(ddb.sp.recentsModel, lv.model)
    }

    function test_item_click() {
      mouseClick(lv)
      compare(ddb._recentsItemClicked, [1, 1])
    }
  }
}