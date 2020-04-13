import QtQuick 2.14
import QtQuick.Controls 2.14

TableView {
  id: root
  property int position
  property int sectionId
  property var base
  height: 50 * rows
//  width: ListView.view.width
  width: base.width
//  anchors.fill: parent
//  Binding on currentIndex {
//    when: model.sectionIdChanged
//    value: model.cursor
//  }
  clip: true
  columnSpacing: 1
  rowSpacing: 1
  delegate: Rectangle {
        implicitWidth: 100
        implicitHeight: 50
        TextInput {
            text: "display"
        }
    }
}