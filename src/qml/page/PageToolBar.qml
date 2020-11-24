import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "qrc:/qml/buttons" as Buttons
import "qrc:/qml/layouts"

ToolBar {
    id: root

    property QtObject page

    visible: true

    RowLayout {
        id: rowLayout

        anchors.fill: parent
        spacing: 0

        ToolBar {
            RowLayout {
                spacing: 0

                Buttons.NewTextSection {
                    appendMode: true
                    page: root.page
                }

                Buttons.NewImageSection {
                    appendMode: true
                    page: root.page
                }

                Buttons.NewImageSectionVide {
                    appendMode: true
                    page: root.page
                }

                Buttons.NewEquationSection {
                    appendMode: true
                    page: root.page
                }

                Buttons.NewOperationSection {
                    appendMode: true
                    page: root.page
                }

                Buttons.NewTableauSection {
                    appendMode: true
                    page: root.page
                }

                Buttons.NewFriseSection {
                    appendMode: true
                    page: root.page
                }

                Buttons.RemovePage {
                    page: root.page
                }

                Buttons.ExportOdt {
                    page: root.page
                }

                Buttons.ExportPdf {
                    page: root.page
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
