import QtQuick 2.15
import QtQuick.Controls 2.15

Dialog {
    id: root

    property int itemIndex
    property string message

    function open(inputIndex) {
        itemIndex = inputIndex;
        visible = true;
    }

    parent: Overlay.overlay
    x: Math.round((parent.width - width) / 2)
    y: Math.round((parent.height - height) / 2)

    contentItem: Row {
        Label {
            id: label

            text: root.message
        }

    }

    enter: Transition {
        NumberAnimation {
            property: "scale"
            from: 0
            to: 1
        }

    }

    exit: Transition {
        NumberAnimation {
            property: "scale"
            from: 1
            to: 0
        }

    }

}
