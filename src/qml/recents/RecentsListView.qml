import QtQuick 2.12
import QtQuick.Controls 2.12
ListView {
  signal itemClicked(int id, int matiere)
  headerPositioning: ListView.OverlayHeader
  spacing: 5
  height: parent.height
  width: parent.width
  clip: true
  delegate: RoundButton {
    id: _buttonDelegateRecents
    objectName: "_buttonDelegateRecents"
    height: 40
    radius: 10
    text: modelData.titre
    highlighted: hovered
    background: Rectangle {
      id: back
      color: modelData.matiereBgColor ? modelData.matiereBgColor : "white"
      anchors.fill: parent
      radius: 10
    }
    width: ListView.view.width
    onClicked: ListView.view.itemClicked(modelData.id, modelData.matiere)
  }
  // TODO: tester tout ça
}