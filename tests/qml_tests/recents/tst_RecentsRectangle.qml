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
      compare(ddb.sp.recentsModel, tested.listview.model)
    }

    function test_item_click() {
      mouseClick(tested.listview)
      compare(ddb._recentsItemClicked, [1, 1])
    }
    //    function test_color() {
    ////      mouseClick(tested.listview)
    ////      ddb.recentsModel[0].matiereBgColor = "red"
    //      var un = tested.listview.itemAtIndex(0)
    //      compare(un.background.color, "red")
    //    }
  }
}