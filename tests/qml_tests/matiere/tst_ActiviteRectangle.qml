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
      model: ddb.pagesParSection[2]
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
    /* beautify preserve:start */
    property var lv
    /* beautify preserve:end */

    function init() {
      ddb = createTemporaryObject(ddbcomp, item)
      verify(ddb)
      rec = createTemporaryObject(reccomp, col, {
        "ddb": ddb
      })
      waitForRendering(rec)
      lv = findChild(rec, "_listView")
    }

    function cleanup() {
      rec.destroy() // remove warn message
      ddb.destroy()
    }

//
    function test_header() {
      compare(lv.headerItem.label.text, "Evaluations")
    }

    function test_header_click() {
    mouseClick(lv.headerItem, 0, 0 , Qt.RightButton)
      compare(ddb._newPage, rec.model.id)
    }

    function test_lv_item() {
      compare(lv.currentItem.text, "letitre 2 3")
      compare(lv.currentItem.height, lv.headerItem.height)
    }


    function test_click_on_item() {
      mouseClick(lv.currentItem)
      compare(ddb.currentPage, 12)
      }
//      var item = ddb.sp.lessonsList[0]
//      rec.model = ddb.sp.lessonsList
//      mouseClick(rec, 5, 35)
//      tryCompare(ddb, "currentPage", item.id)

  }
}