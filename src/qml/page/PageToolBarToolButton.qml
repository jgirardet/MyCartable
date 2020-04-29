import QtQuick 2.14
import QtQuick.Controls 2.14

ToolButton {
  id: control
  enabled: ddb.currentPage
  ToolTip.visible: hovered
  icon.color: enabled ? "transparent" : ddb.colorPageToolBar
  visible: enabled

  background: Rectangle {
    implicitWidth: 40
    implicitHeight: 40
    color: Qt.darker(ddb.colorPageToolBar, control.enabled && control.hovered ? 1.5 : 1.0)

  }

}