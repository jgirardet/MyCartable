import QtQuick 2.14
import QtQuick.Controls 2.14
//import QtQuick.Controls 1.4 as Controls1
import QtQuick.Layouts 1.14
import QtQuick.Dialogs 1.3 as Dialogs13

ToolBar {
  id: root
  background: Rectangle {
    anchors.fill: parent
    radius: 10
    //    color: "transparent"

  }
  RowLayout {
    anchors.fill: parent
    spacing: 0
    id: rowLayout

    ToolButton {
      id: newImageSection
      icon.source: "qrc:///icons/newImageSection"
      onClicked: newImageSectionFileDialog.open()
      enabled: ddb.currentPage
      ToolTip.visible: hovered
      ToolTip.text: "Ajouter une image"
      icon.color: "transparent"
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
      icon.color: "transparent"
    }

    ToolButton {
      id: removePage
      icon.source: "qrc:///icons/removePage"
      onClicked: dialogRemovePage.open()
      enabled: ddb.currentPage
      ToolTip.visible: hovered
      ToolTip.text: "Supprimer la page"
      icon.color: "transparent"
    }

    ToolBar {
      //      visible: ddb.currentMatiere == 1
      RowLayout {
        ToolButton {
          id: addAddition
          icon.source: "qrc:///icons/addAddition"
          icon.color: "transparent"
          onClicked: dialogAddAddition.open()
          enabled: ddb.currentPage
          ToolTip.visible: hovered
          ToolTip.text: "Ajouter une addition"
        }
        ToolButton {
          id: addSoustraction
          icon.color: "transparent"
          icon.source: "qrc:///icons/addSoustraction"
          onClicked: dialogAddSoustraction.open()
          enabled: ddb.currentPage
          ToolTip.visible: hovered
          ToolTip.text: "Ajouter une soustraction"
        }
        ToolButton {
          id: addMultiplication
          icon.color: "transparent"
          icon.source: "qrc:///icons/addMultiplication"
          onClicked: dialogAddMultiplication.open()
          enabled: ddb.currentPage
          ToolTip.visible: hovered
          ToolTip.text: "Ajouter une multiplication"
        }
        ToolButton {
          id: addDivision
          icon.color: "transparent"
          icon.source: "qrc:///icons/addDivision"
          onClicked: dialogAddDivision.open()
          enabled: ddb.currentPage
          ToolTip.visible: hovered
          ToolTip.text: "Ajouter une division"
        }
      }
    }

    Rectangle {
      Layout.fillWidth: true
      Layout.fillHeight: true
      //      height:
      color: "transparent"
      radius: 10
    }

    //  }
  }
  Dialogs13.FileDialog {
    id: newImageSectionFileDialog
    title: "Choisir une image à importer"
    folder: shortcuts.pictures
    nameFilters: ["fichiers Images (*.jpg *.png *.bmp *.ppm, *.pdf)"]
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

  DialogOperation {
    id: dialogAddAddition
    title: "Entrer l'addition,  ex: 234+6"
    classType: "AdditionSection"
  }

  DialogOperation {
    id: dialogAddSoustraction
    title: "Entrer la soustraction,  ex: 234-6"
    classType: "SoustractionSection"
  }

  DialogOperation {
    id: dialogAddMultiplication
    title: "Entrer la multiplication,  ex: 234*6"
    classType: "MultiplicationSection"
  }

  DialogOperation {
    id: dialogAddDivision
    title: "Entrer la division,  ex: 234/6"
    classType: "DivisionSection"
  }

}