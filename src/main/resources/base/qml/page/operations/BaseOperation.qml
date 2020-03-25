import QtQuick 2.14
import QtQuick.Controls 2.14

GridView {
  id: root
  property int position
  property int sectionId
  width: cellWidth * model.columns
  height: cellHeight * model.rows
  cellWidth: 50
  cellHeight: 50
  keyNavigationEnabled: false
  onCurrentItemChanged: {
    currentItem.textinput.forceActiveFocus()
  }

  Binding on currentIndex {
    when: model.cursorChanged
    value: model.cursor
  }

  Component.onCompleted: {
    currentIndex = root.model.getInitialPosition()
  }
}