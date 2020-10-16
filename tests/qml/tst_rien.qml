import ".."
import PyTest 1.0
import QtQuick 2.15

Item {
    id: item

    width: 200
    height: 200

    Rectangle {
        id: rect

        height: 50
        width: 100
        color: "blue"
        border.width: 5
        border.color: "green"
    }

    TestCase {
        function test_grad() {
            rect.visible = false;
            wait(50);
            rect.grabToImage(function(result) {
                result.saveToFile("/tmp/something.png");
            });
            wait(50);
        }

    }

}
