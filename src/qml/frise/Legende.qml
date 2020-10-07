//TextArea {
//    id: legende
//    height: Math.max(contentHeight + 10, 10)
//    width: Math.max(contentWidth + 20, 40)
//    anchors.bottomMargin: 10
//    anchors.topMargin: 10
//    anchors.horizontalCenter: separator.horizontalCenter
//    anchors.top: separator.bottom
//    state: separator.state
//    horizontalAlignment: TextEdit.AlignHCenter
//    verticalAlignment: TextEdit.AlignVCenter
//    text: separatorText
//    Component.onCompleted: {
//        onTextChanged.connect(function() {
//            separatorText = text;
//        });
//    }
//    states: [
//        State {
//            name: "up"
//            AnchorChanges {
//                target: legende
//                anchors.bottom: separator.top
//                anchors.top: undefined
//            }
//        }
//    ]
//    background: Rectangle {
//        anchors.fill: parent
//        border.width: 1
//        border.color: "black"
//    }

import QtQuick 2.15
import QtQuick.Controls 2.15

//}
Item {
    id: root

    property string legendeId
    property alias languette: languette
    property alias legende: legende
    property var realParent
    property Item handler

    anchors.top: parent.bottom
    Component.onCompleted: {
        onStateChanged.connect(() => {
            return handler.setProperty(index, "side", Boolean(state));
        });
        onXChanged.connect(() => {
            return handler.set(index, {
                "relativeX": x / parent.width
            });
        });
    }
    states: [
        State {
            name: "up"

            AnchorChanges {
                target: root
                anchors.bottom: parent.top
                anchors.top: undefined
            }

            AnchorChanges {
                target: legende
                anchors.bottom: languette.top
                anchors.top: undefined
            }

            PropertyChanges {
                target: languette
                y: -languette.height
            }

        }
    ]

    //    property
    TextArea {
        id: legende

        Component.onCompleted: {
            onTextChanged.connect(() => {
                return handler.setProperty(index, "texte", text);
            });
        }
        anchors.horizontalCenter: languette.horizontalCenter
        anchors.top: languette.bottom
        height: Math.max(contentHeight + 10, 10)
        width: Math.max(contentWidth + 20, 40)
        horizontalAlignment: TextEdit.AlignHCenter
        verticalAlignment: TextEdit.AlignVCenter

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.MiddleButton
            onWheel: {
                if (wheel.angleDelta.y > 0)
                    root.state = "up";
                else
                    root.state = "";
                wheel.accepted = true;
            }
            cursorShape: Qt.IBeamCursor
            onPressed: {
                if (mouse.button & Qt.MiddleButton)
                    handler.remove(index);

            }
        }

        background: Rectangle {
            anchors.fill: parent
            border.width: 1
            border.color: "black"
        }

    }

    Rectangle {
        id: languette

        width: 2
        height: 10
        color: "black"

        //        states
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.SizeHorCursor
            drag.target: root
            drag.axis: Drag.XAxis
            drag.minimumX: 5
            //drag.maximumX: root.parent.width - 5
            drag.threshold: 0
        }

    }

}
