import QtQuick 2.14

BaseOperation {
    id: root

    cellWidth: 50
    cellHeight: 50

    delegate: MultiplicationDelegate {
        model: root.model
    }

}
