import QtQuick 2.15
import QtQuick.Controls 2.15

TableView {
    id: tableView

    required property Item lexique
    required property int columnWidth
    required property int rowHeight
    property alias removeDialog: effacer

    function itemAt(row, col) {
        return contentItem.children[row * columns + col];
    }

    model: lexique.proxy
    clip: true
    columnWidthProvider: () => {
        return columnWidth;
    }
    rowHeightProvider: () => {
        return rowHeight;
    }

    Dialog {
        id: effacer

        property int row

        function removeRow(nb) {
            row = nb;
            open();
        }

        anchors.centerIn: Overlay.overlay
        title: "Effacer cette ligne ?"
        standardButtons: Dialog.Yes | Dialog.No
        onAccepted: lexique.removeRow(row)
    }

    delegate: TextField {
        id: name

        color: 'black'
        text: display
        font.pointSize: 11
        onTextEdited: edit = text
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        onPressed: {
            if (event.button == Qt.MiddleButton) {
                readOnly = true;
                effacer.removeRow(row);
                event.accepted = true;
                timer_readonly.start();
            }
        }

        Timer {
            // dummy timer to prevent middle button past on  linux

            id: timer_readonly

            interval: 500
            repeat: false
            onTriggered: name.readOnly = false
        }

    }

}
