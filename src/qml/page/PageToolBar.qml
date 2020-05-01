import QtQuick 2.14
import QtQuick.Controls 2.14
//import QtQuick.Controls 1.4 as Controls1
import QtQuick.Layouts 1.14
import QtQuick.Dialogs 1.3 as Dialogs13

ToolBar {
  id: root
  background: Rectangle {
    //    radius: 10
    color: ddb.colorPageToolBar
  }
  visible: ddb.currentPage

  RowLayout {
    anchors.fill: parent
    spacing: 0
    id: rowLayout

    ToolBar {
      RowLayout {
        spacing: 0
        PageToolBarToolButton {
          id: newImageSection
          icon.source: "qrc:///icons/newImageSection"
          onClicked: newImageSectionFileDialog.open()
          ToolTip.text: "Ajouter une image"
        }

        PageToolBarToolButton {
          id: newTextSection
          icon.source: "qrc:///icons/newTextSection"
          onClicked: ddb.addSection(ddb.currentPage, {
            "classtype": "TextSection"
          })
          ToolTip.text: "Ajouter du texte"
        }

        PageToolBarToolButton {
          id: newTableauSection
          icon.source: "qrc:///icons/newTableauSection"
          onClicked: dialogNewTableau.open()
          //          onClicked: ddb.addSection(ddb.currentPage, {
          //            "classtype": "TextSection"
          //          })
          ToolTip.text: "Ajouter un tableau"
        }

        PageToolBarToolButton {
          id: removePage
          icon.source: "qrc:///icons/removePage"
          onClicked: dialogRemovePage.open()
          ToolTip.text: "Supprimer la page"
        }
      }
    }

    ToolBar {
      //  TODO:    visible: ddb.currentMatiere == 1
      RowLayout {
        spacing: 0
        PageToolBarToolButton {
          id: addAddition
          icon.source: "qrc:///icons/addAddition"
          onClicked: dialogAddAddition.open()
          ToolTip.text: "Ajouter une addition"
        }
        PageToolBarToolButton {
          id: addSoustraction
          icon.source: "qrc:///icons/addSoustraction"
          onClicked: dialogAddSoustraction.open()
          ToolTip.text: "Ajouter une soustraction"
        }
        PageToolBarToolButton {
          id: addMultiplication
          icon.source: "qrc:///icons/addMultiplication"
          onClicked: dialogAddMultiplication.open()
          ToolTip.text: "Ajouter une multiplication"
        }
        PageToolBarToolButton {
          id: addDivision
          icon.source: "qrc:///icons/addDivision"
          onClicked: dialogAddDivision.open()
          ToolTip.text: "Ajouter une division"
        }
      }
    }

    Item {
      Layout.fillWidth: true
      Layout.fillHeight: true
    }

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
    id: dialogNewTableau
    title: "Ajouter un tableau"
    contentItem: Column {
      Text {
        id: textColumn
        text: "nombre de colonnes : " + colonneSlider.value
      }
      Slider {
        id: colonneSlider
        wheelEnabled: true
        stepSize: 1
        to: 20
        from: 1
        value: 1

      }
      Text {
        id: textLignes
        text: "nombre de lignes: " + lignesSlider.value
      }
      Slider {
        id: lignesSlider
        wheelEnabled: true
        stepSize: 1
        to: 20
        from: 1
        value: 1

      }
    }

    standardButtons: Dialog.Ok | Dialog.Cancel
    onAccepted: ddb.addSection(ddb.currentPage, {
      'lignes': ~~lignesSlider.value,
      'colonnes': ~~colonneSlider.value,
      "classtype": "TableauSection"
    })
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