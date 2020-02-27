import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.12

Button {
  id: root
  property alias shortcut: action.shortcut
  /* beautify preserve:start */
  property color color
  property var menu
  property var type
  /* beautify preserve:end */

  Layout.fillHeight: true
  Layout.fillWidth: true

  background: Rectangle {
    id: back
    color: root.color
    anchors.fill: parent
  }
  highlighted: pressed
  action: action
  Action {
    id: action
    onTriggered: {
      uiManager.menuTarget.setStyleFromMenu({
        "type": root.type,
        "value": root.color
      })
      menu.ferme()
    }
  }
}