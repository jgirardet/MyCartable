// on l'attend dans un listview avec modelData

import QtQuick 2.14
import QtQuick.Controls 2.14

RoundButton {
    id: root

    property var model
    property var borderDefaultWidth: 1
    property var borderActivatedWidth: 3

    radius: 10
    onClicked: ddb.currentPage = model.id

    contentItem: MovingText {
        move: hovered
        text: model ? model.titre : null
    }

    background: Rectangle {
        id: back

        color: model && model.matiereBgColor ? model.matiereBgColor : "white"
        anchors.fill: parent
        radius: 10
        border.width: hovered ? borderActivatedWidth : borderDefaultWidth
    }

}
