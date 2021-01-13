import QtQuick 2.15
import QtQuick.Controls 2.15

TableView {
    id: tableView

    //    columnWidthProvider: () => {
    //        return width / columns;
    //    }
    rowHeightProvider: () => {
        return 50;
    }

    delegate: TextField {
        id: name

        text: display
        onTextEdited: edit = text
    }

}
