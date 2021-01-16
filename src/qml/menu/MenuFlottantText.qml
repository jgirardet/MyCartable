import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12

BaseMenu {
    id: root

    property color red_color
    property color blue_color
    property color green_color
    property color black_color

    Component.onCompleted: {
        red_color = "#D40020";
        blue_color = "#0048BA";
        green_color = "#006A4E";
        black_color = "#363636";
    }

    MenuItem {
        RowLayout {
            anchors.fill: parent
            spacing: 0

            ColorButton {
                color: root.red_color
                style: {
                    "fgColor": color,
                    "underline": false
                }
                menu: root
            }

            ColorButton {
                color: root.blue_color
                style: {
                    "fgColor": color,
                    "underline": false
                }
                menu: root
            }

            ColorButton {
                color: root.green_color
                style: {
                    "fgColor": color,
                    "underline": false
                }
                menu: root
            }

            ColorButton {
                color: root.black_color
                style: {
                    "fgColor": color,
                    "underline": false
                }
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
                color: root.red_color
                style: {
                    "fgColor": color,
                    "underline": true
                }
                menu: root
                text: "S"
            }

            ColorButton {
                color: root.blue_color
                style: {
                    "fgColor": color,
                    "underline": true
                }
                menu: root
                text: "S"
            }

            ColorButton {
                color: root.green_color
                style: {
                    "fgColor": color,
                    "underline": true
                }
                menu: root
                text: "S"
            }

            ColorButton {
                color: root.black_color
                style: {
                    "fgColor": color,
                    "underline": true
                }
                menu: root
                text: "S"
            }

        }

    }
    //  enter: Transition {

}
