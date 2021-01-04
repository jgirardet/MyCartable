import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/actions" as PageActions

BaseButton {
    id: imagesectionbutton

    Dialog {
        id: busydialog

        height: 400
        width: 400
        anchors.centerIn: Overlay.overlay

        BusyIndicator {
            anchors.fill: parent
            running: true
        }

        background: Rectangle {
            color: "transparent"
        }

    }

    action: PageActions.NewImageSection {
        position: targetIndex
        append: appendMode
        busy: busydialog
    }

}
