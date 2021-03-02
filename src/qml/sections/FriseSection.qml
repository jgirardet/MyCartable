import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15
import "qrc:/qml/divers"
import "qrc:/qml/frise"

Rectangle {
    id: root

    property alias corps: corps_id
    property alias titre: titre
    required property var sectionItem
    required property QtObject section
    property var model: section.model

    width: sectionItem.width
    height: section ? section.height : 0
    color: "white"

    UndoAbleTextArea {
        id: titre

        function setText() {
            root.section.set({
                "titre": titre.text
            }, "modifier titre frise");
        }

        txtfield: section.titre
        undostack: section.undoStack
        font.pointSize: 16
        anchors.horizontalCenter: parent.horizontalCenter
    }

    CorpsFrise {
        id: corps_id

        model: root.model
        height: 100
        section: root.section

        anchors {
            left: root.left
            right: root.right
            top: root.top
            topMargin: root.height / 2 - height / 2
            leftMargin: 30
            rightMargin: 50
        }

    }

    Shape {
        id: fleche

        z: 0
        anchors.left: corps_id.right
        anchors.top: corps_id.top
        anchors.topMargin: -10
        height: corps_id.height + 20
        width: 30

        ShapePath {
            strokeWidth: 4
            strokeColor: "black"
            strokeStyle: ShapePath.SolidLine
            startX: 0
            startY: 0

            PathLine {
                x: fleche.width
                y: fleche.height / 2
            }

            PathLine {
                x: 0
                y: fleche.height
            }

        }

    }

}
