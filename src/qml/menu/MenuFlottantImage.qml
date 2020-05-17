import QtQuick 2.14
import QtQuick.Controls 2.14

BaseMenu {
  MenuItem {
    Column {
      ToolButton {
        text: qsTr("‹")
        onClicked: ddb.pivoterImage(root.sectionId, 90)
        ToolTip.text: "Pivoter l'image de 90°"
      }
    }
  }
}