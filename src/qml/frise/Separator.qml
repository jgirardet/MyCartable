import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: separator

    property QtObject dragParent: null
    property alias mousearea: mouseseparator
    property real localRatio

    color: mouseseparator.held ? "yellow" : "black"
    height: parent.height // + rab
    width: 5
    Component.onCompleted: localRatio = ratio

    MouseArea {
        id: mouseseparator

        property real startx
        property bool held: false

        cursorShape: Qt.SplitHCursor
        anchors.fill: parent
        onPressed: {
            startx = mouse.x;
            held = true;
            mouse.accepted = true;
        }
        onReleased: {
            if (held) {
                ratio = localRatio; //(separator.x + separator.width) / dragParent.width;
                //                mouse.accepted = true;
                held = false;
            }
        }
        drag.target: separator
        drag.axis: Drag.XAxis
        drag.threshold: 0
        drag.minimumX: 0
        drag.maximumX: separator.x + (dragParent.width - dragParent.contentItem.childrenRect.width) - 5
        onPositionChanged: {
            if (held) {
                localRatio = (separator.x + separator.width) / dragParent.width;
                mouse.accepted = true;
            }
        }
    }

}
