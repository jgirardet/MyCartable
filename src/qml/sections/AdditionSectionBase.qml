import QtQuick 2.14
import "../page/operations"

BaseOperation {
  id: root
  cellWidth: 50
  cellHeight: 50
  //

  delegate: AdditionDelegate {
    model: root.model
  }

  Component.onCompleted: {
    print(width)
    currentIndex = count - 1
  }
}