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
        color: ddb.getTextSectionColor('red')
        style: {
          "fgColor": color,
          "underline": false
        }
        menu: root
      }
      ColorButton {
        color: ddb.getTextSectionColor("blue")
        style: {
          "fgColor": color,
          "underline": false
        }
        menu: root
      }
      ColorButton {
        color: ddb.getTextSectionColor("green")
        style: {
          "fgColor": color,
          "underline": false
        }
        menu: root
      }
      ColorButton {
        color: ddb.getTextSectionColor("black")
        style: {
          "fgColor": color,
          "underline": false
        }
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
        color: ddb.getTextSectionColor('red')
        style: {
          "fgColor": color,
          "underline": true
        }
        menu: root
        text: "S"
      }
      ColorButton {
        color: ddb.getTextSectionColor("blue")
        style: {
          "fgColor": color,
          "underline": true
        }
        menu: root
        text: "S"
      }
      ColorButton {
        color: ddb.getTextSectionColor("green")
        style: {
          "fgColor": color,
          "underline": true
        }
        menu: root
        text: "S"
      }
      ColorButton {
        color: ddb.getTextSectionColor("black")
        style: {
          "fgColor": color,
          "underline": true
        }
        menu: root
        text: "S"
      }
    }
  }

}