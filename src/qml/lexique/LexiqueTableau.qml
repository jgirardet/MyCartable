import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    required property QtObject lexique
    property alias rows: table_content.rows
    property alias columns: table_content.columns

    function itemAt(row, col) {
        return table_content.contentItem.children[row * columns + col];
    }

    LexiqueTableauHeader {
        id: table_header
    }

    LexiqueContent {
        id: table_content

        model: lexique.proxy
        anchors.top: table_header.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        clip: true
    }

}
