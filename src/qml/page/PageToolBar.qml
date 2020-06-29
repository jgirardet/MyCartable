import "../toolbuttons"
import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Dialogs 1.3 as Dialogs13
//import QtQuick.Controls 1.4 as Controls1
import QtQuick.Layouts 1.14

ToolBar {
    id: root

    visible: ddb.currentPage

    RowLayout {
        id: rowLayout

        anchors.fill: parent
        spacing: 0

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

                RemovePageButton {
                    targetIndex: ddb.currentPage ? ddb.pageModel.count : 0
                }

                ExportOdtButton {
                    //          targetIndex: ddb.currentPage ? ddb.pageModel.count : 0

                }

                ExportPdfButton {
                    //          targetIndex: ddb.currentPage ? ddb.pageModel.count : 0

                }

            }

        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }

    }

    background: Rectangle {
        //    radius: 10
        color: ddb.colorPageToolBar
    }

}
