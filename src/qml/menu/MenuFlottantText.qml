import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.12

BaseMenu {
    //    onRunningChanged: print("go")
    //    NumberAnimation {
    //      property: "opacity";from: 0.0;to: 1.0;duration: 500
    //    }
    //  }

    id: root

    property color red_color
    property color blue_color
    property color green_color
    property color black_color

    Component.onCompleted: {
        red_color = ddb.getTextSectionColor("red");
        blue_color = ddb.getTextSectionColor("blue");
        green_color = ddb.getTextSectionColor("green");
        black_color = ddb.getTextSectionColor("black");
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
