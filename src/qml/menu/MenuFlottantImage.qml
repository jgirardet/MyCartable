import QtQuick 2.14
import QtQuick.Controls 2.14

BaseMenu {
  id: menu
  MenuItem {
    Row {
      ToolButton {
        icon.source: "qrc:///icons/rotateLeft"
        icon.color: "blue"
        onClicked: {
          var res = ddb.pivoterImage(menu.target.sectionId, 0)
          if (res) {
            target.reloadImage()
          }
        }
        ToolTip.text: "Pivoter à  gauche"
      }
      ToolButton {
        icon.source: "qrc:///icons/rotateRight"
        icon.color: "blue"

        onClicked: {
          var res = ddb.pivoterImage(menu.target.sectionId, 1)
          if (res) {
            target.reloadImage()
          }
        }
        ToolTip.text: "Pivoter à droite"
      }
    }
  }
}