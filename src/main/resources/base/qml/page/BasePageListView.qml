import QtQuick 2.14
import QtQuick.Controls 2.14

ListView {

  id: lv
  spacing: 10
  clip: true
  currentIndex: model.lastPosition
  focus: true

  highlightMoveDuration: -1
  highlightMoveVelocity: 200 * count
  boundsBehavior: Flickable.DragOverBounds

}