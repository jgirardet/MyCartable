// on l'attend dans un listview avec modelData

import QtQuick 2.15
import QtQuick.Controls 2.15

RoundButton {
    id: root

    property var borderDefaultWidth: 1
    property var borderActivatedWidth: 3

    radius: 10

    contentItem: MovingText {
        move: hovered
        text: titre

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            onPressed: {
                if (mouse.button == Qt.LeftButton)
                    classeur.setPage(pageid);
                else if (mouse.button == Qt.RightButton)
                    root.ListView.view.deplacePopup.ouvre(pageid, root);
            }
        }

    }

    background: Rectangle {
        id: back

        color: bgcolor
        anchors.fill: parent
        radius: 10
        border.width: hovered ? borderActivatedWidth : borderDefaultWidth
    }

}
