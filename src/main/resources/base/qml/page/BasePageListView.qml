import QtQuick 2.14
import QtQuick.Controls 2.14

ListView {

  id: lv
  spacing: 10
  clip: true
//  currentIndex: model.lastPosition
  focus: true

//  highlightMoveDuration: -1
//  highlightMoveVelocity: 200 * count
  boundsBehavior: Flickable.DragOverBounds
  onCurrentIndexChanged: {
    print("currentindex changed :", currentIndex)
    if (model.lastPosition !== currentIndex) {
      model.lastPosition = currentIndex
    }
  }

  function onItemAdded(modelIndex, row, col) {
//    print()
    positionViewAtIndex(row, ListView.Contain )
    currentIndex = row
  }
  Component.onCompleted: {
    model.rowsInserted.connect(onItemAdded)
  }
//  ListView.s: {
//    print("on adde")
//  }
//  onCurrentIndexChanged: Transition {
//        NumberAnimation { properties: "x,y"; duration: 400; easing.type: Easing.OutBounce }
//    }
//    print("currentIndex", currentIndex, model.lastPosition)
//    if (currentIndex != model.lastPosition) {
//    print("on bosse")
//        model.lastPosition=currentIndex
//        positionViewAtIndex(currentIndex, ListView.Beginning)
//
//    }
//    print("current currentIndexChanged", currentIndex)
//  }
//  onMovementEnded: {
//    print(currentIndex)
//  }
//  Binding on currentIndex {
//      when: model.modelReset
//      value: model.lastPosition
//    if (currentIndex != model.lastPosition) {
//      model.lastPosition=currentIndex
//      print("on currentindex changed", currentIndex)
//    }
//    }
//   move: Transition {
//        NumberAnimation { property: "opacity"; from: 0; to: 1.0; duration: 400 }
//        NumberAnimation { property: "scale"; from: 0; to: 1.0; duration: 400 }
//    }

//    displaced: Transition {
//        NumberAnimation { properties: "x,y"; duration: 400; easing.type: Easing.OutBounce }
//    }

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