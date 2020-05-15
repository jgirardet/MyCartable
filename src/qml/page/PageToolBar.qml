import QtQuick 2.14
import QtQuick.Controls 2.14
//import QtQuick.Controls 1.4 as Controls1
import QtQuick.Layouts 1.14
import QtQuick.Dialogs 1.3 as Dialogs13
import "../toolbuttons"

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
        NewTextSectionButton {
          targetIndex: ddb.currentPage ? ddb.pageModel.count : 0
        }
        NewImageSectionButton {
          targetIndex: ddb.currentPage ? ddb.pageModel.count : 0
        }
        NewEquationSectionButton {
          targetIndex: ddb.currentPage ? ddb.pageModel.count : 0
        }
        NewOperationSectionButton {
          targetIndex: ddb.currentPage ? ddb.pageModel.count : 0
        }
        NewTableauSectionButton {
          targetIndex: ddb.currentPage ? ddb.pageModel.count : 0
        }
        //        PageToolBarToolButton {
        //          id: newImageSection
        //          icon.source: "qrc:///icons/newImageSection"
        //          onClicked: newImageSectionFileDialog.open()
        //          ToolTip.text: "Ajouter une image"
        //        }

        //        PageToolBarToolButton {
        //          id: newTableauSection
        //          icon.source: "qrc:///icons/newTableauSection"
        //          onClicked: dialogNewTableau.open()
        //          //          onClicked: ddb.addSection(ddb.currentPage, {
        //          //            "classtype": "TextSection"
        //          //          })
        //          ToolTip.text: "Ajouter un tableau"
        //        }

        //        PageToolBarToolButton {
        //          id: removePage
        //          icon.source: "qrc:///icons/removePage"
        //          onClicked: dialogRemovePage.open()
        //          ToolTip.text: "Supprimer la page"
        //        }
      }
    }

    ToolBar {
      RowLayout {
        spacing: 0

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
    id: dialogRemovePage
    title: "Supprimer la page ?"
    standardButtons: Dialog.Ok | Dialog.Cancel
    onAccepted: ddb.removePage(ddb.currentPage)
  }

}