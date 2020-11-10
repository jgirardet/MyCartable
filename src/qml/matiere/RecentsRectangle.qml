import "../divers"
import "../menu"
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.14

ListView {
    id: root

    anchors.fill: parent
    model: ddb.recentsModel
    spacing: 5
    clip: true

    delegate: PageButton {
        height: contentItem.contentHeight + 20
        width: root.width
        model: modelData
    }

}
