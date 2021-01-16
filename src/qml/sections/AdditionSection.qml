import MyCartable 1.0
import QtQuick 2.15
import "qrc:/qml/operations"

BaseOperation {
    id: root

    cellWidth: 50
    cellHeight: 50

    delegate: AdditionDelegate {
        model: section.model
    }

}
