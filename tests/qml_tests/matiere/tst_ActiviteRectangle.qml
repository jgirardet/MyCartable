import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/matiere"
import ".."
Item {
  id: item
  width: 200
  height: 60
  Component {
    id: ddbcomp
    DdbMock {}
  }
  ColumnLayout {
    id: col
    anchors.fill: parent
  }
  Component {
    id: reccomp
    ActiviteRectangle {
      headerText: "Evaluations"
      headerColor: "#ffa500"
      //            ddb: ddbcomp
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }
  TestCase {
    id: testcase
    name: "ActiviteRectangle"
    when: windowShown
    property DdbMock ddb
    property ActiviteRectangle rec

    function init() {
      ddb = createTemporaryObject(ddbcomp, item)
      verify(ddb)
      rec = createTemporaryObject(reccomp, col, {
        "ddb": ddb
      })
      waitForRendering(rec)
    }

    function cleanup() {
      rec.destroy() // remove warn message
      ddb.destroy()
    }

    function test_click_on_item() {
      var item = ddb.sp.lessonsList[0]
      rec.model = ddb.sp.lessonsList
      mouseClick(rec, 5, 35)
      tryCompare(ddb, "currentPage", item.id)
    }

    function test_ui_values() {
      rec.model = ddb.sp.lessonsList
      compare(rec.headerText, findChild(rec, "headerLabel").text)
      compare(rec.headerColor, findChild(rec, "headerRectangle").color)
      compare(rec.model[0].titre, findChild(rec, "buttonDelegate").text)
    }
  }
}