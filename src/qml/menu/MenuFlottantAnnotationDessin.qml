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
          "fgColor": color,
          "bgColor": color,
        }

        menu: root
      }
      ColorButton {
        color: "blue"
        style: {
          "fgColor": color,
          "bgColor": color,
        }

        menu: root
      }
      ColorButton {
        color: "lime"
        style: {
          "fgColor": color,
          "bgColor": color,
        }

        menu: root
      }
      ColorButton {
        color: "black"
        style: {
          "fgColor": color,
          "bgColor": color,
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
    PointSizeSlider {
      menu: root
    }
  }

}