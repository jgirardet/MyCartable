import QtQuick 2.15
import QtQuick.Controls 2.15

TableView {
    id: tableView

    required property Item lexique
    required property QtObject database

    function itemAt(row, col) {
        return contentItem.children[row * columns + col];
    }

    model: lexique.proxy
    clip: true
    columnWidthProvider: () => {
        return database.getConfig("lexiqueColumnWidth");
    }
    rowHeightProvider: () => {
        return 50;
    }

    delegate: TextField {
        id: name

        color: 'black'
        text: display
        font.pointSize: 14
        onTextEdited: edit = text
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
    }

}
