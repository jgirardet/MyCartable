import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../src/main/resources/base/qml/"


Item {
    width: 200
    height: 200
    id: item

    Component {
        id: refcomp
        Item {
            width: item.width
            height: item.height
            property var annotations: []
        }
    }

    Component {
        id: anotinp
        AnnotationInput {
            relativeX: 0.48
            relativeY: 0.10
            //referent: ref
        }
    }

    TestCase {

        name: "AnnotationInput"; when: windowShown
        property AnnotationInput anot
        property Item ref

        function init() {
//            ref = createTemporaryObject(refcomp, item) sinon Warn
            ref = refcomp.createObject(item)
            anot = createTemporaryObject(anotinp, ref, {"referent":ref})
            verify(anot)
            verify(ref)
            ref.annotations.push(anot)
        }

        function test_AnotXY() {
            compare(anot.x, 96)
            compare(anot.y, 20)
        }
         function test_focus() {
             anot.focus = true
             compare(anot.background.border.color, "#21be2b")

             anot.focus = false
             compare(anot.background.border.color, "#00000000")
         }

         function test_mousearea() {
             //ficusable
             anot.focus = false
             mouseClick(anot)
             compare(anot.focus, true)

             //right click destry
             mouseClick(anot,undefined,undefined,Qt.RightButton)
             waitForRendering(anot)
             compare(ref.annotations, [])
             compare(anot, null)

         }
    }
}
//}
