import Operations 1.0
import "qrc:/qml/operations"

AdditionSectionBase {
  id: root
  model: AdditionModel {
    sectionId: root.sectionId // on laisse tout là pour les tests
  }
}