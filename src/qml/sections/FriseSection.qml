import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3
import QtQuick.Shapes 1.15
import "qrc:/qml/frise"

Rectangle {
    id: root

    //    property alias listmodel: listmodel
    property alias corps: corps
    property string sectionId
    property var sectionItem
    property QtObject model
    property alias titre: titre

    //    property alias repeater: repeater
    //    model:
    //    Rectangle {
    //        anchors.fill: parent
    //        border.width: 1
    //    }
    width: sectionItem.width
    height: model ? model.height : 0
    color: "white"

    TextEdit {
        id: titre

        text: root.model ? root.model.titre : ""
        font.pointSize: 16
        anchors.horizontalCenter: parent.horizontalCenter
        Component.onCompleted: {
            onTextChanged.connect(() => {
                return root.model.titre = text;
            });
        }
    }

    CorpsFrise {
        id: corps

        model: root.model
        height: 100

        anchors {
            left: root.left
            right: root.right
            top: root.top
            //            bottom: root.bottom
            topMargin: root.height / 2 - height / 2
            //            bottomMargin: 150
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
        sectionId: dao ? root.sectionId : ""
        dao: ddb
    }

}
