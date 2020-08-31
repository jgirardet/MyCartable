import QtQuick 2.15
import QtQuick.Controls 2.15

Slider {
    id: colonneSlider

    property var menu
    property var target: menu.target
    property int adjustedValue: Math.floor(value / 10) ? Math.floor(value / 10) : 1

    wheelEnabled: true
    stepSize: 1
    to: 100
    from: 1
    Component.onCompleted: {
        value = target ? target.item.opacity * 100 : 0;
    }
    onAdjustedValueChanged: {
        if (!target)
            return ;

        menu.target.setStyleFromMenu({
            "style": {
                "weight": adjustedValue
            }
        });
    }

    background: Rectangle {
        implicitWidth: 200
        implicitHeight: 10
        color: target ? target.item.fillStyle : "transparent"
        opacity: colonneSlider.adjustedValue / 10

        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            width: parent.width
            height: 2
            color: "black" //"#21be2b"
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

            text: colonneSlider.adjustedValue
            font.pixelSize: 12
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }

    }

}
