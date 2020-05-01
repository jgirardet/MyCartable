import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  CasTest {
    name: "RecentsRectangle"
    testedNom: "qrc:/qml/matiere/RecentsRectangle.qml"
    params: {}

    function test_init() {
      compare(ddb.recentsModel, tested.children[0].model)
    }
  }
}