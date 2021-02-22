import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12
import "qrc:/qml/actions"
import "qrc:/qml/buttons"

BaseMenu {
    id: root

    property alias fonds: fonds_id
    property alias styleNoUnderline: styleNoUnderline_id
    property alias styleUnderline: styleUnderline_id
    property alias appendColumn: appendColumn_id
    property alias insertColumn: insertColumn_id
    property alias removeColumn: removeColumn_id
    property alias appendRow: appendRow_id
    property alias insertRow: insertRow_id
    property alias removeRow: removeRow_id

    width: 241

    Text {
        Layout.alignment: Qt.AlignHCenter
        Layout.preferredHeight: 40
        text: "couleur d'arrière plan"
    }

    MenuItem {
        RowLayout {
            id: fonds_id

            anchors.fill: parent
            //                Layout.fillHeight: true
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
            id: styleNoUnderline_id

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
            id: styleUnderline_id

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

            TableauButton {
                id: insertColumn_id

                ToolTip.text: "Ajouter une colone"
                menu: root

                action: TableauActions.AddColumn {
                    cell: root.target
                }

            }

            TableauButton {
                id: removeColumn_id

                ToolTip.text: "Supprimer une colonne"
                menu: root

                action: TableauActions.RemoveColumn {
                    cell: root.target
                }

            }

            TableauButton {
                id: appendColumn_id

                ToolTip.text: "Ajouter une colonne à la fin"
                menu: root

                action: TableauActions.AppendColumn {
                    cell: root.target
                }

            }

            TableauButton {
                id: insertRow_id

                ToolTip.text: "Ajouter une ligne"
                menu: root

                action: TableauActions.AddRow {
                    cell: root.target
                }

            }

            TableauButton {
                id: removeRow_id

                ToolTip.text: "Supprimer une ligne"
                menu: root

                action: TableauActions.RemoveRow {
                    cell: root.target
                }

            }

            TableauButton {
                id: appendRow_id

                ToolTip.text: "Ajouter une ligne à la fin"
                menu: root

                action: TableauActions.AppendRow {
                    cell: root.target
                }

            }

        }

    }

}
