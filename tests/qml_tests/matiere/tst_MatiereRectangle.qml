import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/matiere"
import ".."
Item {
  id: item
  width: 800
  height: 600
  Component {
    id: ddbcomp
    DdbMock {}
  }
  RowLayout {
    id: col
    anchors.fill: parent
  }
  Component {
    id: reccomp
    MatiereRectangle {
      property
      var ddb
    }
  }
  Component {
    id: spycomp
    SignalSpy {}
  }
  TestCase {
    id: testcase
    name: "MatiereRectangle"
    when: windowShown
    property DdbMock ddb
    property MatiereRectangle rec

    function init() {
      ddb = createTemporaryObject(ddbcomp, item)
      verify(ddb)
      rec = createTemporaryObject(reccomp, col, {
        "ddb": ddb
      })
      waitForRendering(rec)
    }

    function cleanup() {
      rec.destroy()
    }

    function test_matiere_combox() {
      ddb._getMatiereIndexFromId = ddb.sp.getMatiereIndexFromId.id3
      var cb = findChild(rec, "_comboBoxSelectMatiere")
      compare(cb.currentIndex, 2)
      compare(cb.currentText, "Histoire")
    }

    function test_matiere_combo_click() {
      var cb = findChild(rec, "_comboBoxSelectMatiere")
      var spt = ddb.getSpy(ddb, "setCurrentMatiereFromIndexSignal")
      compare(spt.count, 0)
      cb.activated(3)
      compare(spt.count, 2) // called twice... why ???
    }

    function test_activite_rectangle() {
        var rep = findChild(rec, "repeater")
        compare(rep.itemAt(0).headerText, "Lessons")
        compare(rep.itemAt(0).model, ddb.pagesParSection[0].pages)
        compare(rep.itemAt(1).headerText, "Exercices")
        compare(rep.itemAt(1).model, ddb.pagesParSection[1].pages)
        compare(rep.itemAt(2).headerText, "Evaluations")
        compare(rep.itemAt(2).model, ddb.pagesParSection[2].pages)

    }
  }
}