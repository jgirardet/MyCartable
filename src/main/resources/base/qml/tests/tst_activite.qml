import QtQuick 2.14
import QtTest 1.14

Item {

    ActiviteRectangle {
            headerText: "Leçons"
            headerColor: "orange"
            ddb: Rectangle{}
            activiteIndex: 0
            model: base.ddb.lessonsList
        }

//Rectangle {}

TestCase {
 name: "MathTests"
function test_math()
{ compare(2 + 2, 4, "2 + 2 = 4") }
}

}
