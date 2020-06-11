import QtQuick 2.14
import QtQuick.Controls 2.14

NewSectionButton {
  id: root
  ToolTip.text: "Effacer un page"
  icon.source: "qrc:///icons/removePage"
  dialog: Dialog {
    id: dialogRemovePage
    title: "Supprimer la page ?"
    standardButtons: Dialog.Ok | Dialog.Cancel
    onAccepted: ddb.removePage(ddb.currentPage)
  }
}