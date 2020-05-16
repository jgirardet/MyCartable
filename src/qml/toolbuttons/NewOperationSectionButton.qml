import QtQuick 2.14
import QtQuick.Controls 2.14

NewSectionButton {
  id: root
  sectionName: "OperationSection"
  //  func = function ()
  ToolTip.text: "Ajouter une Operation"
  dialog: Dialog {
    id: dialog
    implicitWidth: 300
    title: "Entrer 2 nombres séparés par +,-,* ou /"
    standardButtons: Dialog.Ok | Dialog.Cancel
    focus: true
    contentItem: TextField {
      focus: true
      background: Rectangle {
        anchors.fill: parent;
        color: "white"
      }
      onAccepted: dialog.accept()
    }
    onAccepted: {
      ddb.addSection(ddb.currentPage, {
        'string': contentItem.text,
        "classtype": root.sectionName,
        "position": typeof root.targetIndex == "number" ? root.targetIndex : null
      })
      contentItem.clear()
    }
  }
}