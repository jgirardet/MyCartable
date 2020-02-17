import QtQuick 2.14
import QtQuick.Controls 2.14

ListView {

  id: lv
  spacing: 10
  clip: true
  currentIndex: 0
  focus: true

  highlightMoveDuration: 1000
  highlightMoveVelocity: -1
  boundsBehavior: Flickable.DragOverBounds


//  preferredHighlightBegin: 0
//  preferredHighlightEnd: height / 2 + 1000
//  highlightRangeMode: ListView.StrictlyEnforceRange


  function onInsertRows(modelIndex, row, col) {
   currentIndex = row
  }

  function onModelReset() {
   currentIndex = 0
  }


  Component.onCompleted: {
    model.rowsInserted.connect(onInsertRows)
    model.modelReset.connect(onModelReset)
  }


}