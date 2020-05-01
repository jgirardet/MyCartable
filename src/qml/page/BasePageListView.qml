import QtQuick 2.14
import QtQuick.Controls 2.14

ListView {

  id: lv
  spacing: 10
  clip: true
  //  currentIndex: model.lastPosition
  focus: true

  boundsBehavior: Flickable.DragOverBounds
  onCurrentIndexChanged: {
    print("currentindex changed :", currentIndex)
    if (model.lastPosition !== currentIndex) {
      model.lastPosition = currentIndex
    }
  }

  function onItemAdded(modelIndex, row, col) {
    positionViewAtIndex(row, ListView.Contain)
    currentIndex = row
  }
  Component.onCompleted: {
    model.rowsInserted.connect(onItemAdded)
  }

  Connections {
    target: model
    function onModelReset() {
      if (currentIndex != model.lastPosition) {
        currentIndex = model.lastPosition
      }
    }
  }

}