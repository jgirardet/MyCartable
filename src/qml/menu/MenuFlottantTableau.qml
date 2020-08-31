import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12
import "qrc:/qml/actions"

BaseMenu {
    id: root

    width: 241

    MenuItem {
        ColumnLayout {
            anchors.fill: parent

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "couleur d'arrière plan"
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 0

                ColorButton {
                    color: Qt.lighter("red")
                    style: {
                        "bgColor": color
                    }
                    shortcut: "Ctrl+r"
                    menu: root
                }

                ColorButton {
                    color: Qt.lighter("blue")
                    style: {
                        "bgColor": color
                    }
                    shortcut: "Ctrl+b"
                    menu: root
                }

                ColorButton {
                    color: Qt.lighter("green")
                    style: {
                        "bgColor": color
                    }
                    shortcut: "Ctrl+g"
                    menu: root
                }

                ColorButton {
                    color: Qt.lighter("grey")
                    style: {
                        "bgColor": color
                    }
                    shortcut: "Ctrl+n"
                    menu: root
                }

            }

        }

    }

    MenuSeparator {

        contentItem: Rectangle {
            implicitWidth: 200
            implicitHeight: 1
            color: "#21be2b"
        }

    }

    Text {
        Layout.alignment: Qt.AlignHCenter
        text: "couleur du texte"
    }

    MenuItem {
        RowLayout {
            anchors.fill: parent
            spacing: 0

            ColorButton {
                color: "red"
                style: {
                    "fgColor": color,
                    "underline": false
                }
                shortcut: "Ctrl+r"
                menu: root
            }

            ColorButton {
                color: "blue"
                style: {
                    "fgColor": color,
                    "underline": false
                }
                shortcut: "Ctrl+b"
                menu: root
            }

            ColorButton {
                color: "green"
                style: {
                    "fgColor": color,
                    "underline": false
                }
                shortcut: "Ctrl+g"
                menu: root
            }

            ColorButton {
                color: "black"
                style: {
                    "fgColor": color,
                    "underline": false
                }
                shortcut: "Ctrl+n"
                menu: root
            }

        }

    }

    MenuSeparator {

        contentItem: Rectangle {
            implicitWidth: 200
            implicitHeight: 1
            color: "#21be2b"
        }

    }

    MenuItem {
        RowLayout {
            anchors.fill: parent
            spacing: 0

            ColorButton {
                color: "red"
                style: {
                    "fgColor": color,
                    "underline": true
                }
                shortcut: "Alt+r"
                menu: root
                text: "S"
            }

            ColorButton {
                color: "blue"
                style: {
                    "fgColor": color,
                    "underline": true
                }
                shortcut: "Alt+b"
                menu: root
                text: "S"
            }

            ColorButton {
                color: "green"
                style: {
                    "fgColor": color,
                    "underline": true
                }
                shortcut: "Alt+g"
                menu: root
                text: "S"
            }

            ColorButton {
                color: "black"
                style: {
                    "fgColor": color,
                    "underline": true
                }
                shortcut: "Alt+n"
                menu: root
                text: "S"
            }

        }

    }

    MenuSeparator {

        contentItem: Rectangle {
            implicitWidth: 200
            implicitHeight: 1
            color: "#21be2b"
        }

    }

    MenuItem {
        id: manipulation

        RowLayout {
            spacing: 0
            anchors.fill: parent

            ToolButton {
                icon.color: "transparent"
                ToolTip.visible: hovered
                ToolTip.text: "Ajouter une colone"

                action: TableauActions.AddColumn {
                    cell: root.target
                }

            }

            ToolButton {
                icon.color: "transparent"
                ToolTip.visible: hovered
                ToolTip.text: "Supprimer une colonne"

                action: TableauActions.RemoveColumn {
                    cell: root.target
                }

            }

            ToolButton {
                icon.color: "transparent"
                ToolTip.visible: hovered
                ToolTip.text: "Ajouter une colonne à la fin"

                action: TableauActions.AppendColumn {
                    cell: root.target
                }

            }

            ToolButton {
                icon.color: "transparent"
                ToolTip.visible: hovered
                ToolTip.text: "Ajouter une ligne"

                action: TableauActions.AddRow {
                    cell: root.target
                }

            }

            ToolButton {
                icon.color: "transparent"
                ToolTip.visible: hovered
                ToolTip.text: "Supprimer une ligne"

                action: TableauActions.RemoveRow {
                    cell: root.target
                }

            }

            ToolButton {
                icon.color: "transparent"
                ToolTip.visible: hovered
                ToolTip.text: "Ajouter une ligne à la fin"

                action: TableauActions.AppendRow {
                    cell: root.target
                }

            }

        }

    }

}
