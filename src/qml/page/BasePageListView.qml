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
    //    print()
    positionViewAtIndex(row, ListView.Contain)
    currentIndex = row
  }
  Component.onCompleted: {
    model.rowsInserted.connect(onItemAdded)
  }

  Connections {
    target: model
    function onModelReset() {
      print("on bosse")
      print("model lastposition on resest", model.lastPosition)
      if (currentIndex != model.lastPosition) {
        currentIndex = model.lastPosition
        print("on set on resest ", currentIndex)
        //        lv.positionViewAtIndex(model.lastPosition, ListView.Beginning)
      }
    }
  }

}