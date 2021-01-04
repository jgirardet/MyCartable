import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 70
    height: 200

    CasTest {
        // pour avoir le temps de tester
        //pas de latence
        //            wait(1000);
        // timeout pour la CI
        //            if (Qt.platform.os == "windows")
        //                skip("ne marche pas sur windows");

        property var moveTextLeft
        property var moveTextRight

        function initPre() {
        }

        function initPreCreate() {
        }

        function initPost() {
            moveTextLeft = findChild(tested, "moveTextLeft");
            moveTextRight = findChild(tested, "moveTextRight");
            verify(moveTextLeft.loops == 1);
            verify(moveTextRight.loops == 1);
        }

        function test_init() {
            verify(tested.text == "a");
            tested.text = "azeraezrtrerter".repeat(10);
            compare(tested.truncated, true);
        }

        function test_do_nothing_if_no_truncated() {
            tested.text = "a";
            tested.move = true;
            verify(moveTextLeft.running == false);
        }

        function test_start_animation() {
            tested.text = "azeraezrtrerter";
            tested.move = true;
            tryCompare(moveTextLeft, "running", true);
        }

        function test_start_animation_and_stop() {
            tested.text = "azeraezrtrerter";
            verify(tested.truncated == true);
            var oldX = tested.x;
            tested.move = true;
            tryCompare(moveTextLeft, "running", true);
            tested.move = false;
            tryCompare(moveTextLeft, "running", false);
            tryCompare(tested, "x", oldX, 2000);
            compare(tested.textInitialPosition, 0);
        }

        name: "MovingText"
        testedNom: "qrc:/qml/divers/MovingText.qml"
        params: {
            "referentiel": item.width,
            "text": "a",
            "width": item.width,
            "vitesse": 1,
            "pauseOnLeft": 0,
            "pauseOnRight": 0
        }
    }

}
