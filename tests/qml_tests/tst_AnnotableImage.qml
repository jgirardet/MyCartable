import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../src/main/resources/base/qml/"

Item {
    id: item
    width: 200
    height: 300


    Component {
            id: anotimg
            AnnotableImage {
                sourceSize.width: parent.width
                source: 'aaa.png'}
        }

    TestCase {
        id: testcase
        name: "AnnotableImage"; when: windowShown
        property AnnotableImage anot: null

        function init() {
            anot = createTemporaryObject(anotimg, item )
            verify(anot)
        }

        function test_init() {
            compare(anot.annotationInput.url, "qrc:/qml/AnnotationInput.qml")

        }

       function test_addannotation() {
            mouseDoubleClick(anot, 50, 30)
            keyPress(Qt.Key_A)
            keyPress(Qt.Key_B)
            var inp = anot.annotations[0]
            compare(inp.text, "ab")
            compare(inp.relativeX, 0.25)
            compare(inp.relativeY, 30/anot.implicitHeight)
        }

       function test_init_zone() {
           mousePress(anot)
           compare(anot.mouseArea.temp_rec.relativeWidth, 0)
       }

       function test_update_zone() {
           mouseDrag(anot, 50, 50,50, 100)
           var rec = anot.mouseArea.temp_rec
           console.log(rec, "re")
           compare(rec.relativeWidth, 50/item.width)
       }
    }
   }
