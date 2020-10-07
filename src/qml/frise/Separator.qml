import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    //        id: legende
    //        height: Math.max(contentHeight + 10, 10)
    //        width: Math.max(contentWidth + 20, 40)
    //        anchors.bottomMargin: 10
    //        anchors.topMargin: 10
    //        anchors.horizontalCenter: separator.horizontalCenter
    //        anchors.top: separator.bottom
    //        state: separator.state
    //        horizontalAlignment: TextEdit.AlignHCenter
    //        verticalAlignment: TextEdit.AlignVCenter
    //        text: separatorText
    //        Component.onCompleted: {
    //            onTextChanged.connect(function() {
    //                separatorText = text;
    //            });
    //        }
    //        states: [
    //            State {
    //                name: "up"
    //                AnchorChanges {
    //                    target: legende
    //                    anchors.bottom: separator.top
    //                    anchors.top: undefined
    //                }
    //            }
    //        ]
    //        background: Rectangle {
    //            anchors.fill: parent
    //            border.width: 1
    //            border.color: "black"
    //        }
    //    }
    //    state: separatorPosition ? "up" : ""
    //    states: [
    //        State {
    //            name: "up"
    //            PropertyChanges {
    //                target: separator
    //                y: -rab
    //            }
    //        }
    //    ]
    //    Legende {
    //        id: legende
    //        function updateText() {
    //            separatorText = text;
    //        }
    //        stateToUpdate: separator.state
    //        text: separatorText
    //        state: separator.state
    //        anchors.horizontalCenter: parent.horizontalCenter
    //    }
    //    TextArea {

    id: separator

    property QtObject dragParent: null
    //    property int rab: 20
    //    property alias legende: legende
    property alias mousearea: mouseseparator

    color: mouseseparator.held ? "yellow" : "black"
    height: parent.height // + rab
    width: 5

    MouseArea {
        //                separator.state = "up";

        id: mouseseparator

        property real startx
        property bool held: false

        //        hoverEnabled: true
        cursorShape: Qt.SplitHCursor
        anchors.fill: parent
        onPressed: {
            startx = mouse.x;
            held = true;
            mouse.accepted = true;
        }
        //        onWheel: {
        //            if (wheel.angleDelta.y > 0)
        //                separatorPosition = true;
        //            else
        //                separatorPosition = false;
        //                            separator.state = "";
        //            wheel.accepted = true;
        //        }
        onReleased: {
            if (held)
                held = false;

        }
        drag.target: separator
        drag.axis: Drag.XAxis
        drag.threshold: 0
        drag.minimumX: 0
        drag.maximumX: separator.x + (dragParent.width - dragParent.contentItem.childrenRect.width) - 5
        onPositionChanged: {
            if (held) {
                ratio = (separator.x + separator.width) / dragParent.width;
                mouse.accepted = true;
            }
        }
    }

}
