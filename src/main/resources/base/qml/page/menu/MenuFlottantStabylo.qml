import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.12

Menu {
  id: root
  property
  var editor
  signal styleChange(var data)

  MenuItem {
    RowLayout {
      anchors.fill: parent
      spacing: 0
      ColorButton {
        type: "color"
        color: "red"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "blue"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "aqua"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "green"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "chartreuse"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "yellow"
        menu: root
      }
    }
  }

}