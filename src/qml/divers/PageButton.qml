import QtQuick 2.14
import QtQuick.Controls 2.14

// on l'attend dans un listview avec modelData

RoundButton {
  id: root
  /* beautify preserve:start */
  property var model
  property var borderDefaultWidth: 1
  property var borderActivatedWidth: 4
  /* beautify preserve:end */
  radius: 10
  contentItem: MovingText {
    move: hovered
    text: model ? model.titre : null
  }
  background: Rectangle {
    id: back
    color: model && model.matiereBgColor ? model.matiereBgColor : "white"
    anchors.fill: parent
    radius: 10
    border.width: hovered ? borderActivatedWidth : borderDefaultWidth
  }
  onClicked: ddb.currentPage = model.id
}