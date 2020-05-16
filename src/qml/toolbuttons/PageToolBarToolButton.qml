import QtQuick 2.14
import QtQuick.Controls 2.14

ToolButton {
  id: control
  /* beautify preserve:start */
  property string sectionName
  property var func: function() {}
  property int targetIndex
  property var target
  property var dialog
  /* beautify preserve:end */
  enabled: ddb.currentPage
  ToolTip.visible: hovered
  icon.color: enabled ? "transparent" : ddb.colorPageToolBar
  visible: enabled
  onClicked: {
    print(dialog)
    if (dialog) {
      dialog.open()
    } else {
      func()
    }
    if (root.target) {
      target.close()
    }
  }
  background: Rectangle {
    //    width: 40
    implicitWidth: 40
    implicitHeight: 40
    //    height: 40
    color: Qt.darker(ddb.colorPageToolBar, control.enabled && control.hovered ? 1.5 : 1.0)

  }

}