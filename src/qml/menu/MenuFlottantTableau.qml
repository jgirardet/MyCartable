import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.12

BaseMenu {
  id: root

  MenuItem {
    ColumnLayout {
      anchors.fill: parent
      Text {
        Layout.alignment: Qt.AlignHCenter
        text: "couleur d'arrière plan"
      }
      RowLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing: 0
        ColorButton {
          type: "cell_color"
          color: Qt.lighter("red")
          shortcut: "Ctrl+r"
          menu: root
        }
        ColorButton {
          type: "cell_color"
          color: Qt.lighter("blue")
          shortcut: "Ctrl+b"
          menu: root
        }
        ColorButton {
          type: "cell_color"
          color: Qt.lighter("green")
          shortcut: "Ctrl+g"
          menu: root
        }
        ColorButton {
          type: "cell_color"
          color: Qt.lighter("grey")
          shortcut: "Ctrl+n"
          menu: root
        }
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
  Text {
    Layout.alignment: Qt.AlignHCenter
    text: "couleur du texte"
  }

  MenuItem {
    RowLayout {
      anchors.fill: parent
      spacing: 0
      ColorButton {
        type: "color"
        color: "red"
        shortcut: "Ctrl+r"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "blue"
        shortcut: "Ctrl+b"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "green"
        shortcut: "Ctrl+g"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "black"
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
        type: "underline"
        color: "red"
        shortcut: "Alt+r"
        menu: root
        text: "S"
      }
      ColorButton {
        type: "underline"
        color: "blue"
        shortcut: "Alt+b"
        menu: root
        text: "S"
      }
      ColorButton {
        type: "underline"
        color: "green"
        shortcut: "Alt+g"
        menu: root
        text: "S"

      }
      ColorButton {
        type: "underline"
        color: "black"
        shortcut: "Alt+n"
        menu: root
        text: "S"

      }
    }
  }

}