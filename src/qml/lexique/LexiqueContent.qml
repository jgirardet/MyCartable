import QtQuick 2.15
import QtQuick.Controls 2.15

TableView {
    id: tableView

    columnWidthProvider: () => {
        return 300;
    }
    rowHeightProvider: () => {
        return 50;
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
