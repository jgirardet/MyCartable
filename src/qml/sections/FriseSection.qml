import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3
import QtQuick.Shapes 1.15
import "qrc:/qml/frise"

Rectangle {
    id: root

    property alias corps: corps
    property alias titre: titre
    property string sectionId
    property var sectionItem
    property QtObject model

    width: sectionItem.width
    height: model ? model.height : 0
    color: "white"

    TextEdit {
        id: titre

        onTextChanged: {
            return root.model.titre = titre.text;
        }
        font.pointSize: 16
        anchors.horizontalCenter: parent.horizontalCenter
    }

    CorpsFrise {
        id: corps

        model: root.model
        height: 100

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
        anchors.left: corps.right
        anchors.top: corps.top
        anchors.topMargin: -10
        height: corps.height + 20
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

    model: FriseModel {
        dao: ddb
        dtb: c_dtb
        Component.onCompleted: {
            sectionId = root.sectionId;
            root.titre.text = model.titre;
        }
    }

}
