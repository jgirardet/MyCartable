import MyCartable 1.0
import "qrc:/qml/operations"
TableauSectionBase {
  id: root
  model: TableauModel {
    sectionId: root.sectionId // on laisse tout là pour les tests
  }
}