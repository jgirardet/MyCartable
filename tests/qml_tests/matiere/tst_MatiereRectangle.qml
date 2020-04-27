import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  CasTest {
    name: "MatiereRectangle"
    testedNom: "qrc:/qml/matiere/MatiereRectangle.qml"
    params: {}
    property QtObject combo

    function initPreCreate() {
      ddb = ddbData
    }

    function initPost() {
      combo = findChild(tested, "combo")
    }

   function test_matiere_combox() {
    ddb._getMatiereIndexFromId = 1
    compare(combo.currentIndex, 1)
    compare(combo.contentItem.text, "Mathematiques")
  }

    function test_matiere_combo_click() {
      var spt = getSpy(ddb, "setCurrentMatiereFromIndexSignal")
      compare(spt.count, 0)
      combo.activated(3)
      compare(spt.count, 2) // called twice... why ???
    }



    function test_comno_property_when_matiere_set() {
      ddb._getMatiereIndexFromId = 1
      compare(combo.contentItem.text, "Mathematiques")
      compare(Qt.colorEqual(combo.contentItem.color, "yellow"), true)
      compare(Qt.colorEqual(combo.background.color, "black"), true)
      compare(combo.popup.contentItem.children[0].children[0].contentItem.text, "Lecture")
      compare(Qt.colorEqual(combo.popup.contentItem.children[0].children[0].contentItem.color,"red"), true)
    }

    function test_activite_rectangle() {
      ddb.currentPage = 1
      var rep = tested.repeater
      compare(rep.itemAt(0).model, ddb.pagesParSection[0])

    }
  }
}