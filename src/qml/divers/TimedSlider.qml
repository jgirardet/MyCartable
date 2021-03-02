import QtQuick 2.15
import QtQuick.Controls 2.15

/*
  Slider which keeps live to update value, but trigger update of target
  after a given interval
*/
Slider {
    property Timer timer: timer_id
    property var triggerValue: value

    function update_target() {
    }

    onTriggerValueChanged: timer_id.restart()

    Timer {
        id: timer_id

        interval: 300
        repeat: false
        onTriggered: update_target()
    }

}
