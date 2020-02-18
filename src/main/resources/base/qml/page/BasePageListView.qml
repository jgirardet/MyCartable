import QtQuick 2.14
import QtQuick.Controls 2.14

ListView {

  id: lv
  spacing: 10
  clip: true
  currentIndex: model.lastPosition
  focus: true

//  highlightFollowsCurrentItem: false

  highlightMoveDuration: 1000
  highlightMoveVelocity: -1
  boundsBehavior: Flickable.DragOverBounds

  //  onMovementStarted: print(currentIndex)

  //  preferredHighlightBegin: 0
  //  preferredHighlightEnd: height / 2 + 1000
  //  highlightRangeMode: ListView.StrictlyEnforceRange

  //
//    function onInsertRows(modelIndex, row, col) {
//      positionViewAtIndex(row , ListView.Visible)
//     model.lastPosition = row
//     print(currentIndex)
//    }

  function onModelReset() {
    // on ne peut pas changer currentIndex avant positionAt sinon on a le scroll
    // currentIndex n'est pas modifié car signal émis avant endSlotReset
    // envisager une transition sympa ?
    print(model.lastPosition, "danse onmodelreste")
    positionViewAtIndex(model.lastPosition, ListView.Contain) //non testé
//    model.lastPositionChanged() // update currentIndex sans peter le binding
  }

  Component.onCompleted: {
    model.modelReset.connect(onModelReset)
//    model.rowsInserted.connect(onInsertRows)
  }

}