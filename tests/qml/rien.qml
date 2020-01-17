import QtQuick 2.0
import QtTest 1.2


Item {
    RecentsListView {
    id: bla
    model: [1,2,3,4]

}

TestCase {
    name: "MathTests"

    function test_count() {

        compare(bla.contentItem.children[0],4, "2 + 2 = 4")
    }


  }
}