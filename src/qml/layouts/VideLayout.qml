import QtQuick 2.15
import "qrc:/qml/layouts"

Rectangle {
    SplitSwitch {
        id: switcher

        Component.onCompleted: switcher.popup.open()

        anchors {
            top: parent.top
            horizontalCenter: parent.horizontalCenter
        }

    }

}
