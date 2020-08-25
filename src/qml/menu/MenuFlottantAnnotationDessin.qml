import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.12

BaseMenu {
    id: root

    MenuItem {
        height: 20

        Text {
            text: "Changer la couleur du contour"
            anchors.centerIn: parent
        }

    }

    MenuItem {
        RowLayout {
            property string newTool: root.target ? setRemplissageTool() : ""

            function setRemplissageTool() {
                var tool = root.target.item.tool;
                if (tool == "fillrect")
                    return "rect";
                else if (tool == "fillellipse")
                    return "ellipse";

                return tool;
            }

            anchors.fill: parent
            spacing: 0

            ColorButton {
                color: "red"
                style: {
                    "fgColor": color
                }
                menu: root
            }

            ColorButton {
                color: "blue"
                style: {
                    "fgColor": color
                }
                menu: root
            }

            ColorButton {
                color: "lime"
                style: {
                    "fgColor": color
                }
                menu: root
            }

            ColorButton {
                color: "black"
                style: {
                    "fgColor": color
                }
                menu: root
            }

        }

    }

    MenuItem {
        id: titreremplissage

        Text {
            text: "Remplir avec  la couleur"
            anchors.centerIn: parent
        }

    }

    MenuItem {
        RowLayout {
            property string newTool: root.target ? setRemplissageTool() : ""

            function setRemplissageTool() {
                var tool = root.target.item.tool;
                if (tool == "rect")
                    return "fillrect";
                else if (tool == "ellipse")
                    return "fillellipse";

                return tool;
            }

            anchors.fill: parent
            spacing: 0

            ColorButton {
                color: "red"
                style: {
                    "bgColor": color
                }
                menu: root
            }

            ColorButton {
                color: "blue"
                style: {
                    "bgColor": color
                }
                menu: root
            }

            ColorButton {
                color: "lime"
                style: {
                    "bgColor": color
                }
                menu: root
            }

            ColorButton {
                color: "black"
                style: {
                    "bgColor": color
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
        PointSizeSlider {
            menu: root
        }

    }

    MenuItem {
        OpacitySlider {
            menu: root
        }

    }

}
