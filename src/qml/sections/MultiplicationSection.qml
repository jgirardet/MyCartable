import MyCartable 1.0
import "qrc:/qml/operations"

BaseOperation {
    id: root

    cellWidth: 50
    cellHeight: 50
    model: section.model

    delegate: MultiplicationDelegate {
        model: section.model
    }

}
