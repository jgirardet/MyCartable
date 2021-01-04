import MyCartable 1.0
import "qrc:/qml/operations"

BaseOperation {
    id: root

    cellWidth: 30
    cellHeight: 50
    model: section.model

    delegate: SoustractionDelegate {
        model: section.model
    }

}
