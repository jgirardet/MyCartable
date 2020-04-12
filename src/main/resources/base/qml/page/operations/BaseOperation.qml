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
    if (currentItem) {
      currentItem.textinput.forceActiveFocus()
    }
  }

  Binding on currentIndex {
    when: model.sectionIdChanged
    value: model.cursor
  }

  Component.onCompleted: {
    currentIndex = model.getInitialPosition()
    print(currentIndex)
  }
}