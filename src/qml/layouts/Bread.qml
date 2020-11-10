import QtQuick 2.15
import QtQuick.Controls 2.15

Control {
    id: bread

    property Item sandwich
    property int widthBig: 250
    property int widthSmall: 20
    property alias animDuration: width_animation.duration

    z: parent.contentItem.z + 1
    state: sandwich.breadsState
    height: sandwich.height
    hoverEnabled: true
    onHoveredChanged: {
        if (hovered)
            sandwich.breadsState = "big";
        else if (!hovered && !sandwich.expectBig)
            sandwich.breadsState = "small";
    }
    states: [
        State {
            name: "small"

            PropertyChanges {
                target: bread
                width: widthSmall
            }

            PropertyChanges {
                target: bread
                horizontalPadding: 0
            }

        },
        State {
            name: "big"

            PropertyChanges {
                target: bread
                width: widthBig
            }

            PropertyChanges {
                target: bread
                horizontalPadding: 0
            }

        }
    ]

    Behavior on width {
        PropertyAnimation {
            id: width_animation

            duration: 300
        }

    }

}
