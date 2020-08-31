import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "qrc:/qml/actions"

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

                Buttons.NewTextSection {
                }

                Buttons.NewImageSection {
                }

                Buttons.NewEquationSection {
                }

                Buttons.NewOperationSection {
                }

                Buttons.NewTableauSection {
                }

                Buttons.RemovePage {
                }

                Buttons.ExportOdt {
                }

                Buttons.ExportPdf {
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
