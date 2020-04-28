import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  CasTest {
    name: "RecentsRectangle"
    testedNom: "qrc:/qml/recents/RecentsRectangle.qml"
    params: {}

    function test_init() {
      compare(ddb.recentsModel, tested.listview.model)
    }

    function test_item_click() {
      signalChecker(ddb, "recentsItemClicked", "mouseClick(tested.listview)", [23, 13])
    }
    //    function test_color() {
    ////      mouseClick(tested.listview)
    ////      ddb.recentsModel[0].matiereBgColor = "red"
    //      var un = tested.listview.itemAtIndex(0)
    //      compare(un.background.color, "red")
    //    }
  }
}