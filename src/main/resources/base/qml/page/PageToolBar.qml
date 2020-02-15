import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.14
import QtQuick.Dialogs 1.3
//import Qt.labs.platform 1.1
//
//ToolBar {
//  id: root
//  RowLayout{
//    ToolButton {
//      id: newImageSection
//      iconSource: "qrc:///icons/newImageSection"
//      onClicked: newImageSectionFileDialog.open()
//    }
//  }
//
////FileDialog {
////    id: newImageSectionFileDialog
////    fileMode: FileDialog.OpenFile
////    folder: StandardPaths.writableLocation(StandardPaths.MoviesLocation)
////    onVisibleChanged: print(StandardPaths.writableLocation(StandardPaths.MoviesLocation))
////}
////}
////}
ToolBar {
  id: root
  ToolButton {
    id: newImageSection
    iconSource: "qrc:///icons/newImageSection"
    onClicked: newImageSectionFileDialog.open()
  }



  FileDialog {
    id: newImageSectionFileDialog
    title: "Choisir une image à importer"
    folder: shortcuts.pictures
    nameFilters: [ "fichiers Images (*.jpg *.png *.bmp)"]
    onAccepted: {
        ddb.addSection(ddb.currentPage, {'path':fileUrl, "classtype":"ImageSection"})

    }
    }
}