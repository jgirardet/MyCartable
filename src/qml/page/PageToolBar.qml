import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "qrc:/qml/buttons" as Buttons
import "qrc:/qml/layouts"

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
                    appendMode: true
                }

                Buttons.NewImageSection {
                    appendMode: true
                }

                Buttons.NewImageSectionVide {
                    appendMode: true
                }

                Buttons.NewEquationSection {
                    appendMode: true
                }

                Buttons.NewOperationSection {
                    appendMode: true
                }

                Buttons.NewTableauSection {
                    appendMode: true
                }

                Buttons.NewFriseSection {
                    appendMode: true
                }

                Buttons.RemovePage {
                }

                Buttons.ExportOdt {
                }

                Buttons.ExportPdf {
                }

            }

        }

        SplitSwitch {
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
