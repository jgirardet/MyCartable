import QtQuick 2.14
import QtQuick.Controls 2.14

GridView {
  id: root
  /* beautify preserve:start */
  property int sectionId
  property var sectionItem
  /* beautify preserve:end */
  contentWidth: cellWidth * model.columns
  width: contentWidth
  height: contentHeight
  contentHeight: cellHeight * model.rows
  //  height: cellHeight * model.rows
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

}