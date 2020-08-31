import QtQuick 2.15
import QtQuick.Controls 2.15

Slider {
    id: colonneSlider

    property var menu

    //              height: 40
    wheelEnabled: true
    stepSize: 1
    to: 20
    from: 1
    value: 5
    onValueChanged: {
        menu.target.setStyleFromMenu({
            "style": {
                "pointSize": value
            }
        });
    }

    background: Rectangle {
        implicitWidth: 200
        implicitHeight: 10
        color: "transparent"

        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            width: parent.width
            height: colonneSlider.value
            color: "black" //"#21be2b"
            radius: 2
        }

    }

    handle: Rectangle {
        x: colonneSlider.leftPadding + colonneSlider.visualPosition * (colonneSlider.availableWidth - width)
        y: colonneSlider.topPadding + colonneSlider.availableHeight / 2 - height / 2
        //                    x:
        implicitWidth: 26
        implicitHeight: 26
        radius: 13
        color: colonneSlider.pressed ? "#f0f0f0" : "#f6f6f6"
        border.color: "#bdbebf"

        Text {
            id: textColumn

            text: colonneSlider.value
            font.pixelSize: 12
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }

    }

}
