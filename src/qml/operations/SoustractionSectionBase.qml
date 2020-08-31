import QtQuick 2.15

BaseOperation {
    id: root

    cellWidth: 30
    cellHeight: 50

    delegate: SoustractionDelegate {
        model: root.model
    }

}
