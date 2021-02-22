import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12
import "qrc:/qml/buttons" as Buttons

BaseMenu {
    id: menu

    property alias rotateLeft: rotateLeft_id
    property alias rotateRight: rotateRight_id

    closePolicy: Popup.NoAutoClose

    MenuItem {
        Row {
            ToolButton {
                id: rotateLeft_id

                icon.source: "qrc:///icons/rotateLeft"
                icon.color: "blue"
                onClicked: target.section.pivoterImage(0)
                ToolTip.text: "Pivoter à  gauche"
            }

            ToolButton {
                id: rotateRight_id

                icon.source: "qrc:///icons/rotateRight"
                icon.color: "blue"
                onClicked: target.section.pivoterImage(1)
                ToolTip.text: "Pivoter à droite"
            }

        }

    }

    MenuItem {
        height: 80

        ColumnLayout {
            RowLayout {
                spacing: 0

                ColorButton {
                    color: "transparent"
                    style: {
                        "tool": "text"
                    }
                    icon.source: "qrc:///icons/abcd"
                    icon.color: "transparent"
                    menu: menu
                }

                ColorButton {
                    color: "transparent"
                    style: {
                        "tool": "trait"
                    }
                    icon.source: "qrc:///icons/trait"
                    icon.color: "transparent"
                    menu: menu
                }

                ColorButton {
                    color: "transparent"
                    style: {
                        "tool": "rect"
                    }
                    icon.source: "qrc:///icons/rect"
                    icon.color: "transparent"
                    menu: menu
                }

                ColorButton {
                    color: "transparent"
                    style: {
                        "tool": "fillrect"
                    }
                    icon.source: "qrc:///icons/fillrect"
                    icon.color: "transparent"
                    menu: menu
                }

            }

            RowLayout {
                spacing: 0

                ColorButton {
                    color: "transparent"
                    style: {
                        "tool": "ellipse"
                    }
                    icon.source: "qrc:///icons/ellipse"
                    icon.color: "transparent"
                    menu: menu
                }

                ColorButton {
                    color: "transparent"
                    style: {
                        "tool": "arrow"
                    }
                    icon.source: "qrc:///icons/arrow-right"
                    icon.color: "transparent"
                    menu: menu
                }

                ColorButton {
                    color: "transparent"
                    style: {
                        "tool": "point"
                    }
                    icon.source: "qrc:///icons/newTextSection"
                    icon.color: "transparent"
                    menu: menu
                }

                ColorButton {
                    color: "transparent"
                    style: {
                        "tool": "floodfill"
                    }
                    icon.source: "qrc:///icons/floodfill"
                    icon.color: "transparent"
                    menu: menu
                }

            }

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
                    "bgColor": color
                }
                menu: menu
            }

            ColorButton {
                color: "blue"
                style: {
                    "fgColor": color,
                    "bgColor": color
                }
                menu: menu
            }

            ColorButton {
                color: "lime"
                style: {
                    "fgColor": color,
                    "bgColor": color
                }
                menu: menu
            }

            ColorButton {
                color: "black"
                style: {
                    "fgColor": color,
                    "bgColor": color
                }
                menu: menu
            }

        }

    }

    MenuItem {
        PointSizeSlider {
            menu: menu
            pointSize: target ? target.section.annotationDessinCurrentLineWidth : 5
        }

    }

}
