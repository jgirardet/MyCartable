import QtQuick 2.14
import Operations 1.0
import "../page/operations"

BaseOperation {
  id: root
  cellWidth: 30
  cellHeight: 50

  model: SoustractionModel {
    sectionId: root.sectionId
  }

  delegate: SoustractionDelegate {
    model: root.model
  }
}