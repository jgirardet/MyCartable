import QtQuick 2.14
import QtQuick.Controls 2.14
Dialog {
  id: root
  property string classType
  title: "Entrer l'operation"
  standardButtons: Dialog.Ok | Dialog.Cancel
  focus: true
  contentItem: TextField {
    focus: true
    background: Rectangle {
      anchors.fill: parent;
      color: "white"
    }
    onAccepted: root.accept()
  }
  onAccepted: {
    ddb.addSection(ddb.currentPage, {
      'string': contentItem.text,
      "classtype": classType
    })
    contentItem.clear()
  }
}