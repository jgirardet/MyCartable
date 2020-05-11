import QtQuick 2.14
import Operations 1.0
import "../page/operations"

BaseOperation {
  id: root
  cellWidth: 50
  cellHeight: 50
  //
  model: AdditionModel {
    sectionId: root.sectionId // on laisse tout là pour les tests
  }
  delegate: AdditionDelegate {
    model: root.model
  }

  Component.onCompleted: {
    print(width)
    currentIndex = count - 1
  }
}