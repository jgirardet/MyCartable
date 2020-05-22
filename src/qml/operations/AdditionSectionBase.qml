import QtQuick 2.14

BaseOperation {
  id: root
  cellWidth: 50
  cellHeight: 50
  //

  delegate: AdditionDelegate {
    model: root.model
  }

  Component.onCompleted: {
    currentIndex = count - 1
  }
}