import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../src/main/resources/base/qml"

Item {
    id: item
    width: 200
    height: 300


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
            headerColor: "orange"
//            ddb: ddbcomp
            model: [{"titre":"bla", "id": 5}]
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
            rec = createTemporaryObject(reccomp,col,  {"ddb":ddb})
            verify(rec)
        }

        function test_init() {
            var lv = findChild(rec, "listview")
            print(rec.children[0].children[0].children[0].text)
            mouseClick(rec.children[0].children[0].children[0], 50, 40)
            tryCompare(ddb, "currentPage", 5)
        }

        //       function test_addannotation() {
        //            mouseDoubleClick(anot, 50, 30)
        //            keyPress(Qt.Key_A)
        //            keyPress(Qt.Key_B)
        //            var inp = anot.annotations[0]
        //            compare(inp.text, "ab")
        //            compare(inp.relativeX, 0.25)
        //            compare(inp.relativeY, 30/anot.implicitHeight)
        //        }

        //       function test_init_zone() {
        //           mousePress(anot)
        //           compare(anot.mouseArea.temp_rec.relativeWidth, 0)
        //       }

        //       function test_update_zone() {
        //           mousePress(anot, 50, 50)
        //           mouseMove(anot, 100, 170)
        //           var rec = anot.mouseArea.temp_rec
        //           compare(rec.relativeWidth, 0.25)
        //           compare(rec.relativeHeight, 120/174) //174 et le ratio de la hauteur avec preservefit

        //       }
        //       function test_update_zone_negative_size() {
        //           mousePress(anot, 100, 100)
        //           mouseMove(anot, 50, 50)
        //           var rec = anot.mouseArea.temp_rec
        //           compare(rec.relativeWidth, 0)
        //           compare(rec.relativeHeight, 0)
        //       }

        //       function test_store_zone() {
        //           mousePress(anot, 50, 50)
        //           mouseMove(anot, 100, 170)

        //           mouseRelease(anot, 100, 170)
        //           var rec = anot.mouseArea.temp_rec
        //           compare(rec, null)
        //           compare(anot.annotations[0].relativeWidth, 0.25)
        //           compare(anot.annotations[0].relativeHeight,120/174) //cf plus heut

        //       }
    }
}
