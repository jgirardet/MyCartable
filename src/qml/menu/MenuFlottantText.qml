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
        color: "red"
        style: {
          "fgColor": color
        }
        shortcut: "Ctrl+r"
        menu: root
      }
      ColorButton {
        color: "blue"
        style: {
          "fgColor": color
        }
        shortcut: "Ctrl+b"
        menu: root
      }
      ColorButton {
        color: "green"
        style: {
          "fgColor": color
        }
        shortcut: "Ctrl+g"
        menu: root
      }
      ColorButton {
        color: "black"
        style: {
          "fgColor": color
        }
        shortcut: "Ctrl+n"
        menu: root
      }
    }
  }
  MenuSeparator {
    contentItem: Rectangle {
      implicitWidth: 200
      implicitHeight: 1
      color: "#21be2b"
    }
  }
  MenuItem {
    RowLayout {
      anchors.fill: parent
      spacing: 0
      ColorButton {
        color: "red"
        style: {
          "fgColor": color,
          "underline": "true"
        }
        shortcut: "Alt+r"
        menu: root
        text: "S"
      }
      ColorButton {
        color: "blue"
        style: {
          "fgColor": color,
          "underline": "true"
        }
        shortcut: "Alt+b"
        menu: root
        text: "S"
      }
      ColorButton {
        color: "green"
        style: {
          "fgColor": color,
          "underline": "true"
        }
        shortcut: "Alt+g"
        menu: root
        text: "S"

      }
      ColorButton {
        color: "black"
        style: {
          "fgColor": color,
          "underline": "true"
        }
        shortcut: "Alt+n"
        menu: root
        text: "S"

      }
    }
  }

}