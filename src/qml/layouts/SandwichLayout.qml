/*
  Composant avec 2 parties latérales qui se cachent en fonction de la taille du composant.
  La partie centrale est toujours affichée
*/

import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: sandwich

    property Item hamAndCheese
    property alias leftBread: left_bread.contentItem // left side
    property alias rightBread: right_bread.contentItem // right side
    property int widthLimit: 1000 // au delà cette largeur on passe en mode Big
    property alias leftWidthBig: left_bread.widthBig
    property alias rightWidthBig: right_bread.widthBig
    property alias leftWidthSmall: left_bread.widthSmall
    property alias rightWidthSmall: right_bread.widthSmall
    property alias leftDuration: left_bread.animDuration
    property alias rightDuration: right_bread.animDuration
    readonly property bool expectBig: width > widthLimit // mode Big if true
    property string breadsState
    property alias centerControl: centercontrol

    state: expectBig ? "bigsandwich" : "smallsandwich"
    states: [
        State {
            name: "bigsandwich"

            AnchorChanges {
                target: left_bread
                anchors.left: undefined
                anchors.right: centercontrol.contentItem.left
            }

            AnchorChanges {
                target: right_bread
                anchors.left: centercontrol.contentItem.right
                anchors.right: undefined
            }

            PropertyChanges {
                target: centercontrol
                anchors.leftMargin: left_bread.width
                anchors.rightMargin: right_bread.width
            }

            PropertyChanges {
                target: sandwich
                breadsState: "big"
            }

        },
        State {
            name: "smallsandwich"

            PropertyChanges {
                target: centercontrol
                leftPadding: leftWidthSmall
                rightPadding: rightWidthSmall
            }

            AnchorChanges {
                target: left_bread
                anchors.right: undefined
                anchors.left: centercontrol.left
            }

            AnchorChanges {
                target: right_bread
                anchors.left: undefined
                anchors.right: centercontrol.right
            }

            PropertyChanges {
                target: sandwich
                breadsState: "small"
            }

        }
    ]

    Control {
        id: centercontrol

        objectName: "centercontrol"
        anchors.fill: parent
        contentItem: hamAndCheese

        Bread {
            id: left_bread

            sandwich: sandwich
        }

        Bread {
            id: right_bread

            objectName: "right"
            sandwich: sandwich
        }

    }

}
