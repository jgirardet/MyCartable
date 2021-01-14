import QtQuick 2.15
import QtQuick.Controls 2.15

HorizontalHeaderView {
    id: root

    required property Item lexique
    required property QtObject database

    columnWidthProvider: () => {
        return database.getConfig("lexiqueColumnWidth");
    }
    rowHeightProvider: () => {
        return 50;
    }
    model: lexique.model

    delegate: Label {
        text: display
        color: '#aaaaaa'
        font.pointSize: 20
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter

        MouseArea {
            anchors.fill: parent
            onClicked: lexique.doSort(index)
        }

    }

}
