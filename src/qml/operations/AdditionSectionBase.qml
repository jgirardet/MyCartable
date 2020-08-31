import QtQuick 2.15

BaseOperation {
    id: root

    cellWidth: 50
    cellHeight: 50
    Component.onCompleted: {
        currentIndex = count - 1;
    }

    delegate: AdditionDelegate {
        model: root.model
    }

}
