import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  Item {
    id: model
    property string nom: "Evaluations"
    property ListModel pages: ListModel {
      id: listmodel
      Component.onCompleted: {
        listmodel.append({
          "modelData": {
            "titre": "premier",
            "id": 99
          }
        })
      }
    }
  }

  CasTest {
    name: "ActiviteRectangle"
    testedNom: "qrc:/qml/matiere/ActiviteRectangle.qml"
    params: {
      "model": model
    }
    /* beautify preserve:start */
    property var lv
    /* beautify preserve:end */

    function initPost() {
      lv = findChild(tested, "_listView")
      tested.width = item.width //fix le problème deLayout.fillWidth
      tested.height = item.height //fix le problème deLayout en test
    }

    function test_header() {
      compare(lv.headerItem.label.text, "Evaluations")
    }

    function test_header_click() {
      mouseClick(lv.headerItem, 0, 0, Qt.RightButton)
      compare(ddb._newPage, tested.model.id)
    }

    function test_lv_item() {
      lv.currentIndex = 0
      ddb.currentPage = 0
      compare(lv.currentItem.text, "premier")
      compare(lv.currentItem.height, lv.headerItem.height)
    }

    function test_click_on_item() {
      lv.currentIndex = 0
      lv.forceLayout()
      mouseClick(lv.currentItem)
      compare(ddb.currentPage, 99)
    }

  }
}