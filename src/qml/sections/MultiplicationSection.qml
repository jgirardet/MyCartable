import QtQuick 2.14
import Operations 1.0
import "../page/operations"

BaseOperation {
  id: root
  cellWidth: 50
  cellHeight: 50

  model: MultiplicationModel {
    sectionId: root.sectionId
  }

  delegate: MultiplicationDelegate {
    model: root.model
  }

}