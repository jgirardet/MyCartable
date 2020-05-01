import QtQuick 2.14
import QtQuick.Controls 2.14
import "../divers"

Rectangle {
  id: base
  color: ddb.colorFond
  ListView {
    id: root
    model: ddb.recentsModel
    anchors.fill: parent
    spacing: 5
    clip: true
    delegate: PageButton {
      height: contentItem.contentHeight + 20
      width: root.width
      model: modelData
    }
  }
}