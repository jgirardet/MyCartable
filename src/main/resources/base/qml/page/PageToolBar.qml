import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.14
import QtQuick.Dialogs 1.3

ToolBar {
  id: root

  RowLayout {
    ToolButton {
      id: newImageSection
      iconSource: "qrc:///icons/newImageSection"
      onClicked: newImageSectionFileDialog.open()
      enabled: ddb.currentPage
    }

    ToolButton {
      id: newTextSection
      iconSource: "qrc:///icons/newTextSection"
      onClicked: ddb.addSection(ddb.currentPage, {
        "classtype": "TextSection"
      })
      enabled: ddb.currentPage
    }
  }
  FileDialog {
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
}