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
      skip("broken")
      ddb._getMatiereIndexFromId = 1
      compare(combo.contentItem.text, "Mathematiques")
      compare(Qt.colorEqual(combo.contentItem.color, "yellow"), true)
      compare(Qt.colorEqual(combo.background.color, "black"), true)
    }

    function test_activite_rectangle() {
      ddb.currentPage = 1
      var rep = findChild(tested, "repeater")
      compare(rep.contentItem.children[0].model, ddb.pagesParSection[0])

    }

    function test_combo_popup() {
      combo.popup.open()
      var le_un = combo.popup.contentItem.itemAtIndex(0)
      compare(le_un.contentItem.text, "Lecture")
      compare(le_un.contentItem.color, "#ff0000")
      compare(le_un.background.color, "#0000ff")

    }
  }
}