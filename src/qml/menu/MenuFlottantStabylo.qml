import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.12

BaseMenu {
  id: root
  MenuItem {
    RowLayout {
      anchors.fill: parent
      spacing: 0
      ColorButton {
        style: {
          "bgColor": color
        }
        color: "red"
        menu: root
      }
      ColorButton {
        style: {
          "bgColor": color
        }
        color: "blue"
        menu: root
      }
      ColorButton {
        style: {
          "bgColor": color
        }
        color: "aqua"
        menu: root
      }
      ColorButton {
        style: {
          "bgColor": color
        }
        color: "green"
        menu: root
      }
      ColorButton {
        style: {
          "bgColor": color
        }
        color: "chartreuse"
        menu: root
      }
      ColorButton {
        style: {
          "bgColor": color
        }
        color: "yellow"
        menu: root
      }
    }
  }

}