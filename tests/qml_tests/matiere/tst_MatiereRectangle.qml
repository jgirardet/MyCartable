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

    function initPre() {
    }

    function initPost() {
    }

    function test_matiere_combox() {
      ddb._getMatiereIndexFromId = ddb.sp.getMatiereIndexFromId.id3
      var cb = findChild(tested, "_comboBoxSelectMatiere")
      compare(cb.currentIndex, 2)
      compare(cb.currentText, "Histoire")
    }

    function test_matiere_combo_click() {
      var cb = findChild(tested, "_comboBoxSelectMatiere")
      var spt = getSpy(ddb, "setCurrentMatiereFromIndexSignal")
      compare(spt.count, 0)
      cb.activated(3)
      compare(spt.count, 2) // called twice... why ???
    }

    function test_activite_testedtangle() {
        ddb.currentPage =1
        var rep = tested.repeater
        compare(rep.itemAt(0).model, ddb.pagesParSection[0])

    }
  }
}