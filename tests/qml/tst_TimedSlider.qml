import QtQuick 2.15
import "qrc:/qml/divers"

Item {
    id: item

    width: 200
    height: 200

    TimedSlider {
        id: slider

        property real rien

        function update_target() {
            rien = position;
        }

    }

    CasTest {
        function initPre() {
        }

        function initPost() {
            slider.value = 0;
            slider.rien = 0;
        }

        function test_change_doesnt_apply_if_too_fast() {
            for (const i of Array(5).keys()) {
                slider.increase();
            }
            compare(slider.rien, 0);
        }

        function test_change_value() {
            slider.timer.interval = 0;
            for (const i of Array(5).keys()) {
                slider.increase();
            }
            tryCompare(slider, "rien", 0.5);
        }

        autocreate: false
        name: "TimedSlider"
        testedNom: "qrc:/qml/divers/TimedSlider.qml"
    }

}
