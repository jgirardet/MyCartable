import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

TableView {
    id: tableView

    columnWidthProvider: () => {
        return database.getConfig("lexiqueColumnWidth");
    }
    rowHeightProvider: () => {
        return 50;
    }

    Database {
        id: database
    }

    delegate: TextField {
        id: name

        text: display
        font.pointSize: 14
        onTextEdited: edit = text
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
    }

}
