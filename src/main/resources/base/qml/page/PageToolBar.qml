import QtQuick 2.14
import QtQuick.Controls 2.14
//import QtQuick.Controls 1.4 as Controls1
import QtQuick.Layouts 1.14
import QtQuick.Dialogs 1.3 as Dialogs13

ToolBar {
  id: root

  RowLayout {
    ToolButton {
      id: newImageSection
      icon.source: "qrc:///icons/newImageSection"
      onClicked: newImageSectionFileDialog.open()
      enabled: ddb.currentPage
      ToolTip.visible: hovered
      ToolTip.text: "Ajouter une image"
    }

    ToolButton {
      id: newTextSection
      icon.source: "qrc:///icons/newTextSection"
      onClicked: ddb.addSection(ddb.currentPage, {
        "classtype": "TextSection"
      })
      enabled: ddb.currentPage
      ToolTip.visible: hovered
      ToolTip.text: "Ajouter du texte"
    }

    ToolButton {
      id: removePage
      icon.source: "qrc:///icons/removePage"
      onClicked: dialogRemovePage.open()
      enabled: ddb.currentPage
      ToolTip.visible: hovered
      ToolTip.text: "Supprimer la page"
    }
  }
  Dialogs13.FileDialog {
    id: newImageSectionFileDialog
    title: "Choisir une image à importer"
    folder: shortcuts.pictures
    nameFilters: ["fichiers Images (*.jpg *.png *.bmp)"]
    onAccepted: {
      ddb.addSection(ddb.currentPage, {
        'path': fileUrl,
        "classtype": "ImageSection"
      })

    }
  }
  Dialog {
      id: dialogRemovePage
      title: "Supprimer la page ?"
      standardButtons: Dialog.Ok | Dialog.Cancel
      onAccepted: ddb.removePage(ddb.currentPage)
    }
}